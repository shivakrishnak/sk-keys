---
id: CTR-051
title: "Container Security Research (Rootless, gVisor)"
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-017, CTR-021, CTR-044
used_by: CTR-054
related: CTR-044, CTR-049
tags:
  - containers
  - security
  - deep-dive
  - advanced
  - first-principles
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /ctr/container-security-research-rootless-gvisor/
---

# CTR-051 - Container Security Research (Rootless, gVisor)

⚡ TL;DR - Rootless containers (user namespaces) and gVisor (user-space kernel) are complementary advanced isolation techniques: rootless eliminates host root privilege; gVisor reduces kernel attack surface - together they provide defense-in-depth beyond standard securityContext controls.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-017, CTR-021, CTR-044 |     |
| **Used by:**    | CTR-054                  |     |
| **Related:**    | CTR-044, CTR-049         |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Standard container security (non-root user, dropped capabilities,
seccomp) reduces attack surface but does not fundamentally change the
threat model: containers still run on the host kernel, and root inside
a container (even with `runAsNonRoot: true` at the pod level) can still
become host root via a kernel exploit. The security baseline is a
reduction of risk, not a change of trust boundary.

**THE BREAKING POINT:**
A container escape CVE is disclosed. The attack vector requires the
container to be running as root (UID 0) or to have the `SYS_PTRACE`
capability. Standard security hardening (non-root + dropped capabilities)
blocks this specific CVE. But the next CVE might not require these
preconditions. Teams want a more fundamental isolation guarantee.

**THE INVENTION MOMENT:**
Two orthogonal approaches emerged:

1. **Rootless containers** (user namespace isolation): root inside the
   container is mapped to an unprivileged UID on the host. Even if the
   container is fully compromised, the attacker operates as an
   unprivileged user on the host.
2. **gVisor** (kernel interposition): a user-space kernel intercepts
   all syscalls from container processes. The container never directly
   calls the host kernel. A kernel vulnerability requires first
   compromising gVisor's user-space kernel.

**EVOLUTION:**
2013: User namespaces merged into Linux 3.8. 2019: gVisor (runsc) open-
sourced by Google. 2020: Rootless Docker becomes stable. 2021: Rootless
Kubernetes (kubelet in user namespace) becomes feasible. 2022: Kata
Containers 3.0 improves startup performance. 2023: gVisor adds io_uring
support (previously a compatibility gap). Confidential computing
(Kata + AMD SEV/Intel TDX) provides hardware-attested isolation.

---

### 📘 Textbook Definition

**Rootless containers** use Linux user namespaces to run container
runtimes and containers without any host root privilege. The container
runtime daemon (Podman, rootless Docker, rootless containerd) runs as
an unprivileged user; root (UID 0) inside the container maps to the
user's UID on the host via the user namespace UID mapping.

**gVisor** is a user-space kernel that intercepts syscalls made by
container processes and implements them in user space, reducing the
attack surface of the host kernel. Container processes communicate with
gVisor's Sentry (the kernel implementation) rather than directly with
the host kernel. Sentry makes a minimal set of host syscalls on behalf
of the container.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Rootless containers remove host root privilege; gVisor removes direct
host kernel access - each adds an independent isolation layer.

**One analogy:**

> Standard containers are like renting a flat with a shared building
> entrance (host kernel). Rootless containers give each tenant their
> own locked entrance (user namespace: even if a tenant breaks in, they
> are still just a tenant, not the building manager). gVisor is like
> adding an airlock between the flat and the building (syscall interposition:
> the tenant must go through the airlock, which screens all requests
> before they reach the building systems).

**One insight:**
Rootless and gVisor are orthogonal: rootless protects host privilege
escalation; gVisor protects kernel vulnerability exploitation. Using
both together means: (1) even if gVisor is bypassed, the attacker is
an unprivileged host user (rootless); (2) even if the container escapes
the user namespace, gVisor's syscall filter limits what it can do.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **User namespaces map UID 0 inside to non-0 outside** - root in a
   rootless container is a fully unprivileged user on the host. This
   is the key security property: privilege escalation from inside the
   container cannot gain host root.
