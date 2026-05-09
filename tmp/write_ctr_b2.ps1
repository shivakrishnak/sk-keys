# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\write_ctr_b2.ps1
Set-Location "C:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-6-infrastructure-devops\CTR-containers"

# ── CTR-047 ──────────────────────────────────────────────────────────────
$ctr047 = @'
---
id: CTR-047
title: "Multi-Runtime Container Strategy (containerd, CRI-O)"
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-025, CTR-042, CTR-043
used_by:
related: CTR-048, CTR-025
tags:
  - containers
  - architecture
  - advanced
  - deep-dive
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /ctr/multi-runtime-container-strategy-containerd-cri-o/
---

# CTR-047 - Multi-Runtime Container Strategy (containerd, CRI-O)

⚡ TL;DR - Multi-runtime container strategy is the deliberate choice between containerd and CRI-O as the Kubernetes container runtime, and optionally mixing runtimes within a cluster for different workload security or performance profiles.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-025, CTR-042, CTR-043 |     |
| **Used by:**    |                          |     |
| **Related:**    | CTR-048, CTR-025         |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An organisation's Kubernetes cluster uses dockershim (Docker as the
container runtime via an adapter shim). Kubernetes 1.24 removes
dockershim. The team must migrate to a CRI-compatible runtime - but
they have never evaluated containerd vs. CRI-O, do not understand the
difference, and must migrate a production cluster under time pressure.

**THE BREAKING POINT:**
A security team requires that GPU workloads run in a sandboxed runtime
(gVisor or Kata Containers) for tenant isolation, while standard
workloads run in containerd for performance. The team has no mechanism
to assign different runtimes to different workloads within the same
cluster. Every workload runs in the same runtime with the same trust
level.

**THE INVENTION MOMENT:**
The Container Runtime Interface (CRI) standardised how Kubernetes talks
to container runtimes. This enables: (1) runtime choice at cluster
creation (containerd or CRI-O), and (2) runtime mixing within a cluster
via RuntimeClass - different pods can use different runtimes (containerd,
gVisor, Kata) based on workload security requirements.

**EVOLUTION:**
2016: CRI introduced. dockershim bridges Docker to CRI. 2018: containerd
1.0 released as a standalone CRI runtime. CRI-O 1.0 released as a
Kubernetes-specific CRI runtime. 2022: dockershim removed from Kubernetes
1.24. All clusters must use CRI-compatible runtimes. 2023: RuntimeClass
matures - multi-runtime clusters (containerd + gVisor) become production
standard for multi-tenant and regulated workloads.

---

### 📘 Textbook Definition

**Multi-runtime container strategy** is the selection and governance of
one or more CRI-compatible container runtimes within a Kubernetes cluster.
The primary choice is containerd vs. CRI-O as the default runtime. An
advanced strategy uses Kubernetes RuntimeClass to assign different runtimes
(including sandboxed runtimes like gVisor or Kata Containers) to different
workloads within the same cluster based on security or performance
requirements.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Choose containerd or CRI-O as your default runtime; use RuntimeClass
to assign sandboxed runtimes to workloads that need stronger isolation.

**One analogy:**

> Container runtimes are like engine types in a vehicle fleet. Most
> vehicles use a standard engine (containerd). Specialised vehicles
> (armoured trucks = regulated workloads) use a reinforced engine (gVisor
> or Kata). The fleet manager (Kubernetes RuntimeClass) assigns the right
> engine type to each vehicle type.

**One insight:**
For most clusters, the containerd vs. CRI-O choice is a minor operational
preference. The strategically important decision is: do any workloads
require sandbox-level isolation? If yes, RuntimeClass with gVisor or
Kata Containers is required; the base runtime choice becomes secondary.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **All CRI-compatible runtimes implement the same CRI API** - from
   Kubernetes' perspective, containerd and CRI-O are interchangeable.
   The choice affects operational tooling, not scheduling behaviour.
2. **RuntimeClass enables per-workload runtime selection** - a pod can
   specify `runtimeClassName: gvisor` to run in a sandboxed runtime
   while other pods use the default containerd runtime.
3. **Sandboxed runtimes trade performance for isolation** - gVisor
   intercepts syscalls in user space (overhead per syscall); Kata runs
   a full VM per pod (startup latency). Both reduce kernel attack surface.
4. **Runtime choice is a node-level configuration** - changing the
   runtime requires node reprovisioning (or node pools in managed K8s).
   It is not a live change.

**DERIVED DESIGN:**
Given invariant 2: use RuntimeClass to enforce sandbox runtimes for
multi-tenant and regulated workloads. Given invariant 4: plan runtime
changes as part of cluster lifecycle management, not as live operations.

**THE TRADE-OFFS:**
**Gain:** RuntimeClass enables fine-grained isolation: standard workloads
run efficiently in containerd; high-risk workloads run in gVisor with
additional kernel protection.
**Cost:** Multi-runtime clusters require multiple node pools (one per
runtime), increasing cluster complexity and cost.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any cluster needs a CRI runtime. Regulated workloads
genuinely need additional kernel isolation.
**Accidental:** Running three different runtimes in a cluster where
all workloads have the same trust level. Complexity without benefit.

---

### 🧪 Thought Experiment

**SETUP:**
A SaaS platform runs untrusted customer code (user-submitted functions
or scripts) in containers alongside trusted internal microservices.
All containers run in the same containerd runtime on shared nodes.

**WHAT HAPPENS WITHOUT MULTI-RUNTIME STRATEGY:**
A sophisticated user exploits a kernel vulnerability. Because the
container runtime shares the host kernel (standard containerd isolation),
the attacker gains host access. From the host, the attacker can read
the memory of other tenants' containers and access their data. The
shared-kernel model means one tenant's exploit affects all tenants.

**WHAT HAPPENS WITH MULTI-RUNTIME STRATEGY:**
Untrusted customer code workloads are assigned `runtimeClassName: gvisor`
via RuntimeClass. gVisor interposes on all syscalls in user space,
preventing direct kernel access. A kernel exploit inside the gVisor
sandbox reaches gVisor's user-space kernel, not the host kernel. The
blast radius is limited to the exploited container; other tenants are
unaffected.

**THE INSIGHT:**
The multi-runtime strategy exists specifically for the shared-kernel
problem. When tenant isolation requires stronger guarantees than standard
namespaces provide, a sandboxed runtime (gVisor, Kata) adds a kernel
isolation boundary. This is not general-purpose hardening - it is a
specific solution to the multi-tenant kernel sharing problem.

---

### 🧠 Mental Model / Analogy

> Think of container runtimes as process execution environments. Standard
> containerd is a shared-kernel model: all processes talk to the same
> OS kernel (efficient, low overhead). gVisor is a user-space kernel:
> processes talk to a user-space kernel emulator that translates to
> the host kernel (isolates the syscall interface). Kata Containers is
> a lightweight VM: each pod gets its own kernel in a hardware VM (maximum
> isolation, higher overhead).

Element mapping:

- **Shared-kernel** = containerd, CRI-O (standard isolation)
- **User-space kernel** = gVisor (syscall interposition)
- **Lightweight VM** = Kata Containers (full VM per pod)
- **RuntimeClass** = the dispatcher that assigns execution environment

Where this analogy breaks down: in software, the isolation boundaries
are not perfectly clean - gVisor does not emulate all syscalls perfectly
and some applications fail to run under it.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A container runtime is the software that actually starts and runs
containers. Kubernetes can use different runtimes, and you can choose
which one based on how isolated you need your containers to be.

**Level 2 - How to use it (junior developer):**
For most clusters: use containerd (the default in EKS, GKE, AKS).
If running untrusted code or multi-tenant workloads, add a gVisor node
pool and use RuntimeClass to assign those workloads to it. CRI-O is
a valid alternative to containerd with no meaningful functional difference
for standard use cases.

**Level 3 - How it works (mid-level engineer):**
containerd manages the full container lifecycle: image pull, snapshot
management, container creation, and process execution via runc. CRI-O
does the same but is designed exclusively for Kubernetes and has a
smaller footprint. RuntimeClass allows a pod to request a non-default
runtime: `runtimeClassName: gvisor` causes the Kubernetes scheduler
to place the pod on a node with gVisor installed, and the CRI runtime
dispatches the pod to gVisor instead of runc.

**Level 4 - Why it was designed this way (senior/staff):**
The CRI was designed to decouple Kubernetes from Docker's implementation.
Before CRI, Docker was the only runtime option. CRI enabled a plugin
model: any runtime implementing the CRI gRPC API can be used. RuntimeClass
extends this by making runtime selection a pod-level declaration rather
than a cluster-level setting. This enables the "default secure" pattern:
most workloads run in the standard runtime; specific workloads with
elevated risk are automatically routed to sandboxed runtimes via
admission webhooks that enforce RuntimeClass assignment.

