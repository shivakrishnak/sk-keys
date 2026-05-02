---
layout: default
title: "Container Security"
parent: "Containers"
nav_order: 834
permalink: /containers/container-security/
number: "0834"
category: Containers
difficulty: ★★★
depends_on: Linux Namespaces, Cgroups, Docker, Container, Volume Mounts
used_by: Image Scanning, Distroless Images, Container Runtime Interface (CRI), Container Orchestration
related: Linux Namespaces, Cgroups, Image Scanning, Distroless Images, Container Resource Limits
tags:
  - containers
  - security
  - docker
  - advanced
  - production
---

# 834 — Container Security

⚡ TL;DR — Container security hardens running containers against exploitation by limiting capabilities, dropping privileges, enforcing non-root execution, restricting syscalls, and scanning images for vulnerabilities.

| #834 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Linux Namespaces, Cgroups, Docker, Container, Volume Mounts | |
| **Used by:** | Image Scanning, Distroless Images, Container Runtime Interface (CRI), Container Orchestration | |
| **Related:** | Linux Namespaces, Cgroups, Image Scanning, Distroless Images, Container Resource Limits | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Node.js container runs as root (the default). It has access to all Linux capabilities. The application has a remote code execution vulnerability — an attacker injects a command. Because the container runs as root and has `CAP_NET_ADMIN`, the attacker can: modify iptables rules on the host, access host network interfaces, read sensitive files in other containers' host paths. With `CAP_SYS_PTRACE`, they can attach to other processes on the host. The "container isolation" is a checkbox, not a security boundary.

**THE BREAKING POINT:**
The default Docker configuration is designed for convenience, not security: root user, full Linux capabilities, no syscall restrictions, no read-only filesystem. For production, each of these defaults must be explicitly hardened because each represents a privilege escalation pathway.

**THE INVENTION MOMENT:**
This is exactly why container security practices were formalised — a defence-in-depth approach that applies the principle of least privilege at every layer: image, runtime, capabilities, syscalls, network, and storage.

---

### 📘 Textbook Definition

**Container security** is the set of practices, configurations, and enforcement mechanisms that reduce the risk of a containerised workload being exploited or of a compromised container affecting the host or other containers. It applies the principle of least privilege across six attack surfaces: (1) **Image security** — using minimal base images, scanning for CVEs, never embedding secrets; (2) **Runtime privileges** — running as non-root UID, dropping Linux capabilities; (3) **Syscall filtering** — using seccomp profiles to allow only required syscalls; (4) **Mandatory access control** — AppArmor/SELinux profiles restricting filesystem and network access; (5) **Network policy** — restricting inter-service communication to only required paths; (6) **Resource limits** — preventing resource exhaustion attacks via cgroup limits.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Container security is applying least-privilege at every layer — non-root user, minimal image, restricted capabilities, filtered syscalls — so an exploited container cannot become a host compromise.

**One analogy:**
> Container security is like a prison cell with multiple layers of restraint. The cell walls (namespaces) provide isolation. The ankle monitor (seccomp) prevents certain activities. The guard restrictions (Linux capabilities) limit what the prisoner can reach for. A uniform search on entry (image scanning) ensures no contraband entered. Even if the prisoner picks the cell lock, the ankle monitor and guards limit what they can do. Each layer is designed assuming the previous one might fail.

**One insight:**
The most important single change for container security is running as a non-root user (`USER 1000` in Dockerfile). A process running as UID 1000 inside a container that has a container escape vulnerability lands as UID 1000 on the host — still potentially dangerous, but massively constrained compared to landing as UID 0 (root) with unrestricted host access.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A container is a process — if it runs with high privileges, exploitation = high-privilege host access.
2. Defence-in-depth: assume each security layer will be breached; each subsequent layer must still constrain the attacker.
3. Least privilege: grant only the specific permissions the application needs; deny everything else.

**DERIVED DESIGN:**

**Layer 1 — Image Security:**
- Use minimal base images (Alpine, Distroless, Scratch) — fewer packages = smaller CVE surface
- Scan with Trivy, Snyk, or Grype before pushing to registry
- Never `COPY .env` or hardcode secrets — use runtime environment injection
- Use multi-stage builds to exclude build tools from runtime image

**Layer 2 — User / Privilege:**
- `USER 1000` in Dockerfile — non-root UID
- Kubernetes: `securityContext.runAsNonRoot: true`, `runAsUser: 1000`
- Read-only root filesystem: `--read-only` in Docker, `readOnlyRootFilesystem: true` in K8s