2. **gVisor interposes on the syscall interface** - all syscalls from
   the container go to gVisor's Sentry (a Go process in user space).
   Sentry implements the Linux ABI and makes selective host syscalls.
   A kernel CVE must first compromise Sentry before reaching the host.
3. **Rootless containers have reduced capability** - user namespace
   containers cannot bind to privileged ports (<1024), cannot change
   host network configuration, and have limited access to devices.
   These limitations are the security/capability trade-off.
4. **gVisor has syscall compatibility gaps** - not all Linux syscalls
   are implemented in gVisor's Sentry. Applications using unimplemented
   syscalls fail. `io_uring`, `ptrace`, and some `inotify` variants
   have had compatibility issues historically.

**DERIVED DESIGN:**
Given invariant 1: rootless containers are appropriate for any workload
where host root privilege is not required (which is almost all
application workloads). Given invariant 4: test application compatibility
with gVisor before production deployment. Maintain a compatibility matrix.

**THE TRADE-OFFS:**
**Gain (rootless):** Host root privilege eliminated. Even a container
escape results in an unprivileged host user, not root.
**Cost (rootless):** Network namespace setup requires `newuidmap`/
`newgidmap` helper binaries (setuid). Some host device access unavailable.
**Gain (gVisor):** Kernel attack surface reduced to Sentry's syscall
implementation. Two-layer defense.
**Cost (gVisor):** 10-30% CPU overhead per syscall. Startup latency.
Compatibility gaps with some applications.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The isolation mechanisms (user namespace UID mapping,
syscall interposition) are genuinely novel kernel/user-space boundaries.
**Accidental:** Performance overhead of gVisor for workloads that do
not need kernel-level isolation.

---

### 🧪 Thought Experiment

**SETUP:**
A platform runs untrusted user code. Standard containers with seccomp
and non-root are deployed. An attacker submits code exploiting a kernel
vulnerability that works when called from a container with UID 0.

**WHAT HAPPENS WITHOUT ROOTLESS/GVISOR:**
The seccomp profile blocks most dangerous syscalls, but the vulnerability
is exploitable via a syscall that the seccomp profile permits (it was
not known to be dangerous when the profile was written). The attacker
gains kernel privileges and escapes to the host as root.

**WHAT HAPPENS WITH ROOTLESS + GVISOR:**
Layer 1 (gVisor): the syscall goes to gVisor's Sentry, not the host
kernel. The vulnerability is in the host kernel, not in Sentry. If
Sentry passes the syscall through (not all syscalls are intercepted),
it is a host syscall from an unprivileged process (not kernel context).
Layer 2 (rootless): even if Sentry is compromised, the container process
is mapped to an unprivileged UID on the host. Host root privilege is
not available to the attacker.

**THE INSIGHT:**
Layered isolation degrades gracefully. Each layer must be independently
defeated. The combination does not prevent all attacks but requires
an attacker to find and exploit two independent isolation mechanisms
rather than one. Defense-in-depth is the goal, not perfect isolation.

---

### 🧠 Mental Model / Analogy

> Imagine a secure document handling room. Standard container security
> is like working in a room with a locked door (namespaces + seccomp).
> Rootless containers add that even if you break out of the room, you
> are still just an ordinary staff member with no building keys (no host
> root privilege). gVisor adds a document shredder between the room
> and the filing system: all document requests go through a verifier
> that screens requests before they reach the actual files (syscall
> interposition).

Element mapping:

- **Locked room** = standard namespace isolation
- **Ordinary staff member** = unprivileged UID (rootless)
- **Building keys** = host root privilege
- **Document shredder/verifier** = gVisor Sentry
- **Filing system** = host kernel

Where this analogy breaks down: in the physical world, breaking out
of a room grants immediate access to the hallway; in containers, a
namespace escape still requires defeating additional isolation layers.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Rootless containers run without needing system administrator privileges
on the host. gVisor adds an extra layer of protection between the
container and the computer's core operating system.