**Expert Thinking Cues:**

- "Do any workloads run untrusted or user-submitted code? If yes,
  sandboxed runtime is a security requirement, not an option."
- "Does the team have operational knowledge of gVisor or Kata? A runtime
  that produces unexplained failures under load is worse than standard
  containerd well understood."
- "What is the performance overhead of gVisor for our workload profile?
  syscall-heavy workloads (databases, I/O-intensive) may be unsuitable."

---

### ⚙️ How It Works (Mechanism)

**CRI RUNTIME CALL PATH:**

```
Kubernetes Kubelet
  |
  | gRPC (CRI API)
  v
containerd / CRI-O  (high-level runtime)
  |
  | OCI Runtime Spec
  v
runc / gVisor / Kata  (low-level runtime)
  |
  v
Linux kernel (or gVisor user-space kernel)
```

**RUNTIMECLASS DISPATCH:**

```yaml
# Node pool has gVisor installed
# RuntimeClass maps name to handler
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc   # gVisor's OCI runtime binary

---
# Pod requests the sandboxed runtime
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: gvisor
  containers:
  - name: untrusted-code
    image: user-function:latest
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Pod scheduling request
  |
  v
Scheduler: find node matching RuntimeClass
  |         ← YOU ARE HERE
  v
Kubelet on selected node
  |
  v
CRI call to containerd/CRI-O
  |
  v
containerd routes to handler:
  - default: runc (standard)
  - gvisor: runsc (sandboxed)
  - kata: kata-runtime (VM)
  |
  v
Container process started with
selected isolation level
```

**FAILURE PATH:**
Pod requests `runtimeClassName: gvisor` but no nodes in the cluster
have gVisor installed. Pod stays in `Pending` state indefinitely with
`RuntimeClass "gvisor" not found` error. Without monitoring for stuck
Pending pods, the failure is invisible.

**WHAT CHANGES AT SCALE:**
At scale, multi-runtime clusters need multiple node pools (one per
runtime type). The admission webhook enforces RuntimeClass assignment
for specific namespaces or pod labels - preventing untrusted workloads
from running without the required sandbox.

---

### 💻 Code Example

```yaml
# BAD: no RuntimeClass for untrusted code -
# runs in standard containerd with shared kernel
apiVersion: v1
kind: Pod
metadata:
  name: user-function
spec:
  containers:
  - name: user-code
    image: user-function:latest
    # Shares host kernel with all other pods
```

```yaml
# GOOD: RuntimeClass enforces sandboxed runtime
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc

---
apiVersion: v1
kind: Pod
metadata:
  name: user-function
spec:
  runtimeClassName: gvisor   # sandboxed runtime
  containers:
  - name: user-code
    image: user-function:latest
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
```

```yaml
# GOOD: Kyverno policy enforcing RuntimeClass
# for pods in the untrusted namespace
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-gvisor-for-untrusted
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-runtimeclass
    match:
      resources:
        kinds: [Pod]
        namespaces: [untrusted-workloads]
    validate:
      message: "Untrusted workloads must use gvisor RuntimeClass"
      pattern:
        spec:
          runtimeClassName: gvisor
```

**How to test / verify correctness:**

```bash
# Verify gVisor is installed on node
kubectl get nodes -o json | jq '
  .items[] | select(.metadata.labels."sandbox.gke.io/runtime"
  == "gvisor") | .metadata.name'

# Verify pod is running in gVisor
kubectl exec -it user-function -- \
  dmesg | grep -i gvisor

# Performance comparison: syscall overhead
kubectl run perf-runc --image=ubuntu --rm -it \
  -- dd if=/dev/urandom bs=1M count=100 of=/dev/null

kubectl run perf-gvisor --image=ubuntu --rm -it \
  --overrides='{"spec":{"runtimeClassName":"gvisor"}}' \
  -- dd if=/dev/urandom bs=1M count=100 of=/dev/null
```

---

### ⚖️ Comparison Table

| Runtime | Isolation | Overhead | Syscall Support | Best For |
|---|---|---|---|---|
| runc (via containerd) | Namespace + cgroup | Minimal | Full | Trusted workloads |
| gVisor (runsc) | User-space kernel | 10-30% CPU | Partial | Untrusted code, multi-tenant |
| Kata Containers | Hardware VM | 100-200ms startup | Full | Regulated, maximum isolation |
| Firecracker | MicroVM | 125ms startup | Full | Serverless, Lambda-style |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "containerd and CRI-O are fundamentally different" | Both implement the CRI API and use runc as the default low-level runtime. The operational and functional differences are minor. The choice is primarily a team familiarity decision. |
| "gVisor provides the same isolation as a VM" | gVisor intercepts syscalls in user space but still runs on the host kernel. A kernel exploit that bypasses gVisor's syscall filter can still affect the host. Kata Containers provides VM-level isolation. |
| "RuntimeClass requires separate clusters" | RuntimeClass operates within a single cluster using node pools with different runtimes installed. No separate cluster is required. |
| "gVisor is compatible with all applications" | gVisor does not implement all Linux syscalls. Applications that use unimplemented syscalls fail at runtime. Test application compatibility before production deployment on gVisor. |
| "Docker was removed from Kubernetes in 1.24" | Docker as the runtime (via dockershim) was removed. Docker-built images still work - they follow the OCI image format. The change only affects the runtime layer, not image format. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: RuntimeClass Not Found - Pod Stuck Pending**
**Symptom:** Pods with `runtimeClassName` set stay in Pending state
indefinitely. Events show `RuntimeClass "gvisor" not found`.
**Root Cause:** RuntimeClass object not created in the cluster, or node
pool with gVisor not available for scheduling.
**Diagnostic:**

```bash
# Check if RuntimeClass exists
kubectl get runtimeclasses

# Check pod events
kubectl describe pod <pod-name> | grep -A 5 Events

# Check if gVisor nodes are available
kubectl get nodes -l \
  "sandbox.gke.io/runtime=gvisor"
```

**Fix:** Create the RuntimeClass object. Ensure nodes with the required
runtime handler are present and Ready.
**Prevention:** Validate RuntimeClass availability in pre-deployment
CI checks. Alert on Pending pods older than 5 minutes.

---

**Failure Mode 2: gVisor Incompatibility Crash (Security)**
**Symptom:** Application runs correctly in containerd/runc but crashes
with `invalid argument` or `function not implemented` errors when
migrated to gVisor.
**Root Cause:** Application uses a Linux syscall not implemented by
gVisor's user-space kernel (e.g., `io_uring`, `ptrace`, some inotify
variants).
**Diagnostic:**

```bash
# Check gVisor syscall log for unsupported calls
kubectl logs <pod> 2>&1 | grep "Unsupported syscall"

# Run with gVisor debug logging
kubectl run test --image=myapp \
  --overrides='{"spec":{"runtimeClassName":"gvisor"}}' \
  -- sh -c 'runsc --debug=true myapp 2>&1 | grep -i unsupported'
```

**Fix:** Either modify the application to avoid unsupported syscalls,
or use Kata Containers (full VM kernel, full syscall support) instead
of gVisor.
**Prevention:** Run application compatibility tests against gVisor in
CI before production deployment. Maintain a compatibility matrix of
applications vs. runtimes.

---

**Failure Mode 3: Missing Admission Enforcement**
**Symptom:** Security audit finds untrusted workloads running in standard
containerd without gVisor, despite a policy requiring gVisor for the
`untrusted` namespace.
**Root Cause:** Kyverno/OPA policy is in audit mode, not enforce mode.
Developers deployed without the required RuntimeClass.
**Diagnostic:**

```bash
# Check all pods in untrusted namespace for runtimeClassName
kubectl get pods -n untrusted-workloads -o json | jq '
  .items[] |
  {name: .metadata.name,
   runtime: .spec.runtimeClassName}'

# Check Kyverno policy enforcement action
kubectl get clusterpolicy require-gvisor-for-untrusted \
  -o json | jq '.spec.validationFailureAction'
```

**Fix:** Set Kyverno policy to `Enforce`. Delete non-compliant pods.
**Prevention:** Policies for security-critical namespaces must always
be in Enforce mode. Audit mode is a transition state only.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-025 - containerd]] - the default high-level runtime
- [[CTR-042 - Container Runtime Interface (CRI)]] - the API that enables runtime choice
- [[CTR-043 - Container Platform Strategy]] - platform context for runtime decisions

**Builds On This (learn these next):**

- [[CTR-048 - Container Runtime Internals (runc, containerd)]] - how runtimes work inside

**Alternatives / Comparisons:**

