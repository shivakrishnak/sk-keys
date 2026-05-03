---
layout: default
title: "Ephemeral Container"
parent: "Containers"
nav_order: 841
permalink: /containers/ephemeral-container/
number: "0841"
category: Containers
difficulty: ★★★
depends_on: Container, Docker, Pod, Kubernetes Architecture, Linux Namespaces
used_by: Container Security, Kubernetes Architecture
related: Init Container, Sidecar Container, Pod, Distroless Images, Container Security
tags:
  - containers
  - kubernetes
  - debugging
  - advanced
  - production
---

# 841 — Ephemeral Container

⚡ TL;DR — Ephemeral containers are temporary debugging containers injected into a running pod without restarting it, solving the "distroless image has no shell" problem.

| #841 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Container, Docker, Pod, Kubernetes Architecture, Linux Namespaces | |
| **Used by:** | Container Security, Kubernetes Architecture | |
| **Related:** | Init Container, Sidecar Container, Pod, Distroless Images, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your production application runs in a distroless container image — no shell, no network tools, no debugging utilities. At 2 AM, a pod exhibits strange behaviour: elevated latency, unexpected outbound connections. To debug, you need to run `tcpdump`, `strace`, or `netstat` inside the pod's network namespace. But the image has none of these. Your options: (1) rebuild and redeploy a debug version of the image — this takes 15 minutes and may not reproduce the live state; (2) SSH into the node and try to identify the container process — this requires cluster-node access that should be restricted; (3) resign yourself to reading logs and guessing.

**THE BREAKING POINT:**
As teams adopt distroless and minimal images (which is correct security practice), they trade away the debuggability that comes with full OS images. The more secure the image, the harder it is to debug. This creates a painful tension: either keep debugging tools in images (CVE surface) or lose the ability to investigate live production issues.

**THE INVENTION MOMENT:**
This is exactly why ephemeral containers were introduced in Kubernetes 1.23 (stable) — a mechanism to temporarily attach a container with any image (including full debug toolkits) directly into a running pod, sharing its process, network, and filesystem namespaces, without restarting or altering the production container.

---

### 📘 Textbook Definition

An **ephemeral container** is a special type of container that can be added to a running Kubernetes Pod using `kubectl debug`. Unlike regular containers (which are declared in the Pod spec and run from Pod start), ephemeral containers are added after Pod creation, are not restarted if they exit, cannot define resource limits, and cannot be removed without restarting the Pod. They share all of the target pod's namespaces (PID, network, mount — depending on configuration) and can therefore observe and interact with the running application without modifying it. Ephemeral containers are a Kubernetes-specific concept — the underlying mechanism uses the Linux `setns()` syscall to join target namespaces.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An ephemeral container is a disposable debugging "parachute" you attach to a live production pod without disturbing it.

**One analogy:**
> Imagine a surgeon performing a delicate operation. The operating room is sterile and the procedure is in progress — you cannot stop and restart the surgery to change tools. But a new specialist appears in the doorway with special diagnostic equipment. Rather than cancelling the surgery, the specialist scrubs in, enters the same operating room, makes their observations, and leaves without disturbing the primary procedure. An ephemeral container is that visiting specialist — it joins the running context of the pod, does its work, and exits without affecting the patient (the production application).

**One insight:**
The power of ephemeral containers is rooted in Linux namespaces. Because containers in the same pod share network and PID namespaces, an ephemeral container joined to those namespaces can run `tcpdump` and see all the pod's network traffic, or attach `strace` to any process in the pod. The debug container has full visibility without the production image needing any debug tooling.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Containers are just processes with namespace isolation. Any new process can join an existing namespace by calling `setns()`.
2. Joining a namespace provides full visibility into that namespace — processes, network, filesystem.
3. Debugging context (namespace joins) must not require restarting the production process — restarts destroy in-flight state.

**DERIVED DESIGN:**

An ephemeral container is implemented as:

1. `kubectl debug` sends a `POST /api/v1/namespaces/<ns>/pods/<name>/ephemeralcontainers` request to the API server.
2. The kubelet receives the update and instructs containerd to start a new container in the pod's cgroup and namespace context.
3. The underlying containerd call uses `setns()` to join the target pod's namespaces.