**Level 2 - How to use it (junior developer):**
For rootless Docker: `dockerd-rootless-setuptool.sh install` on the
host. Then use Docker normally. For rootless Kubernetes: use KIND with
rootless mode, or Podman in rootless mode.
For gVisor: install `runsc`, create a RuntimeClass, set
`runtimeClassName: gvisor` on pods that need sandboxed execution.

**Level 3 - How it works (mid-level engineer):**
Rootless: the container runtime (Podman, rootless containerd) starts
as a regular user. It creates a user namespace where UID 0 maps to the
current user's UID (e.g., 1000 on the host). Inside the namespace, the
runtime has full privileges (root in namespace). Outside, it is just
UID 1000. Network namespaces require `slirp4netns` or `pasta` for
userspace networking (no host network privilege needed).
gVisor: the container process communicates via a socket to the `runsc`
process (Sentry). Sentry implements the Linux ABI in Go, translating
container syscalls to a minimal set of host syscalls via a separate
sandbox process (Gofer). The host kernel is called only by Gofer with
a highly restricted seccomp filter.

**Level 4 - Why it was designed this way (senior/staff):**
Rootless containers address the daemon-privilege problem: Docker daemon
running as root is a high-value attack target. Any vulnerability in the
Docker daemon gives the attacker host root. By running the daemon as
an unprivileged user, the attack surface shifts: the daemon can still
be compromised, but the attacker is limited to the user's permissions.
gVisor addresses the kernel surface problem: the Linux kernel has 350+
syscalls, each a potential vulnerability surface. gVisor's Sentry
implements only the syscalls containers actually need, reducing the
host kernel surface accessible from container code to a small set of
well-audited paths.

**Expert Thinking Cues:**

- "Does this workload need host root for any reason? If no, rootless
  should be the default."
- "Does this workload use syscalls that gVisor does not implement?
  Run compatibility tests before committing to gVisor in production."
- "What is the performance overhead of gVisor for this specific workload?
  I/O-intensive and syscall-heavy workloads see higher overhead."

---

### ⚙️ How It Works (Mechanism)

**ROOTLESS CONTAINER UID MAPPING:**

```
Host UID: 1000 (alice)
  |
  v
User namespace created by rootless runtime
  UID mapping: 0 (container root)  -> 1000 (host)
               1 (container user)  -> 100001 (host)
               ...
  |
  v
Inside container: ps shows UID 0 (root)
On host:         ps shows UID 1000 (alice)
File written as  container UID 0
  -> stored on host filesystem as UID 1000
```

**GVISOR SYSCALL PATH:**

```
Container process (e.g. nginx)
  | syscall: read(fd, buf, size)
  v
gVisor Sentry (user-space kernel, Go)
  | Sentry handles the read in user space
  | OR delegates to Gofer (for file I/O)
  v
Gofer process (file system proxy)
  | Gofer makes host syscall: read(fd, buf, size)
  | Gofer has restrictive seccomp filter
  v
Host kernel (minimal attack surface)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (gVisor container start):**

```
Kubelet -> CRI call to containerd
  |
  v
containerd: RuntimeClass = gvisor
  -> invoke runsc (gVisor OCI runtime)
  |           ← YOU ARE HERE
  v
runsc creates Sentry + Gofer processes
  |
  v
Container process starts
  | All syscalls -> Sentry (not host kernel)
  v
Sentry handles or forwards to Gofer
  |
  v
Gofer -> host kernel (restricted interface)
```

**FAILURE PATH:**
Container application uses `io_uring` for high-performance I/O. gVisor
does not implement `io_uring` in older versions. Application crashes
with `ENOSYS` (function not implemented). Falls back to standard
`read`/`write` if the application has a fallback path; otherwise fails.

**WHAT CHANGES AT SCALE:**
At scale, gVisor overhead accumulates. For a service making 100,000
syscalls/second (network-intensive), 15% overhead = 15,000 extra
syscalls/second intercepted by Sentry. Monitor CPU utilisation relative
to standard containerd. Use gVisor only where the security benefit
justifies the overhead.

---

### 💻 Code Example

```bash
# Set up rootless Docker (no sudo required after setup)
curl -fsSL https://get.docker.com/rootless | sh
# OR on systems with systemd:
dockerd-rootless-setuptool.sh install
systemctl --user start docker