**Layer 3 — Linux Capabilities:**
Default Docker capabilities (not exhaustive): `CHOWN`, `DAC_OVERRIDE`, `FSETID`, `FOWNER`, `MKNOD`, `NET_RAW`, `SETGID`, `SETUID`, `SETPCAP`, `NET_BIND_SERVICE`, `SYS_CHROOT`, `KILL`, `AUDIT_WRITE`.
These enable privilege escalation (SETUID, SETGID), raw socket access (NET_RAW useful for DoS and ARP spoofing), and more. Best practice: `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` (or whatever specific caps the app needs).

**Layer 4 — Seccomp:**
Seccomp (secure computing mode) filters which syscalls a process can make. Docker's default seccomp profile blocks ~40 dangerous syscalls (e.g., `ptrace`, `mount`, `pivot_root`). A custom profile for a Node.js web service can allow ~60 syscalls and block the remaining ~300+.

**Layer 5 — AppArmor/SELinux:**
Mandatory Access Control profiles that restrict filesystem paths the container can access, network access, and executable invocation — even if the process gains unexpected privileges.

**THE TRADE-OFFS:**
**Gain:** Compromise blast radius reduced; container escape → limited damage; defence-in-depth.
**Cost:** Security hardening adds configuration complexity; overly restrictive profiles break legitimate application functionality; requires security expertise to implement correctly.

---

### 🧪 Thought Experiment

**SETUP:**
Two containers: Container A (hardened) and Container B (default Docker config). Both have the same remote code execution vulnerability (attacker can run arbitrary shell commands).

**WHAT AN ATTACKER CAN DO IN CONTAINER B (default):**
- Running as root (UID 0)
- Has `CAP_NET_RAW` → can create raw sockets → network sniffing, ARP spoofing
- Has `CAP_SYS_PTRACE` capability (if granted) → can attach to other processes
- No seccomp restrictions → can call `ptrace`, `mount`, `pivot_root`
- No read-only filesystem → can write anywhere mutable in container
- If misconfigured: can access `/proc/sysrq-trigger`, escape via `runc` CVE

**WHAT AN ATTACKER CAN DO IN CONTAINER A (hardened):**
- Running as UID 1000 (non-root)
- ALL capabilities dropped (`--cap-drop=ALL`)
- Only `NET_BIND_SERVICE` re-added (app binds to port 80)
- Seccomp: custom profile allows only ~60 required syscalls
- Read-only root filesystem — cannot modify container files
- Even with container escape: lands as UID 1000 on host, no capabilities

**THE INSIGHT:**
The hardened container dramatically limits what an attacker can accomplish even with arbitrary code execution. Each security layer is an independent constraint. An attacker must bypass all of them — a much harder problem.

---

### 🧠 Mental Model / Analogy

> Container security is like the security model for a bank employee. The employee (container process) enters through a security checkpoint (image scan). Inside, they are limited to their role: a teller (app user) cannot enter the vault (root filesystem), cannot transfer money beyond their daily limit (resource limits), cannot ping other bank addresses (network policy), and every action they perform is logged (seccomp audit). Even if they are compromised (RCE), they cannot access areas beyond their defined scope.

**Mapping:**
- "Employee entry security check" → image scan (CVE check before deployment)
- "Role-based access in bank" → USER directive (non-root), Linux capabilities
- "Cannot enter vault" → read-only root filesystem, volume mounts only for needed paths
- "Actions are logged" → seccomp audit mode
- "Cannot transfer beyond limit" → cgroup resource limits + network policy

**Where this analogy breaks down:** A bank employee's role can expand gradually through promotions; container permissions are static at runtime — you cannot gain new syscalls or capabilities without restarting with a different profile. This is a feature, not a limitation.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Container security is making sure a container can only do exactly what it needs to do — nothing more. A container running a web server should not be able to format the host's hard drive. Container security applies the "least privilege" principle: the container gets the minimum permissions it needs.

**Level 2 — How to use it (junior developer):**
Three essential steps: (1) Add `USER node` or `USER 1000` to every Dockerfile — never run as root in production. (2) Run `trivy image myapp:1.0` before pushing — fix critical CVEs. (3) In Kubernetes, add `securityContext: { runAsNonRoot: true, readOnlyRootFilesystem: true }` to every pod spec. These three steps address 80% of the most common container security issues.

**Level 3 — How it works (mid-level engineer):**
**Non-root:** `USER 1000` in Dockerfile sets the default UID for the container process. If the application needs to bind to port 80 (< 1024, normally root-only), add `CAP_NET_BIND_SERVICE` specifically. **Read-only filesystem:** `--read-only` flag mounts the writable layer as read-only. Applications that need temp writes must use `--tmpfs /tmp`. **Capability dropping:** `--cap-drop=ALL` removes all default capabilities; `--cap-add=X` selectively re-adds needed ones. **Seccomp:** the default Docker seccomp profile blocks 40+ syscalls. Custom profiles restrict further — `strace -c` on the application reveals which syscalls it actually uses, enabling minimum-viable seccomp profiles. **Kubernetes Pod Security Admission:** `pod-security.kubernetes.io/enforce: restricted` namespace label enforces all of these requirements via admission control, preventing misconfigured pods from starting.