- [[CTR-025 - containerd]] - the default runtime choice
- [[CTR-048 - Container Runtime Internals (runc, containerd)]] - runtime internals

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Runtime selection per workload type │
│ PROBLEM     │ Shared kernel = shared blast radius │
│ KEY INSIGHT │ RuntimeClass routes pods to sandbox │
│ USE WHEN    │ Untrusted code, multi-tenant, regs  │
│ AVOID WHEN  │ Single-tenant, trusted workloads    │
│ TRADE-OFF   │ Isolation vs. performance overhead  │
│ ONE-LINER   │ containerd default, gVisor for risk │
│ NEXT EXPLORE│ CTR-048 Runtime Internals           │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. containerd and CRI-O are functionally equivalent; the runtime choice
   matters far less than whether you need sandboxed runtimes.
2. RuntimeClass enables per-pod runtime selection - use gVisor for
   untrusted workloads, containerd for trusted ones, in the same cluster.
3. gVisor is not a VM - it intercepts syscalls but shares the host kernel.
   Kata Containers provides true VM-level isolation at higher overhead.

**Interview one-liner:**
"Multi-runtime strategy uses Kubernetes RuntimeClass to assign sandboxed
runtimes (gVisor for syscall interposition, Kata for VM isolation) to
high-risk workloads while trusted services run in standard containerd -
limiting blast radius when one runtime boundary is breached."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When workloads have different trust levels, they need different isolation
boundaries. Applying the same isolation level to all workloads either
over-provisions security for low-risk workloads (wasting resources) or
under-provisions it for high-risk ones (creating unacceptable exposure).
Right-sized isolation by workload type is the principle.

**Where else this pattern appears:**

- **Database connection pooling:** Separate connection pools for OLTP
  (low latency, small queries) and analytics (long-running, high CPU)
  prevent analytics queries from starving OLTP connections.
- **AWS IAM roles:** Different IAM roles per Lambda function (least
  privilege per workload) rather than one role for all Lambdas. Same
  right-sizing principle applied to permissions.
- **Browser process isolation:** Chrome runs each tab in a separate
  process with different trust levels (site isolation). A compromised
  tab cannot access another tab's memory because they are in different
  processes with different OS-level isolation boundaries.

---

### 💡 The Surprising Truth

gVisor, Google's container sandboxing technology, was developed not for
external cloud customers but for Google's own internal infrastructure -
specifically to safely run untrusted user code (Google Cloud Functions,
Google App Engine) on shared infrastructure without VM-level overhead.
The insight was that the performance overhead of a full VM per function
invocation (Kata Containers approach) was unacceptable for Google's
millisecond-level function invocations. gVisor's user-space kernel adds
~10-30% CPU overhead compared to runc but starts in milliseconds vs.
Kata's 100-200ms VM boot. Google runs billions of gVisor instances per
day; its production hardening is among the most battle-tested of any
open-source container security technology.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A team must run user-submitted Python
scripts (untrusted code) with millisecond-level startup requirements.
gVisor adds 10-30% CPU overhead; Kata Containers add 100-200ms startup
latency. Which runtime is appropriate, and what are the constraints that
make the other unsuitable?
*Hint:* Consider the startup latency requirement (milliseconds rules out
Kata's VM boot). Consider the security model: is user-space kernel
interposition (gVisor) sufficient for Python script isolation, or is
VM-level isolation required? What is the threat model?

**Q2 (A - System Interaction):** A Kubernetes cluster uses containerd
with RuntimeClass for gVisor (untrusted namespace) and runc (trusted
namespace). An admission webhook enforces RuntimeClass in the untrusted
namespace. An attacker gains access to the Kubernetes API (via a
compromised CI token). What is the attack sequence to run a pod in
the trusted namespace (runc) without triggering the admission webhook?
*Hint:* Consider: deploying to the trusted namespace (if RBAC allows),
modifying the webhook configuration (if ClusterAdmin), or finding a
namespace not covered by the webhook selector.

**Q3 (B - Scale):** A managed Kubernetes cluster (GKE) has two node
pools: standard (containerd/runc) and sandbox (containerd/gVisor). The
sandbox node pool has 5 nodes. An autoscaling event requires 20 gVisor
pods simultaneously (user-submitted functions spike). What happens to
the 15 pods that cannot be scheduled, and how does cluster autoscaler
interact with RuntimeClass node pool constraints?
*Hint:* Consider GKE cluster autoscaler's awareness of node pool labels
and RuntimeClass constraints. Will it scale the correct node pool?
What is the latency between the scaling trigger and pod scheduling?
'@

# ── CTR-048 ──────────────────────────────────────────────────────────────
$ctr048 = @'
---
id: CTR-048
title: "Container Runtime Internals (runc, containerd)"
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-017, CTR-018, CTR-025, CTR-042
used_by: CTR-049
related: CTR-047, CTR-050
tags:
  - containers
  - internals
  - deep-dive
  - linux
  - first-principles
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /ctr/container-runtime-internals-runc-containerd/
---

# CTR-048 - Container Runtime Internals (runc, containerd)

⚡ TL;DR - A container starts via a two-layer runtime stack: containerd (high-level, manages image and lifecycle) calls runc (low-level, sets up Linux namespaces and cgroups and exec's the process) using the OCI Runtime Specification.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | CTR-017, CTR-018, CTR-025, CTR-042 |     |
| **Used by:**    | CTR-049                            |     |
| **Related:**    | CTR-047, CTR-050                   |     |

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

- [[CTR-017 - Linux Namespaces]] - the kernel isolation primitive runc uses
- [[CTR-018 - Cgroups]] - the resource constraint primitive runc uses
- [[CTR-025 - containerd]] - the high-level runtime
- [[CTR-042 - Container Runtime Interface (CRI)]] - the API layer above containerd

**Builds On This (learn these next):**

- [[CTR-049 - Linux Namespace and Cgroup Architecture]] - deeper kernel internals

**Alternatives / Comparisons:**

- [[CTR-047 - Multi-Runtime Container Strategy (containerd, CRI-O)]] - runtime choices
- [[CTR-050 - Container Image Format Design (OCI)]] - the OCI image spec that feeds containerd

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
│ NEXT EXPLORE│ CTR-049 Namespace/Cgroup Architecture│
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
'@

# ── CTR-049 ──────────────────────────────────────────────────────────────
$ctr049 = @'
---
id: CTR-049
title: Linux Namespace and Cgroup Architecture
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-017, CTR-018
used_by: CTR-048
related: CTR-050, CTR-048
tags:
  - containers
  - linux
  - internals
  - deep-dive
  - first-principles
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /ctr/linux-namespace-and-cgroup-architecture/
---

# CTR-049 - Linux Namespace and Cgroup Architecture

⚡ TL;DR - Linux namespaces provide process isolation (what a process can see); cgroups provide resource control (how much a process can use). Together, they are the kernel primitives that make containers possible.

| Metadata        |                    |     |
| :-------------- | :----------------- | :-- |
| **Depends on:** | CTR-017, CTR-018   |     |
| **Used by:**    | CTR-048            |     |
| **Related:**    | CTR-050, CTR-048   |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Linux namespaces, if two processes ran on the same machine, they
shared the same PID space, network stack, filesystem view, and hostname.
Process isolation required separate VMs - expensive, slow to start, and
wasteful of resources. There was no in-kernel mechanism to give a process
a private view of the system without full VM overhead.

**THE BREAKING POINT:**
Running multiple web applications on a single server: app A's dependency
upgrade breaks app B. App A's process can see and signal app B's process.
App A's network listener can conflict with app B's listener on the same
port. App A can exhaust the system's memory, starving app B. Shared
execution environments require heavyweight separation (VMs) or fragile
coordination.

**THE INVENTION MOMENT:**
Linux 3.8 (2013) completed the namespace suite: PID, network, mount,
UTS, IPC, user, and cgroup namespaces. Cgroups v1 (2007) added resource
control. Together they provided the kernel primitives for "lightweight
virtual machines" - what we now call containers. Docker's 2013 launch
was largely the packaging of these existing kernel features into a
developer-friendly tool.

**EVOLUTION:**
2007: Cgroups v1 merged into Linux kernel. 2008: LXC (Linux Containers)
uses namespaces + cgroups for containers. 2013: Linux 3.8 completes
the namespace suite (user namespaces). Docker 1.0 released. 2016:
Cgroups v2 merged (unified hierarchy, improved accounting). 2019: User
namespaces become production-stable. 2022: Cgroups v2 becomes the
default in major distributions (RHEL 9, Ubuntu 22.04). Kubernetes adds
cgroup v2 support. 2023: Rootless containers (using user namespaces)
become production-viable without kernel patches.

---

### 📘 Textbook Definition

**Linux namespaces** are kernel features that partition global system
resources into isolated per-namespace instances. Seven namespace types
exist: PID (process IDs), Network (network stack), Mount (filesystem
tree), UTS (hostname and NIS domain name), IPC (System V IPC, POSIX
message queues), User (user and group IDs), and Cgroup (cgroup root).
**Linux cgroups** (control groups) are a kernel mechanism to limit,
account for, and isolate the resource usage (CPU, memory, I/O, network)
of a collection of processes. Together, namespaces + cgroups implement
container isolation and resource governance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Namespaces control what a process can see; cgroups control how much
it can consume.

**One analogy:**

> Namespaces are like hotel rooms: each guest (process) has their own
> room with their own view (filesystem), their own phone number (IP
> address), and their own room number (PID 1 in their namespace). Cgroups
> are the hotel's utility meters: each room has a maximum electricity
> (CPU) and water (memory) allowance, enforced by the building systems.

**One insight:**
A container is not a separate OS. It is a set of processes that share
the host kernel but see an isolated view of system resources via
namespaces, and are constrained in resource usage by cgroups. When a
container "escapes", it means the isolation provided by namespaces is
defeated, and the process can access resources outside its namespace.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Namespaces are per-process** - each process has a namespace
   membership for each namespace type. A process is "in" a PID
   namespace, a network namespace, etc.
2. **Namespaces are hierarchical** - child processes inherit parent
   namespaces. Creating a new namespace creates a new root for that
   resource view.
3. **Cgroups control resource usage, not visibility** - cgroups limit
   how much CPU, memory, and I/O a set of processes can use. They do
   not affect what the processes can see.
4. **Cgroups v2 uses a single unified hierarchy** - unlike cgroups v1
   (separate hierarchy per controller), cgroups v2 has one tree with
   all controllers attached at each node.

**DERIVED DESIGN:**
Given invariant 2: containers are created by calling `clone` with the
appropriate `CLONE_NEW*` flags, which creates the child process in new
namespaces. Given invariant 3: namespace + cgroup must both be configured;
a process isolated by namespaces but without cgroup limits can still
consume all host CPU and memory.

**THE TRADE-OFFS:**
**Gain:** Namespaces + cgroups provide lightweight isolation with near-
zero overhead compared to full VMs. Container startup is milliseconds
vs. VM startup in seconds.
**Cost:** All containers share the host kernel. A kernel vulnerability
can be exploited from any container regardless of namespace isolation.
Namespaces provide visibility isolation, not kernel isolation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Seven namespace types exist because seven global system
resources required separate isolation (PID, network, filesystem, etc.).
**Accidental:** Cgroups v1's separate hierarchy per controller (one tree
for CPU, another for memory) created complex interaction effects. Cgroups
v2 unified them.

---

### 🧪 Thought Experiment

**SETUP:**
Two processes run on the same Linux host without any namespace isolation.

**WHAT HAPPENS:**
Process A can see all processes on the host via `/proc`. Process A can
send SIGKILL to process B. Process A can bind to any port. Process A
can mount and unmount filesystems. Process A can read /etc/hosts and
modify it (affecting process B). There is no isolation.

**WHAT HAPPENS WITH NAMESPACES:**
Process A is placed in new PID, network, mount, and UTS namespaces.
From process A's perspective: it is PID 1 in its namespace (sees only
its own descendant processes in /proc). It has its own network interface
and IP address. It has its own /etc/hosts and /etc/hostname. It cannot
see or signal processes in other namespaces. It cannot bind to ports
that are already in use in its own network namespace.