# Verify rootless mode
docker info | grep "rootless"
# Security Options: rootless

# Run a container - daemon runs as current user
docker run --rm ubuntu id
# uid=0(root) gid=0(root) - root inside container
# But on host:
ps aux | grep dockerd
# dockerd is running as current user UID, not root
```

```yaml
# gVisor RuntimeClass configuration
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc    # gVisor OCI runtime binary name

---
# Pod using gVisor (sandboxed runtime)
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-workload
spec:
  runtimeClassName: gvisor
  containers:
  - name: app
    image: myapp:v1.0
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      readOnlyRootFilesystem: true
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
```

```bash
# Verify gVisor is intercepting syscalls
# (inside a gVisor container, dmesg shows gVisor kernel)
kubectl exec -it sandboxed-workload -- dmesg 2>/dev/null | \
  grep -i "gvisor\|runsc"
# Should show gVisor kernel messages, not Linux kernel messages

# Performance comparison (syscall overhead)
# Standard runc:
time kubectl run bench-runc --image=nginx \
  --restart=Never --rm -- \
  sh -c 'for i in $(seq 1 10000); do echo $i > /dev/null; done'

# gVisor:
time kubectl run bench-gvisor --image=nginx \
  --restart=Never --rm \
  --overrides='{"spec":{"runtimeClassName":"gvisor"}}' -- \
  sh -c 'for i in $(seq 1 10000); do echo $i > /dev/null; done'
```

**How to test / verify correctness:**

```bash
# Test rootless: verify runtime is not running as root
systemctl --user status docker | grep "UID\|uid"

# Test gVisor: run gVisor test suite
docker run --runtime=runsc \
  gcr.io/gvisor/ubuntu:latest /bin/true
echo "Exit: $?"  # 0 = gVisor working

# Test application compatibility with gVisor
# Run your application's test suite with gVisor runtime
kubectl run compat-test --image=myapp \
  --restart=Never \
  --overrides='{"spec":{"runtimeClassName":"gvisor"}}' \
  -- /app/run-tests.sh
kubectl logs compat-test
```

---

### ⚖️ Comparison Table

| Technique | Host Root Required | Kernel Attack Surface | Compatibility | Overhead |
|---|---|---|---|---|
| Standard containerd + seccomp | Yes (daemon) | Full (all syscalls) | Full | <1% |
| Rootless containerd | No | Full (all syscalls) | ~Full (some device limits) | <5% |
| gVisor (runsc) | Yes (daemon) | Minimal (Sentry-filtered) | Partial (syscall gaps) | 10-30% CPU |
| Rootless + gVisor | No | Minimal | Partial | 15-35% CPU |
| Kata Containers | Yes (daemon) | None (own kernel) | Full (VM kernel) | 100-200ms start |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Rootless containers cannot run as root inside the container" | Rootless containers can run processes as UID 0 inside the container - that's the point of the user namespace mapping. Root inside = unprivileged user outside. |
| "gVisor provides the same isolation as Kata Containers" | gVisor shares the host kernel (via Gofer's restricted syscall set). Kata Containers runs a full VM with a separate Linux kernel. Kata provides stronger isolation at higher overhead. |
| "Rootless containers have the same network capabilities as root-daemon containers" | Rootless containers use userspace networking (slirp4netns or pasta) which has slightly higher latency and cannot use raw sockets or some advanced networking features. |
| "gVisor is a VM" | gVisor is a user-space process implementing the Linux kernel ABI. It shares the host kernel for its own system calls. A VM has a separate kernel and hardware virtualisation. |
| "Rootless + gVisor together provide VM-level isolation" | They provide complementary software isolation: rootless removes host root privilege, gVisor reduces kernel attack surface. Neither individually nor together do they provide hardware-enforced VM isolation (which requires a hypervisor). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: gVisor Application Incompatibility**
**Symptom:** Application runs correctly with standard containerd but
crashes with `ENOSYS` or unexpected errors when switched to gVisor.
**Root Cause:** Application uses a Linux syscall not implemented by
gVisor's Sentry. Common culprits: `io_uring`, `ptrace` (debugging tools),
`userfaultfd`, some `inotify` variants, `splice` for certain use cases.
**Diagnostic:**

```bash
# Run gVisor with debug logging to capture syscall errors
kubectl run debug --image=myapp \
  --overrides='{
    "spec": {
      "runtimeClassName": "gvisor",
      "containers": [{
        "name": "debug",
        "image": "myapp",
        "env": [{"name": "RUNSC_DEBUG", "value": "1"}]
      }]
    }
  }'