**Namespace sharing options:**
- `--target <container-name>` — join the PID namespace of the specified container (allows `strace`, `pmap`, process inspection)
- Without `--target` — the ephemeral container joins the pod's sandbox (network namespace) but has its own PID namespace

```
┌──────────────────────────────────────────────────────────┐
│       Pod: Shared Namespaces                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Network Namespace (shared: all containers in pod)       │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │  Production Container │  │  Ephemeral Container     │ │
│  │  (distroless, no sh) │  │  (ubuntu, full tools)    │ │
│  │  PID 1: myapp        │  │  → can see pod's network  │ │
│  │  NET: 10.0.0.5       │  │  → if --target: sees PIDs │ │
│  └──────────────────────┘  └──────────────────────────┘ │
│                                                          │
│  Mount Namespace (not shared by default)                 │
│  Process Namespace (shared only with --target)           │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

**Gain:** Debug live production pods with distroless images. No restart required. Full network and process visibility.

**Cost:** Ephemeral containers require Kubernetes 1.23+. Cannot be removed without pod restart. Cannot have resource limits — a runaway debug session consumes unbounded resources on the node. Requires elevated RBAC permissions (not available to all developers by default).

---

### 🧪 Thought Experiment

**SETUP:**
Your production Java service runs in `gcr.io/distroless/java21-debian12`. A pod is exhibiting elevated garbage collection pauses. You need to attach a JVM profiler to the live process.

**WHAT HAPPENS WITHOUT EPHEMERAL CONTAINERS:**
You must rebuild the image with JVM profiling tools included. This takes 10 minutes. You deploy the debug image — which means restarting the pod and losing the current JVM state (heap contents, live threads, GC state that was causing the issue). The reproduction may not recur in the fresh pod. You have lost the diagnostic window.

**WHAT HAPPENS WITH EPHEMERAL CONTAINERS:**
```bash
kubectl debug -it my-pod \
  --image=eclipse-temurin:21-jdk \
  --target=my-app \  # join PID namespace
  -- bash