**THE INSIGHT:**
Namespaces create the illusion of a private system for each container.
The kernel maintains the mapping between global resource IDs and
namespace-local IDs. When process A looks up PID 1, the kernel returns
its own PID (the first process in its PID namespace) not the host's
PID 1 (init/systemd).

---

### 🧠 Mental Model / Analogy

> Namespaces are like a magic mirror in a hotel hallway. Each guest who
> looks in the mirror sees a different view of the hotel. Guest A sees
> themselves as the only guest (PID namespace), with their own room
> (filesystem), their own phone network (network namespace). But all
> guests are actually in the same physical building (same kernel). The
> mirror is the kernel's namespace translation layer.

Element mapping:

- **Physical building** = Linux host kernel
- **Magic mirror** = namespace translation layer
- **Guest's unique view** = process's namespace-local view
- **Room** = mount namespace (container filesystem)
- **Phone network** = network namespace
- **Guest number** = PID (namespace-local)
- **Building utilities** = cgroups (CPU, memory limits)

Where this analogy breaks down: a real hotel's walls are physical
barriers; namespace isolation is a kernel-level software boundary that
can be defeated by kernel vulnerabilities.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Linux has built-in features that let programs pretend they are the only
program running (namespaces) and that limit how much CPU and memory
each program can use (cgroups). Docker and Kubernetes use these features
to run multiple isolated containers on one machine.

**Level 2 - How to use it (junior developer):**
You rarely manipulate namespaces or cgroups directly - Docker and
Kubernetes do it for you. But when debugging, `nsenter` lets you enter
a container's namespaces from the host. `cat /proc/<pid>/cgroup` shows
which cgroup a process is in. `cat /sys/fs/cgroup/<cgroup>/memory.current`
shows current memory usage.

**Level 3 - How it works (mid-level engineer):**
When runc creates a container, it calls `clone(CLONE_NEWPID |
CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS | CLONE_NEWIPC)`. The child
process starts in new namespaces. runc then mounts the container
filesystem, writes `hostname`, and sets up the cgroup via the cgroup
filesystem (`/sys/fs/cgroup`). The container process is then exec'd
into the configured environment.

**Level 4 - Why it was designed this way (senior/staff):**
Each namespace type was added independently in the Linux kernel as the
demand arose. PID namespaces (2008) solved process isolation. Network
namespaces (2009) solved network isolation. User namespaces (2013)
solved privilege separation (allowing containers to run as root inside
the namespace without host root privileges). Cgroups v2 (2016) unified
the controller hierarchy to solve the v1 coordination problems (memory
accounting inconsistencies between controllers, difficulty attaching
single processes to multiple v1 hierarchies).

**Expert Thinking Cues:**

- "Is the container running with user namespaces enabled? If not, root
  inside the container is root on the host kernel."
- "Is the cgroup v1 or v2? v2 is required for correct memory accounting
  in Kubernetes QoS classes on modern distributions."