kubectl logs debug 2>&1 | grep -i "unsupported\|ENOSYS"
```

**Fix:** If the syscall is `io_uring`: upgrade gVisor (io_uring support
added in 2023). If the syscall is essential and not supported: use Kata
Containers instead (full kernel compatibility).
**Prevention:** Run application compatibility tests against gVisor in
staging before production adoption. Maintain a compatibility matrix
by application type (database: avoid gVisor; stateless API: usually
compatible).

---

**Failure Mode 2: Rootless Container Network Performance Degradation**
**Symptom:** Rootless containers have measurably higher network latency
(5-15% compared to root-daemon containers). High-throughput network
workloads show reduced throughput.
**Root Cause:** Rootless containers use userspace networking (slirp4netns
or pasta) which routes packets through a userspace process rather than
the kernel directly. Each packet crosses the kernel/userspace boundary.
**Diagnostic:**

```bash
# Compare network latency
# Root-daemon container:
docker run --rm networkstatic/iperf3 iperf3 -c iperf.example.com

# Rootless container:
DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock \
  docker run --rm networkstatic/iperf3 iperf3 -c iperf.example.com

# Compare throughput values
```

**Fix:** For network-intensive workloads: use standard root-daemon
containerd with enhanced securityContext rather than rootless. Rootless
is appropriate for CPU-bound or low-network workloads.
**Prevention:** Benchmark network-sensitive workloads against both
rootless and root-daemon before production deployment.

---

**Failure Mode 3: User Namespace Breakout via SetUID Binary (Security)**
**Symptom:** Security audit finds a setuid binary inside a rootless
container's image. If executed, it runs as UID 0 inside the user
namespace (which is an unprivileged UID outside).
**Root Cause:** Rootless containers allow setuid binaries to escalate
to UID 0 inside the user namespace. While this is "root inside a
user namespace" (not host root), it grants full namespace-level
capabilities.
**Diagnostic:**

```bash
# Find setuid binaries inside an image
docker export $(docker create myapp:v1.0) | \
  tar -t --full-time | \
  awk '{if ($1 ~ /s/) print $NF}'