**Level 4 — Why it was designed this way (senior/staff):**
Container security was retroactively added to a platform designed for developer experience first. The default-root Docker configuration was intentional in 2013 — it simplified development. Security teams in 2015+ pushed back hard as containers entered production. The OCI runtime spec intentionally does not mandate security defaults beyond namespace isolation — it leaves capability configuration to the higher-level tool (Docker/containerd/Kubernetes). This means every layer of the stack (Dockerfile, Docker CLI, Kubernetes, admission controller) can add security hardening, creating the defence-in-depth model. The ongoing evolution: rootless container runtimes (Podman, rootless Docker, rootless containerd) move the security boundary even earlier — the container runtime itself no longer needs root privileges on the host, eliminating a whole class of container escape vulnerabilities.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  CONTAINER SECURITY LAYERS                               │
│                                                          │
│  1. IMAGE LAYER                                          │
│     Trivy scan → no critical CVEs                       │
│     Multi-stage build → minimal surface                 │
│     No secrets in ENV or layers                         │
│                                                          │
│  2. USER LAYER                                           │
│     USER 1000 → non-root inside container              │
│     USER namespace → UID maps to low-priv on host       │
│                                                          │
│  3. FILESYSTEM LAYER                                     │
│     --read-only → root filesystem immutable             │
│     tmpfs /tmp → in-memory writable scratch             │
│                                                          │
│  4. CAPABILITY LAYER                                     │
│     --cap-drop=ALL                                      │
│     --cap-add=NET_BIND_SERVICE (if needed)              │
│     No: CAP_NET_RAW, CAP_SYS_PTRACE, CAP_SYS_ADMIN    │
│                                                          │
│  5. SYSCALL LAYER (seccomp)                              │
│     Default Docker profile: blocks ~40 syscalls         │
│     Custom profile: allows only 60 of 450+ syscalls     │
│                                                          │
│  6. NETWORK LAYER                                        │
│     Kubernetes NetworkPolicy: whitelist-only ingress    │
│     No egress to metadata service (169.254.169.254)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Build image → image scan → Dockerfile USER directive
→ [CONTAINER STARTS with security profile ← YOU ARE HERE]
→ non-root UID, capabilities dropped, seccomp active
→ application serves normally within restricted context
```

**FAILURE PATH:**
```
Application tries to bind port 80 as non-root (common mistake)
→ "Permission denied: bind: EACCES" (NET_BIND_SERVICE not granted)
→ fix: docker run --cap-add=NET_BIND_SERVICE
→ or better: run on port 3000 and use load balancer to expose 80
```

**WHAT CHANGES AT SCALE:**
At hundreds of microservices, per-container seccomp profiles are impractical to maintain manually. Use a "generate from strace" approach during development to auto-generate minimal profiles. Kubernetes Pod Security Admission Controller enforces baseline/restricted policies across the entire cluster. Container runtime security tools (Falco, Tetragon) provide runtime threat detection — alerting when a container makes a suspicious syscall (e.g., `ptrace` on a web server).

---

### 💻 Code Example

Example 1 — Hardened Dockerfile:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

FROM node:20-alpine
WORKDIR /app

# Copy only production artifacts
COPY --from=builder /app/node_modules ./node_modules
COPY src/ ./src/

# Make all files owned by node user
RUN chown -R node:node /app

# Run as non-root (UID 1000 in node:alpine = "node" user)
USER node

EXPOSE 3000
CMD ["node", "src/server.js"]
```

Example 2 — Hardened Docker run:
```bash
docker run \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=/etc/docker/seccomp-node-profile.json \
  --user 1000:1000 \
  --memory=512m \
  --cpus=0.5 \
  myapp:1.0
```