- "Can a process in this container enter another container's namespace
  via /proc/<pid>/ns/*? If the container has CAP_SYS_PTRACE, yes."

---

### ⚙️ How It Works (Mechanism)

**SEVEN NAMESPACE TYPES:**

```
PID   - Process IDs: containers have PID 1
NET   - Network stack: own IP, routes, iptables
MNT   - Mount tree: own filesystem view
UTS   - Hostname and NIS domain name
IPC   - System V IPC, POSIX message queues
USER  - UID/GID mapping (root inside != root outside)
CGROUPNS - Cgroup root (container sees its cgroup root)
```

**CGROUP V2 HIERARCHY:**

```
/sys/fs/cgroup/                  (root cgroup)
  kubepods/
    burstable/
      pod<uuid>/
        <container-id>/
          cpu.max        # CPU limit
          memory.max     # Memory hard limit
          memory.high    # Soft memory limit
          io.max         # Block I/O limit
```

**NAMESPACE SYSTEM CALLS:**

```
clone(CLONE_NEWPID|CLONE_NEWNET|...) - create new namespaces
unshare(CLONE_NEWNS)                 - leave current namespace
setns(fd, nstype)                    - join existing namespace
/proc/<pid>/ns/                      - namespace file descriptors
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Container Start):**

```
runc: clone() with CLONE_NEW* flags
  |   Child process in new namespaces
  |           ← YOU ARE HERE
  v
runc: pivot_root() - switch to container rootfs
  |
  v
runc: mount proc, sys, dev in new MNT ns
  |
  v
runc: write cgroup limits to cgroup v2 files
  |
  v
runc: set capabilities, seccomp filter
  |
  v
runc: exec() container entrypoint
Container runs with isolated view + resource limits
```

**FAILURE PATH:**
Container process exceeds cgroup memory limit. Kernel OOM killer fires
within the cgroup. Container PID 1 receives SIGKILL. Pod enters
`OOMKilled` state. Without cgroup limits, the process could exhaust
host memory, causing node-level OOM affecting all pods.

**WHAT CHANGES AT SCALE:**
At scale, cgroup accounting overhead accumulates across thousands of
containers. Cgroup v2 reduces this overhead vs. v1. The cgroup hierarchy
must be maintained consistently - stale cgroup directories from deleted
containers accumulate if not cleaned up.

---

### 💻 Code Example

```bash
# Inspect namespaces of a running container
PID=$(docker inspect --format='{{.State.Pid}}' nginx)
ls -la /proc/$PID/ns/
# Each symlink is a namespace the process is in

# Enter a container's network namespace from the host
nsenter --target $PID --net -- ip addr
# Shows the container's network interfaces, not host's

# Enter a container's mount namespace
nsenter --target $PID --mount -- ls /
# Shows the container's filesystem, not host's

# Inspect cgroup membership
cat /proc/$PID/cgroup
# Shows the cgroup hierarchy paths for this process

# Check cgroup v2 memory limits
CGROUP=$(cat /proc/$PID/cgroup | \
  grep "0::" | cut -d: -f3)
cat /sys/fs/cgroup${CGROUP}/memory.max
cat /sys/fs/cgroup${CGROUP}/memory.current

# Check CPU limits (cgroup v2)
cat /sys/fs/cgroup${CGROUP}/cpu.max
# Format: quota period (e.g. 500000 1000000 = 50% of one CPU)
```

```bash
# Create a namespace manually (demo/learning)
# Create a new network namespace
ip netns add mytest
ip netns exec mytest ip addr   # only loopback visible

# Create a process in a new PID namespace
unshare --pid --fork --mount-proc bash
# Inside: ps aux shows only this bash process (PID 1)
```

**How to test / verify correctness:**

```bash
# Verify cgroup limits are applied
kubectl run memtest --image=polinux/stress \
  --limits='memory=128Mi' -- stress --vm 1 \
  --vm-bytes 256M --vm-hang 0

# Check that OOMKill fires (not host OOM)
kubectl describe pod memtest | grep OOMKilled

# Verify namespace isolation
POD=$(kubectl get pod -l app=nginx -o name | head -1)
kubectl exec $POD -- hostname  # container hostname
hostname                        # host hostname - different
```

---

### ⚖️ Comparison Table

| Namespace Type | Isolates | System Call | Container Equivalent |
|---|---|---|---|
| PID | Process IDs | clone(CLONE_NEWPID) | Container PID 1 |
| NET | Network stack | clone(CLONE_NEWNET) | Container IP/ports |
| MNT | Filesystem | clone(CLONE_NEWNS) | Container rootfs |
| UTS | Hostname | clone(CLONE_NEWUTS) | Container hostname |
| IPC | SysV IPC | clone(CLONE_NEWIPC) | Inter-process comms |
| USER | UID/GID | clone(CLONE_NEWUSER) | Rootless containers |
| CGROUP | Cgroup root | clone(CLONE_NEWCGROUP) | Cgroup visibility |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A container is a mini-VM" | A container is a set of processes with isolated views (namespaces) and resource limits (cgroups). It shares the host kernel. A VM has its own kernel; a container does not. |
| "Root in a container is not dangerous" | Without user namespaces, root (UID 0) inside a container is root on the host kernel. A privileged container can access host devices, load kernel modules, and bypass most namespace isolation. |
| "Cgroups prevent a container from crashing the host" | Cgroups limit CPU and memory but do not protect all resources. A container can still exhaust PIDs (fork bomb), file descriptors, or network connections if `pids.max`, `nofile`, and network limits are not set. |
| "Namespace isolation is equivalent to VM isolation" | A VM has a separate kernel; namespaces share the host kernel. A kernel vulnerability exploitable from inside a namespace can affect the host. VM isolation requires a hypervisor boundary. |
| "Cgroups v1 and v2 are interchangeable" | Cgroups v2 has a unified hierarchy and improved memory accounting. Kubernetes features like memory QoS require cgroups v2. Running mixed v1/v2 on a node causes Kubernetes to use only v1 features. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: OOMKilled - Missing or Misconfigured Cgroup Limit**
**Symptom:** Pod restarts repeatedly with `OOMKilled` status. The
application appears to need less than the configured memory limit.
**Root Cause:** The application has a memory leak. The cgroup memory
limit correctly kills it when it exceeds the limit. The limit may also
be set too low for the actual working set.
**Diagnostic:**

```bash
# Check OOM events
kubectl describe pod <pod> | grep -i oom

# Check actual memory usage over time
kubectl top pod <pod>

# Check cgroup memory events on the node
CGROUP=$(cat /proc/$POD_PID/cgroup | \
  grep "0::" | cut -d: -f3)
cat /sys/fs/cgroup${CGROUP}/memory.events
# Look for oom_kill count
```

**Fix:** Increase memory limit to match actual working set, or fix
the memory leak. Add memory `requests` to ensure the pod is scheduled
on a node with sufficient available memory.
**Prevention:** Set memory `requests` equal to expected steady-state
usage. Set `limits` to peak usage + 20% buffer. Monitor `memory.high`
events (soft limit) before `memory.max` (hard limit + OOMKill) is hit.

---

**Failure Mode 2: PID Exhaustion (fork bomb protection)**
**Symptom:** Pod cannot start new processes. `kubectl exec` hangs.
Application logs show `fork: Resource temporarily unavailable`.
**Root Cause:** The container has exhausted its PID namespace cgroup
limit. A fork bomb, a thread leak, or missing `pids.max` allows PID
exhaustion.
**Diagnostic:**

```bash
# Check PID count inside container
kubectl exec <pod> -- cat /proc/sys/kernel/pid_max
kubectl exec <pod> -- ls /proc | wc -l

# Check cgroup PID limit
CGROUP=$(cat /proc/$POD_PID/cgroup | \
  grep "0::" | cut -d: -f3)
cat /sys/fs/cgroup${CGROUP}/pids.max
cat /sys/fs/cgroup${CGROUP}/pids.current
```

**Fix:** Set `pids.max` in the pod spec (`spec.containers[].resources`
does not expose this directly - requires admission webhook or RuntimeClass
configuration). Kill the leaking process.
**Prevention:** Set Kubernetes `--pod-max-pids` flag. Enable `PodPidsLimit`
admission plugin to enforce PID limits per pod.

---

**Failure Mode 3: Network Namespace Leak (Security)**
**Symptom:** `ip netns list` on the host shows thousands of network
namespaces. Host netfilter/conntrack table is exhausted.
**Root Cause:** Containers are deleted but their network namespaces are
not cleaned up (CNI plugin cleanup bug). Each orphaned namespace retains
netfilter rules and conntrack state.
**Diagnostic:**

```bash
# Count network namespaces on the host
ip netns list | wc -l

# Check for orphaned namespaces (no process in them)
for ns in $(ip netns list | awk '{print $1}'); do
  count=$(ip netns exec $ns ls /proc | wc -l)
  [ "$count" -lt 2 ] && echo "Empty: $ns"
done

# Check conntrack table usage
conntrack -C
cat /proc/sys/net/netfilter/nf_conntrack_max
```

**Fix:** Manually clean orphaned namespaces: `ip netns delete <ns>`.
File a bug against the CNI plugin. Upgrade to patched version.
**Prevention:** Monitor namespace count on nodes. Alert if count exceeds
expected maximum (pods per node * 2). Validate CNI cleanup with chaos
engineering (delete pods rapidly and check namespace count returns to
baseline).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-017 - Linux Namespaces]] - namespace concepts overview
- [[CTR-018 - Cgroups]] - cgroup concepts overview

**Builds On This (learn these next):**

- [[CTR-048 - Container Runtime Internals (runc, containerd)]] - how runc uses namespaces/cgroups

**Alternatives / Comparisons:**

- [[CTR-050 - Container Image Format Design (OCI)]] - the image layer (not isolation)
- [[CTR-048 - Container Runtime Internals (runc, containerd)]] - how runc wires it together

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Kernel primitives for containers    │
│ PROBLEM     │ Lightweight isolation without VMs   │
│ KEY INSIGHT │ Namespaces = visibility; cgroups=use│
│ USE WHEN    │ Debugging isolation or resource issues│
│ AVOID WHEN  │ N/A - always active for containers  │
│ TRADE-OFF   │ Lightweight isolation vs. shared    │
│             │ kernel vulnerability surface         │
│ ONE-LINER   │ namespaces see; cgroups limit       │
│ NEXT EXPLORE│ CTR-048 Runtime Internals           │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Seven namespace types provide isolation of visibility; cgroups provide
   resource limits - both are required for container isolation.
2. Root inside a container without user namespaces is root on the host
   kernel - user namespaces are the key to rootless containers.
3. Cgroups v2 (unified hierarchy) is required for correct Kubernetes
   memory QoS - prefer distributions that default to cgroups v2.

**Interview one-liner:**
"Linux containers are processes in new namespaces (PID, NET, MNT, UTS,
IPC, USER) that provide an isolated system view, constrained by cgroups
that limit CPU, memory, and I/O - the two kernel mechanisms together
implement container isolation without a separate kernel."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Visibility isolation (namespaces) and resource isolation (cgroups) are
orthogonal concerns that must both be applied. A process with a private
view but no resource limits can starve all other processes. A process
with resource limits but a shared view can read other processes' data.
Complete isolation requires both dimensions independently satisfied.

**Where else this pattern appears:**

- **Operating system process model:** Processes have separate virtual
  address spaces (visibility isolation) and are scheduled with CPU
  quotas (resource isolation). The OS applies both independently.
- **Database multi-tenancy:** Schema-level isolation (visibility) +
  query-level resource groups (resource limits) together provide tenant
  isolation. Either alone is insufficient.
- **Cloud account IAM:** IAM policies restrict what a user can see
  (visibility); service quotas and budget alerts restrict how much they
  can consume (resource limits). Both are required for multi-tenant
  cloud governance.

---

### 💡 The Surprising Truth

Linux namespaces and cgroups were not designed with containers in mind.
Namespaces were added to Linux between 2002 and 2013 primarily for the
Linux-VServer project (a competing container technology that never became
mainstream). Cgroups were added in 2007 by Google engineers who needed
resource governance for Google's internal workload scheduler (Borg).
Docker's 2013 innovation was not inventing new kernel technology - it
was discovering that packaging these existing, independently developed
kernel features together with a developer-friendly CLI and image format
created something genuinely new: the modern container. The kernel
developers who wrote namespaces and cgroups in the 2000s largely did
not anticipate the container revolution their work would enable.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** A container running as UID 1000 inside
a user namespace is mapped to UID 100000 on the host. If the container
writes a file, what UID owns the file on the host filesystem? If the
container is given CAP_CHOWN inside its user namespace, can it change
the ownership of a host file to UID 0? Why or why not?
*Hint:* User namespace UID mapping means the container's UID 1000 maps
to host UID 100000. File ownership uses the host UID in the filesystem.
CAP_CHOWN inside a user namespace is scoped to that namespace's UID
range. What is the boundary of the capability?

**Q2 (D - Root Cause):** A Kubernetes pod has `memory: limits: 512Mi`
but the node is running cgroups v1. The application uses both malloc
(heap memory) and mmap (file-backed memory). The cgroup `memory.limit_in_bytes`
is correctly set to 512Mi. However, the pod's RSS exceeds 512Mi without
triggering OOMKill. How is this possible under cgroups v1?
*Hint:* Cgroups v1 has separate `memory` and `kmem` controllers.
File-backed mmap pages may be accounted differently than heap pages.
Page cache can grow beyond the limit under certain v1 accounting
configurations. How does cgroups v2's unified memory controller fix this?

**Q3 (C - Design Trade-off):** Rootless containers (user namespaces)
allow non-root users to run containers. However, a limitation is that
user namespace containers cannot bind to ports below 1024 (privileged
ports). A web server container needs to listen on port 80. What are
the three approaches to solve this, and what are their security
trade-offs?
*Hint:* Consider: (1) map the container port 80 to a host port >1024
via network namespace port mapping, (2) set the `net.ipv4.ip_unprivileged_port_start`
sysctl to 0 (all ports unprivileged), (3) use `CAP_NET_BIND_SERVICE`
with user namespace ambient capabilities. Which approach is least
privilege?
'@

# ── CTR-050 ──────────────────────────────────────────────────────────────
$ctr050 = @'
---
id: CTR-050
title: Container Image Format Design (OCI)
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-010, CTR-011, CTR-024
used_by: CTR-045
related: CTR-034, CTR-048
tags:
  - containers
  - internals
  - deep-dive
  - first-principles
  - docker
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /ctr/container-image-format-design-oci/
---

# CTR-050 - Container Image Format Design (OCI)

⚡ TL;DR - An OCI container image is a content-addressable collection of layers (tar archives) plus a JSON manifest and image config - all stored in a registry as blobs identified by their SHA-256 digest.

| Metadata        |                        |     |
| :-------------- | :--------------------- | :-- |
| **Depends on:** | CTR-010, CTR-011, CTR-024 |     |
| **Used by:**    | CTR-045                |     |
| **Related:**    | CTR-034, CTR-048       |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2014, Docker had its own proprietary image format. CoreOS developed
rkt with a different image format (ACI). Running a container image built
for Docker on rkt was impossible. The container ecosystem was fragmenting
along runtime/image format lines before it had a chance to mature.

**THE BREAKING POINT:**
Cloud providers, CI tools, and orchestrators had to choose: support
Docker format only, or implement multiple format converters. Kubernetes
1.0 needed to work with both Docker and rkt. Every registry had to
understand both formats. The ecosystem needed a common standard.

**THE INVENTION MOMENT:**
The Open Container Initiative (OCI) was founded in 2015 by Docker,
CoreOS, Google, and others. Two specifications emerged: OCI Image Spec
(what an image is) and OCI Runtime Spec (how to run it). Any registry
that stores OCI images and any runtime that implements OCI Runtime Spec
can interoperate. Docker images were reformatted to comply with OCI
Image Spec v1.0 (2017).

**EVOLUTION:**
2017: OCI Image Spec v1.0. All major registries and runtimes converge.
2019: OCI Distribution Spec standardises the registry HTTP API (previously
only Docker Registry API v2 was used). 2021: OCI Artifacts extend the
spec to store non-image content (Helm charts, WASM modules, SBOMs)
in OCI registries using the same content-addressable model. 2023:
OCI Image Spec v1.1 adds referrers API (attaching SBOMs and signatures
to images without modifying the image itself).

---

### 📘 Textbook Definition

**OCI Image Spec** defines a container image as a content-addressable
artifact stored in an OCI-compliant registry. An image consists of: a
**manifest** (JSON document listing the config blob and layer blobs
by digest), an **image config** (JSON document with environment,
entrypoint, working directory, and the layer diff chain), and one or
more **layer blobs** (gzip-compressed tar archives of filesystem
changes). All blobs are identified by their SHA-256 digest, enabling
deduplication and integrity verification.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An OCI image = manifest (index) + config (metadata) + layers (filesystem
diffs), all stored as content-addressed SHA-256 blobs in a registry.

**One analogy:**

> An OCI image is like a recipe book. The manifest is the table of
> contents (lists all pages by page number). The config is the recipe
> intro (cooking instructions, temperature, time). Each layer is a
> recipe step (add these ingredients). The SHA-256 digest is the page
> number - if you know the page number (digest), you know exactly what
> is on that page (content-addressable).

**One insight:**
Content-addressability is the OCI image's most important property: the
SHA-256 digest of a blob is both its identifier and its integrity check.
You cannot have a valid blob with a wrong digest. This makes image
pull atomic: either you got the correct content, or the pull fails.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Content-addressability** - every blob is named by its SHA-256
   digest. Two blobs with the same content have the same name, enabling
   deduplication across images.
2. **Layers are filesystem diffs** - each layer is a tar archive of
   files added, modified, or deleted relative to the layer below. The
   union filesystem (overlayfs) merges layers at runtime.
3. **The manifest is the entry point** - to pull an image, you fetch
   the manifest by tag or digest. The manifest references all other
   blobs. Tags are mutable references to manifests; digests are
   immutable.
4. **Image configs are separate from layers** - the config stores
   metadata (environment, entrypoint, ports, labels) independently of
   the filesystem content. A config change creates a new image without
   re-uploading layers.

**DERIVED DESIGN:**
Given invariant 1: a base image layer shared by 100 images is stored
once in the registry and pulled once to a node. Deduplication is
automatic. Given invariant 3: pinning by digest (`myapp@sha256:abc123`)
is immutable and safe for production; pinning by tag (`myapp:v1.0`) is
mutable and risks silent changes.

**THE TRADE-OFFS:**
**Gain:** Content-addressable storage enables deduplication, integrity
verification, and immutable references. Layer sharing reduces registry
storage and pull bandwidth.
**Cost:** Layers are append-only. To "remove" a file from a layer below,
a whiteout file must be added in a higher layer - the file is hidden
but still present in the lower layer's blob. This means sensitive data
accidentally added to a lower layer cannot be truly removed without
rebuilding from scratch.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Content-addressable blobs, manifests, and image configs
are all required to enable deduplication, integrity, and metadata
separation.
**Accidental:** Docker Image Spec v1 (pre-OCI) embedded metadata inside
layers, making layer reuse difficult. OCI cleaned this up.

---

### 🧪 Thought Experiment

**SETUP:**
100 microservices all share the same Java 21 base image (150 MB). Each
service adds ~20 MB of application code on top.

**WHAT HAPPENS WITHOUT CONTENT-ADDRESSABLE STORAGE:**
Each of the 100 images stores its own copy of the 150 MB base layer.
Registry storage: 100 * 170 MB = 17 GB. Each node pull downloads the
full 170 MB per new service, even if the base layer is already present.

**WHAT HAPPENS WITH CONTENT-ADDRESSABLE OCI STORAGE:**
The 150 MB base layer has one SHA-256 digest. It is stored once in the
registry (150 MB). All 100 services reference this digest in their
manifests. Each service only stores its unique 20 MB layer.
Registry storage: 150 MB + (100 * 20 MB) = 2.15 GB (87% reduction).
A node that already has the base layer cached only pulls the 20 MB
service layer for each new service.

**THE INSIGHT:**
Content-addressable layer sharing is an emergent property of the OCI
design, not an explicit optimisation. It falls out automatically from
naming blobs by their content digest. The engineering insight is that
the same principle (content-addressable storage) used in Git and
BitTorrent is also the right model for container image distribution.

---

### 🧠 Mental Model / Analogy

> An OCI image in a registry is like a book in a library's card catalog
> system. The catalog entry (manifest) tells you: "This book uses
> chapter drafts 1a, 2b, and 3c (layer blobs)." Each draft is filed by
> its content hash (digest). If two books share chapter 1 text verbatim,
> there is only one physical copy of that chapter in storage. To read
> the book, you retrieve each chapter draft and stack them in order.

Element mapping:

- **Catalog entry** = OCI manifest
- **Chapter draft** = image layer blob (tar archive)
- **Content hash** = SHA-256 blob digest
- **Book title** = image tag
- **Reading the book** = overlayfs layer merge at runtime
- **Library** = OCI-compliant container registry

Where this analogy breaks down: library books are not stacked and merged
into a combined view; image layers are merged by overlayfs into a single
filesystem view at container runtime.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A container image is like a layered stack of filesystem changes, stored
in a registry. Each layer is a small compressed file. The registry
stores each unique layer once, even if many images share it.

**Level 2 - How to use it (junior developer):**
Understanding OCI format helps you optimise Dockerfiles: put frequently
changing layers (your app code) at the bottom; put stable layers
(base OS, runtime) at the top. This maximises cache sharing. Use
`docker image history` to see your image's layers and sizes.

**Level 3 - How it works (mid-level engineer):**
A registry stores blobs identified by digest. When you push an image,
the CLI computes SHA-256 of each layer, checks if the blob exists in
the registry (via HEAD request), and skips upload if it does. The
manifest references layer digests. When you pull, the CLI fetches the
manifest, then fetches each referenced blob (skipping ones already
in the local cache). containerd stores layers in its content store;
overlayfs merges them at container start.

**Level 4 - Why it was designed this way (senior/staff):**
Content-addressable storage (CAS) was chosen because it solves
deduplication and integrity simultaneously with no additional mechanism.
In a non-CAS system, you need a separate deduplication index and a
separate integrity check. In CAS, the name is the integrity check, and
deduplication is automatic (same content = same name = same blob).
Git uses the same principle for commits and trees. The OCI designers
explicitly borrowed from Git and the academic content-addressable
storage literature.

**Expert Thinking Cues:**

- "Is this image tag mutable? If we pin to the tag in production, can
  it silently change? Use digest pinning for production."
- "A file was added to layer 2 and deleted in layer 4. Is the file
  still present in registry storage? Yes - layer 2's blob still contains
  it. Security implication?"
- "If I change only the CMD in the Dockerfile (no filesystem changes),
  does that create a new layer? No - CMD is stored in the image config,
  not a layer."

---

### ⚙️ How It Works (Mechanism)

**OCI IMAGE STRUCTURE:**

```
Registry
  └─ myapp:v1.0  (tag - mutable pointer)
      └─ manifest.json  (sha256:abc...)
          ├─ config: sha256:def...
          │   { "Env": [...], "Cmd": [...],
          │     "RootFS": {"type": "layers",
          │     "diff_ids": [sha256:l1, ...]}}
          ├─ layer: sha256:l1...  (base OS)
          ├─ layer: sha256:l2...  (runtime)
          └─ layer: sha256:l3...  (app code)
```

**OVERLAYFS LAYER MERGE AT RUNTIME:**

```
Layer 3 (top, app code)    <- upperdir (writable)
Layer 2 (runtime)
Layer 1 (base OS, bottom)  <- lowerdir (read-only)
              |
              v overlayfs merge
              |
Unified view: / (container sees merged filesystem)
```

**WHITEOUT FILES (layer deletion):**

```
Layer 2 adds: .wh.secret.txt
-> Whiteout file signals: hide secret.txt from Layer 1
-> secret.txt is still in Layer 1 blob in the registry
-> It is just hidden from the container's filesystem view
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Image Pull):**

```
docker pull / containerd pull myapp:v1.0
  |
  v
GET /v2/myapp/manifests/v1.0  (resolve tag)
  |         ← YOU ARE HERE
  v
Fetch manifest.json by digest
  |
  v
For each layer blob in manifest:
  HEAD /v2/myapp/blobs/<digest>
  (skip if already in local cache)
  GET /v2/myapp/blobs/<digest>
  (decompress + store in content store)
  |
  v
Fetch config blob
  |
  v
Create overlayfs snapshot from layers
Container ready to start
```

**FAILURE PATH:**
A layer blob is corrupted in transit (SHA-256 mismatch). containerd
rejects the blob and retries. If retries fail, the pull fails with
`unexpected EOF` or `digest mismatch`. The container cannot start with
a corrupted image.

**WHAT CHANGES AT SCALE:**
At scale, a registry serving 10,000 pull requests per hour becomes
the critical path for pod startup latency. Layer caching on nodes
(containerd content store) is essential. An image pull time of 30s for
a cold pull must be reduced via registry mirrors, node-local caches,
or lazy-loading (eStargz, SOCI snapshotter).

---

### 💻 Code Example

```bash
# Inspect OCI image structure directly
# Pull and examine manifest
docker manifest inspect myapp:v1.0

# OR use skopeo (works without Docker daemon)
skopeo inspect --raw docker://myapp:v1.0 | python3 -m json.tool

# Example manifest output:
# {
#   "schemaVersion": 2,
#   "mediaType": "application/vnd.oci.image.manifest.v1+json",
#   "config": {
#     "digest": "sha256:def...",
#     "size": 7023
#   },
#   "layers": [
#     {"digest": "sha256:l1...", "size": 12345678},
#     {"digest": "sha256:l2...", "size": 23456789}
#   ]
# }

# Inspect image config
skopeo inspect docker://myapp:v1.0 | jq '{
  Env: .Env,
  Cmd: .Cmd,
  WorkingDir: .WorkingDir,
  Layers: .RootFS.Layers
}'

# View layer sizes (Dockerfile layer analysis)
docker image history myapp:v1.0 --no-trunc

# Export an OCI image to tarball for inspection
docker save myapp:v1.0 | tar -xv -C /tmp/image-inspect/
ls /tmp/image-inspect/
# blobs/   index.json   oci-layout
```

```bash
# Verify image digest matches expected value
# (detect tampering or corruption)
DIGEST=$(docker inspect --format='{{.Id}}' myapp:v1.0)
echo "Image digest: $DIGEST"

# Pin a deployment to a specific digest
docker pull myapp:v1.0
DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' myapp:v1.0)
echo "Deploy with: $DIGEST"
# myapp@sha256:abc123...
```

**How to test / verify correctness:**

```bash
# Verify OCI compliance of an image
# Install and run oci-image-tool
oci-image-tool validate --type image /tmp/image-inspect/

# Verify layer deduplication works
# Build two images sharing a base layer
docker build -t service-a -f Dockerfile.a .
docker build -t service-b -f Dockerfile.b .
# Both use same FROM base - only one copy stored locally
docker system df  # check image storage
```

---

### ⚖️ Comparison Table

| Format | Version | Manifest | Config | Layer | Registry API |
|---|---|---|---|---|---|
| Docker Image v1 | Pre-2017 | JSON in layer | In layer tarball | tar.gz | Docker Registry v2 |
| Docker Image v2 | 2016-2017 | Separate JSON | Separate JSON | tar.gz | Docker Registry v2 |
| OCI Image v1.0 | 2017 | Separate JSON | Separate JSON | tar.gz | OCI Distribution Spec |
| OCI Image v1.1 | 2023 | + Referrers API | Same | Same + zstd | OCI Distribution Spec v1.1 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Deleting a file in a Dockerfile removes it from the image" | A file deleted in a later layer has a whiteout entry hiding it, but the original file blob still exists in the registry. The image size includes the original layer. Use multi-stage builds to truly exclude files from the final image. |
| "Image tags are stable references" | Tags are mutable pointers to manifests. `myapp:latest` can point to a different manifest after a push. Only digest references (`myapp@sha256:...`) are immutable. |
| "A new CMD in Dockerfile creates a new layer" | CMD, ENV, LABEL, and EXPOSE are stored in the image config blob, not in filesystem layers. They do not add to the image filesystem size. |
| "OCI images require Docker to build" | OCI images can be built by Buildah, Kaniko, BuildKit, or ko. Docker is one builder, not the only one. The output of any compliant builder can be pushed to any OCI registry. |
| "Larger base images are always worse" | A distroless image with outdated packages may have more CVEs than a larger Alpine image with current packages. Size and vulnerability count are separate concerns. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Sensitive Data Leaked in Lower Layer**
**Symptom:** Security scan finds secrets (API keys, certificates) in
a container image layer that the developer thought was deleted.
**Root Cause:** A `RUN` instruction added a secret file; a later `RUN`
deleted it. The file is hidden by a whiteout in the upper layer but
still present in the lower layer's blob in the registry.
**Diagnostic:**

```bash
# Export image and inspect all layers
docker save myapp:v1.0 | tar xv -C /tmp/img/
cd /tmp/img/blobs/sha256/

# Extract each layer and search for secrets
for blob in *; do
  tar tz -f $blob 2>/dev/null | grep -i "secret\|key\|cert"
done
```

**Fix:** Rebuild the image from scratch using multi-stage build, never
adding the secret to any intermediate layer. Use `--secret` BuildKit
flag for build-time secrets (never persisted to layers).
**Prevention:** Use BuildKit secrets mount (`RUN --mount=type=secret`)
for all secrets used during build. Never copy secret files into the
image filesystem.

---

**Failure Mode 2: Image Pull Latency Causing Pod Start Timeout**
**Symptom:** Pods fail to start with `ImagePullBackOff`. Events show
`context deadline exceeded` during image pull. The image is large (2 GB).
**Root Cause:** Cold pull of a large image on a node that does not
have the layers cached. Registry is distant (cross-region) or slow.
**Diagnostic:**

```bash
# Check image pull time
time crictl pull myapp:v1.0

# Check registry response time
curl -o /dev/null -w "%{time_total}s\n" \
  https://registry.example.com/v2/myapp/manifests/v1.0

# Check node disk I/O during pull
iostat -x 1 5
```

**Fix:** Use a regional registry mirror or ECR pull-through cache. Use
lazy loading (eStargz or SOCI snapshotter) to start containers before
the full image is pulled. Reduce image size via multi-stage builds.
**Prevention:** Monitor image layer sizes in CI. Alert on images
exceeding 500 MB. Use registry mirrors for all production clusters.

---

**Failure Mode 3: Tag Mutation Causing Deployment Inconsistency**
**Symptom:** Two identical deployments behave differently. Investigation
reveals the `:latest` tag was pushed to with a new image between the
two deployments.
**Root Cause:** `imagePullPolicy: Always` with a mutable tag causes
different nodes to pull different versions of the same tag.
**Diagnostic:**

```bash
# Check what image SHA each pod is actually running
kubectl get pods -o json | jq '
  .items[] | {
    name: .metadata.name,
    imageID: .status.containerStatuses[].imageID
  }'

# Multiple different SHA256 values for the "same" image
# confirms tag mutation between pulls
```

**Fix:** Pin production deployments to image digests. Set
`imagePullPolicy: IfNotPresent` with digest-pinned images.
**Prevention:** CI pipeline outputs digest; CD pipeline uses digest
in manifests. Mutable tags (`latest`, `main`) are never used in
production Kubernetes manifests.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-010 - Docker Image]] - image fundamentals
- [[CTR-011 - Docker Layer]] - layer model and caching
- [[CTR-024 - OCI Standard]] - OCI overview

**Builds On This (learn these next):**

- [[CTR-045 - Container Image Strategy at Scale]] - strategy for managing images

**Alternatives / Comparisons:**

- [[CTR-034 - Docker BuildKit]] - the build tool that creates OCI images
- [[CTR-048 - Container Runtime Internals (runc, containerd)]] - how OCI images are consumed at runtime

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Content-addressable image format    │
│ PROBLEM     │ Format fragmentation pre-2015       │
│ KEY INSIGHT │ Digest = name + integrity check     │
│ USE WHEN    │ Understanding image pull, layer ops  │
│ AVOID WHEN  │ N/A - always the underlying model   │
│ TRADE-OFF   │ Layer immutability vs. secret leaks │
│ ONE-LINER   │ manifest + config + layers by SHA256│
│ NEXT EXPLORE│ CTR-045 Image Strategy, CTR-048 Runtime│
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. An OCI image = manifest + config + layers, all stored as SHA-256
   content-addressed blobs enabling automatic deduplication.
2. Tags are mutable; digests are immutable - use digest pinning in
   production for reproducible, tamper-evident deployments.
3. Files deleted in a later layer are hidden but not removed from the
   registry - secrets added to any layer are permanent until image
   is rebuilt from scratch.

**Interview one-liner:**
"An OCI image is a content-addressable artifact: manifest references
config and layer blobs by SHA-256 digest; digest naming enables automatic
deduplication, integrity verification, and immutable references; tags
are mutable pointers to manifests and should never be used for
production pinning."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Content-addressable storage solves deduplication and integrity as
emergent properties of naming by content hash. When the identifier of
a piece of data is derived from the data itself (SHA-256), you get
deduplication (same content = same identifier = stored once), integrity
(content that doesn't match its identifier is rejected), and immutability
(changing content changes the identifier) for free. Git, BitTorrent,
IPFS, and OCI images all use this principle.

**Where else this pattern appears:**

- **Git object storage:** Commits, trees, and blobs are named by
  SHA-1/SHA-256 of their content. The same file in two branches is
  stored once. Changing one byte creates a new object with a new hash.
  Git's integrity is inherent in its content-addressable model.
- **Package managers:** npm lockfiles and cargo.lock store package
  SHA-256 hashes. Installing from a lockfile verifies the content hash,
  preventing supply chain attacks where a package version is silently
  replaced.
- **Merkle trees (blockchains, Cassandra):** Distributed systems use
  content-addressed Merkle trees to verify data consistency across
  nodes without transmitting the full data.

---

### 💡 The Surprising Truth

Docker's original image format (v1, pre-2017) stored image metadata
inside the layer tarballs themselves - meaning two images with identical
filesystem content but different metadata (different author labels, for
example) stored different layer blobs and could not share layers in
the registry. This subtle design flaw meant that Docker's own layer
deduplication worked only for images with identical parent image
relationships. The OCI Image Spec v1 fixed this by separating the image
config from the layer content - metadata and filesystem are now stored
as separate blobs. This single architectural change made cross-image
layer deduplication truly universal and reduced registry storage for
large organisations by 40-60%.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** An OCI image has 5 layers. A container
is started from this image. The container writes a 100 MB file to its
filesystem. When the container is stopped, the image is unmodified (still
5 layers). Where did the 100 MB file go? What mechanism makes the
image immutable while the container can write?
*Hint:* overlayfs uses a writable upperdir per container instance.
The image's read-only layers are lowerdir. The container's writes go
to upperdir. The image blobs are never modified. What happens to the
upperdir when the container is removed?

**Q2 (C - Design Trade-off):** A DevOps team wants to attach a
vulnerability report (SBOM) to every container image in the registry
without modifying the image manifest (to avoid changing the image
digest). OCI Image Spec v1.1 provides a "referrers API" for this. What
would be the alternative (pre-v1.1) approach, and what are the
trade-offs?
*Hint:* Pre-v1.1, teams stored SBOMs as separate tagged images
(e.g., `myapp:v1.0-sbom`) with no formal link to the source image.
What are the discovery, association, and integrity problems with this
approach vs. the referrers API?

**Q3 (A - System Interaction):** A container registry uses the OCI
Distribution Spec. A client sends `GET /v2/myapp/manifests/v1.0`.
The registry returns the manifest. The client then sends HEAD requests
for each layer blob to check if they are already cached. One layer
(50 MB, sha256:abc) is already present on the client. The pull skips
that layer. Later, the registry operator deletes the blob sha256:abc
from the registry (storage cleanup). What happens to existing containers
running from images that reference sha256:abc?
*Hint:* Running containers use their local overlayfs snapshots (already
pulled). They do not need the registry blob. But what happens when a new
node tries to schedule a pod using the same image that references the
deleted blob?
'@

# ── Write files ───────────────────────────────────────────────────────────
$files = @{
    "CTR-047 - Multi-Runtime Container Strategy (containerd, CRI-O).md" = $ctr047
    "CTR-048 - Container Runtime Internals (runc, containerd).md" = $ctr048
    "CTR-049 - Linux Namespace and Cgroup Architecture.md" = $ctr049
    "CTR-050 - Container Image Format Design (OCI).md" = $ctr050
}

foreach ($name in $files.Keys) {
    $path = Join-Path $base $name
    [System.IO.File]::WriteAllText(
        $path, $files[$name],
        [System.Text.UTF8Encoding]::new($false))
    $lines = (Get-Content $path -Encoding UTF8).Count
    Write-Host "Written: $name ($lines lines)"
}

foreach ($name in $files.Keys) {
    $path = Join-Path $base $name
    $bytes = [IO.File]::ReadAllBytes($path)
    $bom = "$($bytes[0]),$($bytes[1]),$($bytes[2])"
    Write-Host "BOM check $name : $bom (must NOT be 239,187,191)"
}