# Alternative: use dive to inspect each layer
dive myapp:v1.0 | grep -i "setuid\|suid"
```

**Fix:** Remove setuid binaries from production images. Use distroless
images (no setuid binaries by design). In Kubernetes, set
`allowPrivilegeEscalation: false` to prevent setuid escalation.
**Prevention:** Scan images for setuid binaries in CI. Block images
with setuid binaries via admission policy (Kyverno or OPA).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-017 - Linux Namespaces]] - user namespaces (the rootless mechanism)
- [[CTR-021 - Container Security]] - baseline container security
- [[CTR-044 - Container Security Architecture]] - defense-in-depth framework

**Builds On This (learn these next):**

- [[CTR-054 - Container Security Mental Model]] - threat model thinking

**Alternatives / Comparisons:**

- [[CTR-044 - Container Security Architecture]] - standard security controls
- [[CTR-049 - Linux Namespace and Cgroup Architecture]] - the underlying mechanism

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Advanced isolation: rootless+gVisor │
│ PROBLEM     │ Standard controls don't change trust │
│ KEY INSIGHT │ Rootless: no host root. gVisor: no  │
│             │ direct kernel access.                │
│ USE WHEN    │ Multi-tenant, untrusted code, regs  │
│ AVOID WHEN  │ Network-intensive (rootless perf) or│
│             │ syscall-heavy (gVisor compat)        │
│ TRADE-OFF   │ Isolation vs. performance + compat  │
│ ONE-LINER   │ Rootless + gVisor = defense layers  │
│ NEXT EXPLORE│ CTR-054 Security Mental Model       │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Rootless containers map container root (UID 0) to an unprivileged
   host UID via user namespaces - a full container escape gives the
   attacker only unprivileged host access.
2. gVisor interposes on syscalls in user space - the host kernel is
   not directly accessible from container code, adding a two-layer
   buffer against kernel exploits.
3. Rootless and gVisor are orthogonal and complementary - use both
   for maximum isolation; either alone covers different attack vectors.

**Interview one-liner:**
"Rootless containers use user namespace UID mapping to eliminate host
root privilege (escape = unprivileged host user); gVisor uses a user-
space kernel to intercept all syscalls (escape = gVisor compromise
first, then host kernel); together they provide defense-in-depth beyond
standard securityContext controls."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Defense-in-depth security layers should be orthogonal (protecting
different attack vectors) rather than redundant (protecting the same
vector twice). Rootless containers protect privilege escalation; gVisor
protects kernel surface exposure. Neither duplicates the other. Each
layer degrades an attacker's capabilities independently.

**Where else this pattern appears:**

- **Network security zones:** DMZ (limits external access), firewall
  (limits traffic type), IDS (detects anomalous traffic), and endpoint
  security (limits host privilege). Each layer addresses a different
  attack phase.
- **Database access control:** Network-level firewall (IP whitelisting),
  database authentication, role-based access control (schema level),
  and row-level security. An attacker who compromises one layer is
  constrained by the others.
- **Cryptographic protocol design:** TLS provides: certificate
  authentication (prevents MITM), symmetric encryption (prevents
  eavesdropping), and MAC (prevents tampering). Three orthogonal
  protections in one protocol.

---

### 💡 The Surprising Truth

gVisor's Sentry is written in Go, a garbage-collected language, running
as a user-space process that implements a Linux kernel. Every time a
container process makes a system call, it is handled by a Go goroutine
with garbage collection pauses. For most workloads, GC pauses are
imperceptible (<1ms). But for latency-sensitive workloads (trading
systems, real-time audio), GC pauses can cause tail latency spikes.
Google measured that gVisor's GC pauses cause p99.9 latency increases
of 2-5ms for syscall-heavy workloads. This is the hidden cost of
implementing a kernel in a GC language, and it is one of the reasons
gVisor is not recommended for latency-sensitive production workloads
despite its security benefits.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A platform team is choosing between
(a) standard containerd with strict seccomp + AppArmor profiles for
untrusted workloads, and (b) gVisor with default seccomp. Both aim to
limit the kernel attack surface. What are the trade-offs, and under
what threat model is each approach better?
*Hint:* seccomp + AppArmor is a policy-based approach (allowlist of
allowed syscalls/kernel actions). gVisor is an architecture-based
approach (user-space kernel interposition). What happens when a new
unknown-dangerous syscall is added to the Linux kernel? Which approach
adapts automatically?

**Q2 (E - First Principles):** In rootless containers, UID 0 inside
the user namespace maps to UID 100000 on the host. A container process
running as UID 0 creates a file. The file appears as UID 0 inside the
container and UID 100000 on the host. Now a second container (also
rootless, different user namespace) tries to read that file. Can it?
Why or why not?
*Hint:* File permissions are stored as host UIDs on the filesystem.
The second container has a different UID mapping (its UID 0 maps to
a different host UID, e.g. 200000). The file is owned by 100000 on
the host. From the second container's perspective, that is an unknown
UID with default permissions. What does the `other` permission bit
determine?

**Q3 (B - Scale):** A platform runs 1,000 gVisor containers. Each
Sentry process (per container) consumes approximately 50 MB of resident
memory overhead. What is the total memory overhead from gVisor Sentry
processes alone, and how does this compare to the memory overhead of
1,000 Kata Container VMs (each consuming ~128 MB for the VM kernel)?
*Hint:* Calculate both totals. Then consider: at what container count
does the memory overhead justify moving to a shared-kernel model (standard
containerd) with enhanced seccomp, vs. maintaining per-container Sentry
processes? What metric determines the crossover point?