```
Inside the ephemeral container, `jps` shows the running JVM. `jstack <pid>` captures thread dumps. `jmap -histo <pid>` shows heap histogram. `jcmd <pid> VM.gc` triggers GC. The live JVM state is captured — the debug container has the JDK tools; the production container has the running JVM. All while the production container continues running without interruption.

**THE INSIGHT:**
Ephemeral containers separate the concern of *running* (distroless, minimal, production-hardened) from *debugging* (full tools, debug JDK, network utilities). You don't have to choose between security and debuggability.

---

### 🧠 Mental Model / Analogy

> An ephemeral container is like a diagnostic probe inserted into a running pipeline. The pipeline (production container) keeps flowing. The probe (ephemeral container) connects to the pipeline at the exact point of interest, measures what it needs, and disconnects. The pipeline never stopped, and the probe brought its own instruments — the pipeline didn't need to have them pre-installed.

Mapping:
- "Pipeline" → production container (distroless, running application)
- "Diagnostic probe" → ephemeral container (full debug image)
- "Connecting to the pipeline" → `setns()` joining pod namespaces
- "Probe's own instruments" → debug tools in the ephemeral container image
- "Pipeline never stopped" → production container continues running
- "Probe disconnects" → ephemeral container exits (`kubectl exec` session ends)

Where this analogy breaks down: once inserted, an ephemeral container cannot be removed without restarting the pod. Unlike a physical probe that you can pull out, the ephemeral container's definition remains in the pod spec until the pod is deleted or restarted.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An ephemeral container is a temporary helper container you can add to a running pod for debugging purposes. It doesn't affect the production container — it just lets you look inside the pod using full debugging tools without stopping the main application.

**Level 2 — How to use it (junior developer):**
Use `kubectl debug` to attach an interactive debug container: `kubectl debug -it <pod-name> --image=ubuntu -- bash`. This starts a bash shell in a container that shares the pod's network. From there you can `curl` to other services, run `nslookup` for DNS debugging, install tools with `apt`. Use `--target=<container-name>` to also share the PID namespace and see the production container's processes.

**Level 3 — How it works (mid-level engineer):**
`kubectl debug` patches the pod's `ephemeralContainers` field via a dedicated API endpoint. The kubelet receives the update through its normal pod sync loop. containerd starts the ephemeral container using `setns()` to join the specified namespaces — network namespace always (same as pod), PID namespace only when `--target` is specified. The ephemeral container's lifecycle is: `running → completed/error`. It is not restarted via `restartPolicy` — once it exits, it stays terminated. Its status is visible in `kubectl describe pod` under `Ephemeral Containers`.

**Level 4 — Why it was designed this way (senior/staff):**
The non-restartable and non-removable design of ephemeral containers is intentional. Automatic restart would make them permanent, violating the "ephemeral" intent. The inability to remove them (without pod restart) is a limitation of the Kubernetes API design, not a deliberate choice — the pod spec is immutable post-creation in most fields. The `--target` flag for PID namespace sharing is critical: without it, you can see the network but not the processes. This separation respects the principle of least privilege — not all debug sessions need process introspection. Resource limits are intentionally excluded because ephemeral containers are interactive, ad-hoc sessions — static resource limits would interfere with legitimate debug operations (e.g., heap dumps requiring 4GB temporary disk).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│        Ephemeral Container Creation Flow                 │
├──────────────────────────────────────────────────────────┤
│  kubectl debug -it my-pod                                │
│    --image=ubuntu:22.04                                  │
│    --target=my-app                                       │
│       ↓                                                  │
│  kubectl: PATCH pods/my-pod/ephemeralcontainers          │
│  (JSON patch: add ephemeral container spec)              │
│       ↓                                                  │
│  kube-apiserver: validates, persists to etcd             │
│       ↓                                                  │
│  kubelet (on pod's node): detects spec change            │
│  kubelet: calls CRI (containerd):                        │
│    → pull ubuntu:22.04                                   │
│    → create container in pod's cgroup                    │
│    → setns(): join pod's network namespace               │
│    → setns(): join my-app's PID namespace (--target)    │
│       ↓                                                  │
│  Ephemeral container: running bash shell                 │
│  (sees pod's network + my-app's processes)               │
│       ↓                                                  │
│  Developer exits session                                 │
│       ↓                                                  │
│  Ephemeral container: terminated (NOT restarted)         │
│  Pod: continues running (unchanged)                      │
└──────────────────────────────────────────────────────────┘
```

**Namespace visibility matrix:**

| Capability Inside Ephemeral Container | Without `--target` | With `--target` |
|---|---|---|
| See pod's network traffic (`tcpdump`) | Yes | Yes |
| See production container processes (`ps`) | No | Yes |
| Attach to production process (`strace`, `jstack`) | No | Yes |
| Access production container's filesystem | No (separate mount ns) | No (separate mount ns) |
| Run network tools (`curl`, `nslookup`, `netstat`) | Yes | Yes |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Production pod running (distroless Java app)
  ↓
Developer: kubectl debug -it <pod> --image=eclipse-temurin:21-jdk
                         --target=myapp
  ↓
ephemeral container spec patched ← YOU ARE HERE
  ↓
kubelet → containerd: setns() into pod namespaces
  ↓
debug container running alongside production
  ↓
developer runs: jstack <pid>, tcpdump, curl
  ↓
developer exits
  ↓
ephemeral container: Terminated (pod unaffected)
```

**FAILURE PATH:**
```
ephemeral container fails to start:
  → containerd: image pull failure (registry unreachable)
  → kubectl reports: "error creating ephemeral container"
  → pod continues running normally (unaffected)

ephemeral container consumes excessive resources:
  → no limits → can starve other containers on node
  → fix: time-limit debug sessions + terminate when done
```

**WHAT CHANGES AT SCALE:**
In large clusters, granting all developers the RBAC permission to create ephemeral containers is a security risk — the ephemeral container can join PID namespaces of production processes. Organisations implement RBAC policies so only SRE/on-call engineers have `pods/ephemeralcontainers` create permission. At scale, ephemeral containers are also used by automated diagnostic tools (runbooks that auto-attach to misbehaving pods).

---

### 💻 Code Example

**Example 1 — Basic network debugging:**
```bash
# Attach a network-debug container to a running pod
# (shares network namespace — no --target needed for network)
kubectl debug -it my-pod \
  --image=nicolaka/netshoot \
  -- bash