Example 3 — Kubernetes Pod security context:
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault  # Docker default seccomp
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false   # Cannot re-gain root
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: []  # No capabilities added = minimal
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
```

---

### ⚖️ Comparison Table

| Control | Docker Flag | K8s Field | Prevents |
|---|---|---|---|
| Non-root user | `--user 1000` | `runAsUser: 1000` | Root-level host access after escape |
| No privilege escalation | `--security-opt no-new-privileges` | `allowPrivilegeEscalation: false` | SUID binary exploitation |
| Read-only filesystem | `--read-only` | `readOnlyRootFilesystem: true` | Container filesystem tampering |
| Drop all capabilities | `--cap-drop=ALL` | `capabilities: drop: ["ALL"]` | Kernel-level attacks via capabilities |
| Seccomp profile | `--security-opt seccomp=profile.json` | `seccompProfile: RuntimeDefault` | Kernel exploit via syscall |
| No privileged mode | (avoid `--privileged`) | `privileged: false` | Full namespace bypass |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Running as root in a container is fine because containers are isolated | Root in a default (non-USER-namespace) container = root on the host if a container escape vulnerability exists. Always run non-root. |
| `--read-only` breaks all applications | Many applications need writable temp directories. Use `--tmpfs /tmp` alongside `--read-only` to provide writable ephemeral storage without touching the root filesystem. |
| Seccomp blocks legitimate syscalls | The default Docker seccomp profile is permissive — only blocking known-dangerous syscalls. Applications that break under default seccomp are unusual. Custom profiles are needed only for further hardening. |
| Container scanning is a one-time activity | New CVEs are discovered daily. Images must be rescanned continuously (weekly at minimum) and rebuilt when high/critical CVEs affect base images. |
| Kubernetes RBAC secures containers | Kubernetes RBAC controls API access (who can deploy). Container security controls what the container process can do at runtime. They are orthogonal concerns. |

---

### 🚨 Failure Modes & Diagnosis

**Container Running as Root in Production**

**Symptom:** Security audit finds production pods running as UID 0.

**Diagnostic Command / Tool:**
```bash
# Kubernetes: find pods running as root
kubectl get pods -A -o json \
  | jq '.items[] | select(.spec.containers[].securityContext.runAsUser == 0 or 
    (.spec.containers[].securityContext.runAsUser == null and 
     .spec.securityContext.runAsNonRoot != true)) 
    | .metadata.name'
```

**Fix:** Add `USER 1000` to all Dockerfiles. Add `runAsNonRoot: true` to all Kubernetes pod specs. Enable Kubernetes Pod Security Admission with `baseline` or `restricted` policy.

**Prevention:** Enable Pod Security Admission Controller at namespace level. Fail CI builds for images with `USER root` or no `USER` directive.

---

**CVE Found in Production Image After Deploy**

**Symptom:** Security scanner alerts on a newly-disclosed CVE affecting a library in a production container.

**Diagnostic Command / Tool:**
```bash
# Scan deployed image for CVEs
trivy image myapp:1.0.5 \
  --severity HIGH,CRITICAL \
  --exit-code 1

# Find all images running in cluster with vulnerable base
kubectl get pods -A -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}' \
  | sort -u | grep "node:18" # find pods using vulnerable base
```

**Fix:** Update base image, rebuild, rescan, redeploy. For Kubernetes: rolling update to new image.

**Prevention:** Integrate Trivy into CI (`--exit-code 1` blocking on CRITICAL). Use Renovate/Dependabot to auto-update base images. Subscribe to CVE feeds for your base image OS/runtime.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linux Namespaces` — the primary isolation mechanism containers rely on
- `Cgroups` — resource limits that prevent DoS exploits from containers

**Builds On This (learn these next):**
- `Image Scanning` — the pre-deployment security check
- `Distroless Images` — extreme image minimisation for security

**Alternatives / Comparisons:**
- `MicroVM (Firecracker)` — stronger isolation than containers; trades performance for security
- `gVisor` — user-space kernel that intercepts container syscalls for stronger isolation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Defence-in-depth: non-root + minimal     │
│              │ image + no capabilities + seccomp filter  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Default containers run as root with full │
│ SOLVES       │ capabilities — one RCE = host compromise  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Assume the container will be exploited.  │
│              │ Limit what the attacker can do with it   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All production containers — always;      │
│              │ the default config is not production-safe│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use --privileged in production;   │
│              │ never run as UID 0 in production         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security hardening vs configuration      │
│              │ complexity and app compatibility effort  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Assume the cell door opens. Make sure   │
│              │  the prisoner can't do much when it does"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Image Scanning → Distroless Images →     │
│              │ Pod Security Admission                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A container running with `--cap-drop=ALL` and as a non-root user is found to have a heap buffer overflow vulnerability. The attacker can achieve arbitrary code execution within the container process. Walk through exactly what the attacker CAN and CANNOT do given the security constraints — which Linux capabilities they lack, what the seccomp profile prevents at syscall level, what read-only filesystem prevents, and what a container escape into the host with UID 1000 and no capabilities actually allows them to access on the host.

**Q2.** Your organisation runs 200 Kubernetes microservices. A central platform team must enforce the security standards: non-root, no privilege escalation, read-only root filesystem, resource limits. They cannot manually review every deployment manifest. Design the complete policy enforcement architecture using Kubernetes-native tools (not manual review) that: enforces these standards for all new deployments, prevents existing non-compliant pods from being updated without first meeting the standards, and produces a report of current compliance across the entire cluster.

