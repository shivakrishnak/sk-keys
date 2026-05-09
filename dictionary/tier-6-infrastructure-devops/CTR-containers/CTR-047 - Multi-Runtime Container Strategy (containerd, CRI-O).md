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