# Inside: full network tools available
tcpdump -i eth0 -w /tmp/capture.pcap
netstat -tlnp
nslookup my-service.default.svc.cluster.local
curl http://other-service/health
```

**Example 2 — JVM debugging (with PID namespace sharing):**
```bash
# --target joins the PID namespace of the named container
kubectl debug -it my-java-pod \
  --image=eclipse-temurin:21-jdk \
  --target=my-app \
  -- bash

# Inside: see the production JVM
jps -v          # list JVM processes
jstack <pid>    # thread dump
jmap -histo <pid>  # heap histogram
jcmd <pid> GC.run  # trigger GC
```

**Example 3 — Copy-pod technique for filesystem access:**
```bash
# Ephemeral containers don't share mount namespace
# To inspect production filesystem, copy the pod with a debug image
kubectl debug my-pod \
  --copy-to=my-pod-debug \
  --image=ubuntu \
  --container=my-app \
  -- bash
# This creates a NEW pod copying the spec but replacing the image
# WARNING: this is a different pod, not the live production pod
```

**Example 4 — Check ephemeral container status:**
```bash
# View all containers including ephemeral
kubectl describe pod my-pod | grep -A20 "Ephemeral Containers"

# Get ephemeral container logs after it exits
kubectl logs my-pod -c debugger-abc123

# List all ephemeral containers via JSON path
kubectl get pod my-pod \
  -o jsonpath='{.spec.ephemeralContainers[*].name}'
```

---

### ⚖️ Comparison Table

| Approach | Requires Restart | Image Requirements | Namespace Access | Production Risk |
|---|---|---|---|---|
| **Ephemeral Container** | No | Any image | Network + PID (opt) | Low (no restart) |
| `kubectl exec` | No | Tools in image | Pod namespaces | None (existing container only) |
| Debug image rebuild | Yes | Debug tools baked in | Full | Medium (restart loses state) |
| Node SSH + nsenter | No | Any (host tools) | Full (all namespaces) | High (node-level access) |
| Copy pod with debug image | Yes (new pod) | Any image | Full | Low (separate pod) |

How to choose: Ephemeral containers are the correct tool for debugging live production pods with minimal images. `kubectl exec` works when the production image has the needed tools. Copy-pod is for when you need full filesystem access and can tolerate a separate pod without live state.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Ephemeral containers can be removed when done" | No — once added, the ephemeral container definition stays in the pod spec. It can exit, but cannot be removed. The pod must be deleted/restarted to clear it. |
| "Ephemeral containers can access the production container's filesystem" | By default, no — they have separate mount namespaces. Use `--target` for PID namespace; for filesystem, use the copy-pod debug technique. |
| "Ephemeral containers are available in all Kubernetes versions" | They became stable in Kubernetes 1.23 (2021). Older clusters may have them as alpha/beta with different APIs. Always check your cluster version. |
| "Any developer should be able to create ephemeral containers" | Creating ephemeral containers is a privileged operation (can join production PID namespaces). Restrict via RBAC to on-call/SRE roles only. |
| "Ephemeral containers affect the production container" | No — the production container continues running unmodified. Ephemeral containers share namespaces (read/observe) but do not modify the production container. They do compete for node resources if unconstrained. |

---

### 🚨 Failure Modes & Diagnosis

**Ephemeral container cannot attach (PID namespace sharing fails)**

**Symptom:**
`kubectl debug --target=myapp` fails or the ephemeral container starts but `ps aux` shows no production processes.

**Root Cause:**
The pod is not using `shareProcessNamespace: true` or the `--target` flag was not used. Or the kubelet version is too old for ephemeral container PID namespace joining.

**Diagnostic Command / Tool:**
```bash
# Check if process namespace sharing is enabled in pod spec
kubectl get pod my-pod -o jsonpath='{.spec.shareProcessNamespace}'

# Check kubelet/K8s version
kubectl version
```

**Fix:**
Use `--target=<container-name>` in the `kubectl debug` command to explicitly join the target container's PID namespace. Ensure Kubernetes 1.23+.

**Prevention:**
Document the correct `kubectl debug` command in runbooks for each service.

---

**Ephemeral container consumes excessive node resources**

**Symptom:**
Node CPU/memory spikes after engineer runs `kubectl debug`. Other pods on the same node experience degraded performance. OOM events occur.

**Root Cause:**
Ephemeral containers cannot have resource limits (by design). An engineer running a large operation (heap dump, tcpdump to file) can exhaust node resources.

**Diagnostic Command / Tool:**
```bash
kubectl top pods --all-namespaces
kubectl describe node <node> | grep -A10 "Allocated resources"
```

**Fix:**
Terminate the ephemeral container session immediately. Consider evicting the pod if node is overloaded.

**Prevention:**
Brief debug sessions only. Use `timeout` in debug commands. For long-running diagnostics, use the copy-pod technique on a dedicated debug node with resource limits.

---

**RBAC: user not permitted to create ephemeral containers**

**Symptom:**
`kubectl debug` returns `Error from server (Forbidden): pods "my-pod" is forbidden: cannot use ephemeralcontainers`.

**Root Cause:**
The user's RBAC role does not include `pods/ephemeralcontainers` verb `create`.

**Diagnostic Command / Tool:**
```bash
# Check RBAC permission
kubectl auth can-i create pods/ephemeralcontainers --namespace production

# View current role bindings
kubectl get rolebindings -n production
```

**Fix:**
```yaml
# RBAC Role for on-call debugging
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ephemeral-debugger
rules:
- apiGroups: [""]
  resources: ["pods/ephemeralcontainers"]
  verbs: ["create", "get", "patch"]
```

**Prevention:**
Pre-configure on-call RBAC roles with ephemeral container permissions. Standard developer roles should not include this permission.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Pod` — ephemeral containers are added to pods; understand pod structure and namespaces first
- `Linux Namespaces` — ephemeral container visibility is based on namespace sharing via `setns()`
- `Kubernetes Architecture` — understand kubelet and CRI to know how ephemeral containers are created

**Builds On This (learn these next):**
- `Distroless Images` — ephemeral containers solve the distroless debugging problem; use them together
- `Container Security` — ephemeral container RBAC is a critical security control
- `Kubernetes Architecture` — kubelet implements ephemeral container lifecycle management

**Alternatives / Comparisons:**
- `Init Container` — runs before the main container starts (not for debugging); different lifecycle, different purpose
- `Sidecar Container` — permanent companion container in a pod; not ephemeral; different use case
- `Container Health Check` — proactive health monitoring vs reactive debugging with ephemeral containers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Temporary debug container injected into   │
│              │ running pod without restart               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Distroless/minimal images have no debug   │
│ SOLVES       │ tools; can't debug without restarting     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Linux setns() lets any process join       │
│              │ existing namespaces — no restart needed   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Live production debugging of pods with    │
│              │ minimal/distroless images                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ You need filesystem access (use copy-pod) │
│              │ or need a permanent companion (use sidecar│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Live-state debugging vs no resource limits│
│              │ + stays in pod spec after exit            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A parachute for your distroless pods:    │
│              │  bring your own tools, touch nothing"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distroless Images → Init Container →      │
│              │ Sidecar Container                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Ephemeral containers share the pod's network namespace but have a separate mount (filesystem) namespace by default. If a production container writes temporary data to `/tmp` that is critical for diagnosing the current issue, trace step-by-step why your ephemeral container cannot see this data, what the precise namespace boundary prevents, and design a workaround that does not require restarting the production pod.

**Q2.** Your organisation adopts a security policy: "ephemeral container creation in production namespaces requires two-person approval via a workflow system." Considering that debugging incidents are often time-sensitive (P0 SEV-1), design an RBAC and workflow model that enforces the two-person rule while reducing the approval time during incidents to under 60 seconds. What are the security trade-offs of any "break-glass" emergency access mechanism you propose?

