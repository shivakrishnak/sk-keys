---
id: CTR-044
title: Container Security Architecture
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-017, CTR-018, CTR-021, CTR-023
used_by: CTR-051, CTR-054
related: CTR-022, CTR-040
tags:
  - containers
  - security
  - architecture
  - advanced
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /ctr/container-security-architecture/
---

# CTR-044 - Container Security Architecture

⚡ TL;DR - Container security architecture is defense-in-depth applied to containers: secure the image, the runtime, the network, the secrets, and the admission layer - each independently, all together.

| Metadata        |                               |     |
| :-------------- | :---------------------------- | :-- |
| **Depends on:** | CTR-017, CTR-018, CTR-021, CTR-023 |     |
| **Used by:**    | CTR-051, CTR-054              |     |
| **Related:**    | CTR-022, CTR-040              |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team secures their application code carefully but runs it in a
container as root, with all Linux capabilities, mounting the host
filesystem, and pulling images from an unscanned registry. The container
isolation they thought they had is largely illusory.

**THE BREAKING POINT:**
A container escape vulnerability is disclosed (e.g. runc CVE-2019-5736).
An attacker who can execute code inside a container can overwrite the
host runc binary and achieve host root access. Teams without image
scanning, non-root enforcement, or admission control have no compensating
controls and no detection layer.

**THE INVENTION MOMENT:**
Container security architecture applies the same defense-in-depth
principle that secures networks and operating systems: no single control
is sufficient, and controls at different layers must independently block
or detect attacks. The layers for containers are: supply chain (image),
runtime (process), network (traffic), secrets (credentials), and
admission (policy enforcement).

**EVOLUTION:**
2015: Docker introduces user namespaces for rootless containers.
2018: OPA/Gatekeeper brings policy-as-code to Kubernetes admission.
2019: Falco provides runtime threat detection. 2020: Sigstore launches
for image signing and supply chain integrity. 2022: SLSA framework
standardises supply chain security levels. 2023: eBPF-based runtime
security (Tetragon, Cilium) provides kernel-level observability without
kernel modules.

---

### 📘 Textbook Definition

**Container security architecture** is the structured application of
security controls across the container lifecycle: image build and supply
chain, registry storage, runtime execution, network traffic, secrets
management, and admission policy enforcement. Each layer provides
independent protection; the combination achieves defense-in-depth.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Secure the image, the runtime, the network, and the admission gate -
independently and together.

**One analogy:**

> Container security is like physical building security: the supply chain
> control is vetting construction materials (image scanning); the runtime
> control is locking the doors (non-root, capabilities dropped); the
> network control is CCTV and access cards (network policies); the
> admission control is the security guard at the entrance (OPA/Kyverno).
> A thief who bypasses the guard can still be stopped by the locked door.

**One insight:**
The most dangerous container security posture is "secure application
code inside an insecure container." Application-level security is
necessary but cannot compensate for running as root, with host
privileges, or with unscanned images.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Containers are not VMs** - they share the host kernel. A kernel
   exploit defeats all container isolation unless additional controls
   (gVisor, Kata) add a separate kernel boundary.
2. **Least privilege applies to containers** - run as non-root, drop
   all capabilities not required, use read-only root filesystem.
3. **Images are the primary attack surface** - a vulnerable base image
   exposes all containers built from it; scanning must be continuous.
4. **Admission control is the last-resort gate** - enforce security
   policy at the cluster level so individual teams cannot bypass it.

**DERIVED DESIGN:**
Given invariant 1: assume the kernel can be reached from any container.
Add compensating controls (seccomp, AppArmor, gVisor) to reduce the
kernel attack surface. Given invariant 3: scan images in CI, at push,
and continuously in the registry (images age poorly).

**THE TRADE-OFFS:**
**Gain:** Each independent control layer reduces the probability of a
successful attack reaching the host or adjacent workloads.
**Cost:** Each control adds operational overhead (policy maintenance,
false positives in scanning, admission webhook latency).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Non-root, no privileged mode, network policies, image
scanning, secrets not in environment variables - these address real
attack vectors.
**Accidental:** Overlapping policy engines (OPA + Kyverno + PSP all
at once), scanning tools with unconfigured thresholds that block all
deployments.

---

### 🧪 Thought Experiment

**SETUP:**
A Kubernetes cluster runs 30 microservices. All containers run as UID 0
(root). Images are pulled from DockerHub with no scanning. Secrets are
injected as environment variables.

**WHAT HAPPENS WITHOUT CONTAINER SECURITY ARCHITECTURE:**
A remote code execution vulnerability in one service gives an attacker
shell access inside the container as root. Because the container runs as
root and has the `SYS_ADMIN` capability, the attacker mounts the host
filesystem, reads secrets from environment variables of other containers
via the Kubernetes API (if RBAC is misconfigured), and pivots to the
host. The blast radius is the entire cluster.

**WHAT HAPPENS WITH CONTAINER SECURITY ARCHITECTURE:**
The attacker achieves RCE in the container. The container runs as UID
1000 (non-root), has no capabilities beyond the minimum set, uses a
read-only root filesystem, and runs with a seccomp profile that blocks
unusual syscalls. The network policy prevents lateral movement to other
services. Falco detects the anomalous shell execution and alerts. The
blast radius is one container.

**THE INSIGHT:**
Container security architecture does not prevent vulnerabilities in
application code. It constrains what an attacker can do after exploiting
one - reducing blast radius from "entire cluster" to "one container."

---

### 🧠 Mental Model / Analogy

> Container security architecture is a castle with multiple independent
> defences: the moat (network policies - limit what can reach the castle),
> the drawbridge (admission control - block non-compliant workloads), the
> portcullis (runtime controls - limit what processes can do), the vault
> (secrets management - protect crown jewels separately), and the guards
> (runtime threat detection - detect anomalous behaviour).

Element mapping:

- **Moat** = Kubernetes NetworkPolicy
- **Drawbridge** = OPA/Gatekeeper or Kyverno admission webhooks
- **Portcullis** = seccomp, AppArmor, non-root, dropped capabilities
- **Vault** = Vault, AWS Secrets Manager (not env vars)
- **Guards** = Falco, Tetragon runtime threat detection

Where this analogy breaks down: a real castle's defences are sequential;
container security layers can be bypassed independently (a vulnerability
in the drawbridge does not help if the moat stops lateral movement).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Container security architecture is the set of controls that limit what
a container can do and what happens if one is compromised.

**Level 2 - How to use it (junior developer):**
Start with the 5 basics: (1) non-root user in Dockerfile, (2) no
`:latest` tag (use digest pinning), (3) scan images in CI with Trivy,
(4) set resource limits, (5) do not put secrets in env vars - use
Kubernetes Secrets mounted as files or a secrets manager.

**Level 3 - How it works (mid-level engineer):**
Apply controls at each layer: supply chain (image signing with Cosign,
SBOM generation), runtime (securityContext: non-root, readOnlyRootFilesystem,
drop all capabilities, add only required ones), network (NetworkPolicy
default-deny then allow-list), admission (Kyverno ClusterPolicy enforcing
security baseline), secrets (external-secrets-operator or Vault sidecar).

**Level 4 - Why it was designed this way (senior/staff):**
Each control layer exists because a different attack vector exists at
that layer. Image scanning addresses supply chain compromise (SolarWinds
model). Non-root + dropped capabilities address kernel exploit escalation.
Network policies address lateral movement after container escape.
Admission control addresses developer misconfiguration (the most common
real-world failure mode, not sophisticated attacks).

**Expert Thinking Cues:**

- "What is the blast radius if this container is fully compromised?"
- "Which controls would slow or detect an attacker who has shell access?"
- "Are admission policies enforced via webhook (preventing deployment)
  or audit only (logging but not blocking)?"

---

### ⚙️ How It Works (Mechanism)

**SECURITY LAYER MAP:**

```
[Build] Image scanning (Trivy, Grype)
        Image signing (Cosign + Sigstore)
        SBOM generation (Syft)
        |
[Push]  Registry scanning (ECR scanning,
        Harbor, Snyk Container)
        |
[Admit] Kyverno / OPA Gatekeeper policies
        (enforce security baseline)
        |
[Run]   securityContext (non-root, readOnly,
        dropped caps, seccomp, AppArmor)
        |
[Net]   NetworkPolicy (default-deny, allow-list)
        |
[Secrets] Vault / external-secrets-operator
          (no env var secrets)
        |
[Detect] Falco / Tetragon (runtime anomaly)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Developer pushes code
  |
  v
CI: build image + Trivy scan
  | (fail if Critical CVE)
  v
Registry: sign with Cosign
  |
  v
Kubernetes admission webhook
  | checks: non-root, limits, no privileged
  |           ← YOU ARE HERE
  v
Pod starts with securityContext enforced
  |
  v
Runtime: Falco monitors syscalls
  |
  v
Network: NetworkPolicy restricts traffic
```

**FAILURE PATH:**
Image with critical CVE slips through (scan not blocking in CI, only
reporting). Container deployed and exploited. Without runtime detection
(Falco), the attack is invisible until post-breach forensics.

**WHAT CHANGES AT SCALE:**
At scale, image scanning must be continuous (images in the registry age
as new CVEs are disclosed). Admission control must apply to all
namespaces including system ones. Secrets management must support
rotation without pod restarts.

---

### 💻 Code Example

```yaml
# BAD: privileged, root, no limits, host path access
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      privileged: true    # can access host
    volumeMounts:
    - mountPath: /host
      name: host-root     # full host filesystem
  volumes:
  - name: host-root
    hostPath:
      path: /
```

```yaml
# GOOD: hardened securityContext
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp@sha256:abc123  # digest pin
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
    volumeMounts:
    - mountPath: /tmp
      name: tmp-dir        # writable tmp only
  volumes:
  - name: tmp-dir
    emptyDir: {}
```

```yaml
# GOOD: Kyverno policy enforcing non-root cluster-wide
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-runAsNonRoot
    match:
      resources:
        kinds: [Pod]
    validate:
      message: "Containers must not run as root"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true
```

**How to test / verify correctness:**

```bash
# Scan an image for CVEs
trivy image myapp:v1.4.2

# Verify image signature
cosign verify --key cosign.pub myapp@sha256:abc123

# Check what capabilities a running container has
docker inspect <id> | jq '.[].HostConfig.CapAdd'

# Simulate admission policy in dry-run
kubectl apply --dry-run=server -f pod.yaml
```

---

### ⚖️ Comparison Table

| Layer | Tool Options | Enforcement Point | Blocks or Detects |
|---|---|---|---|
| Image scanning | Trivy, Grype, Snyk | CI / Registry | Blocks |
| Image signing | Cosign + Sigstore | Admission | Blocks |
| Admission policy | Kyverno, OPA/Gatekeeper | Kubernetes API | Blocks |
| Runtime isolation | seccomp, AppArmor, gVisor | Kernel | Blocks |
| Runtime detection | Falco, Tetragon | Kernel (eBPF) | Detects |
| Network control | NetworkPolicy, Cilium | CNI | Blocks |
| Secrets | Vault, external-secrets | App level | Protects |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containers are isolated by default" | Containers share the host kernel. Without seccomp, AppArmor, and non-root enforcement, a kernel vulnerability can escape the container entirely. |
| "Scanning images in CI is sufficient" | Images age - new CVEs are disclosed after images are scanned and deployed. Continuous registry scanning and runtime CVE detection are required. |
| "Kubernetes Secrets are encrypted at rest by default" | Kubernetes Secrets are base64-encoded in etcd but NOT encrypted by default. Encryption at rest requires explicit EncryptionConfiguration and an external KMS. |
| "Running as non-root prevents all privilege escalation" | `allowPrivilegeEscalation: false` and `capabilities: drop: ALL` are also required. Non-root alone does not prevent a setuid binary from escalating. |
| "Network policies are enforced by default" | NetworkPolicy requires a CNI plugin that enforces them (Calico, Cilium). Default Kubernetes installation with a non-enforcing CNI ignores all NetworkPolicy manifests. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Container Running as Root (Security)**
**Symptom:** Post-breach forensics shows attacker achieved host access
from a compromised container. Container was running as UID 0.
**Root Cause:** No runAsNonRoot enforcement in securityContext or
admission policy. Developers default to root because it avoids permission
errors during development.
**Diagnostic:**

```bash
# Find all pods running as root
kubectl get pods -A -o json | jq '
  .items[] |
  select(
    (.spec.securityContext.runAsUser == 0 or
     .spec.securityContext.runAsNonRoot != true)
  ) | .metadata.name'

# Check effective UID inside a running container
kubectl exec -it <pod> -- id
```

**Fix:** Add `runAsNonRoot: true` and `runAsUser: 1000` to all pod
specs. Enforce via Kyverno ClusterPolicy in Enforce mode.
**Prevention:** Enforce non-root via admission webhook from cluster
creation. Test Dockerfiles with `docker run --user 1000`.

---

**Failure Mode 2: Secrets Exposed in Environment Variables**
**Symptom:** Breach investigation reveals database credentials and API
keys were readable from any process inside any pod via `/proc/*/environ`.
**Root Cause:** Secrets injected as environment variables rather than
mounted files. Env vars are visible to all processes in the container
and logged in crash dumps.
**Diagnostic:**

```bash
# Find pods with secrets as env vars (look for secretKeyRef)
kubectl get pods -A -o yaml | \
  grep -A 3 secretKeyRef | head -40

# Read env vars from inside a running pod
kubectl exec -it <pod> -- env | grep -i secret
```

**Fix:** Mount secrets as files (`volumeMounts` with `secret` volume)
rather than environment variables. Use external-secrets-operator or
Vault agent sidecar for automatic rotation.
**Prevention:** Kyverno policy that denies `secretKeyRef` in env vars
and requires file mounts.

---

**Failure Mode 3: Admission Policies in Audit Mode Only**
**Symptom:** Security review shows policy violations everywhere, but no
workloads have been blocked. All policies are in `audit` mode.
**Root Cause:** Team set policies to audit to avoid disruption but never
graduated them to enforce mode. Audit mode generates logs nobody reads.
**Diagnostic:**

```bash
# Check Kyverno policy enforcement actions
kubectl get clusterpolicies -o json | jq '
  .items[] |
  {name: .metadata.name,
   action: .spec.validationFailureAction}'

# Check OPA constraint enforcement actions
kubectl get constraints -A -o json | \
  jq '.items[] | {name:.metadata.name,
  action:.spec.enforcementAction}'
```

**Fix:** Graduate audit policies to enforce mode in non-production
namespaces first. Fix violations. Then promote to production.
**Prevention:** Start with enforce mode in new namespaces. Treat audit
mode as a transition state, not a permanent configuration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-017 - Linux Namespaces]] - kernel isolation primitives containers rely on
- [[CTR-018 - Cgroups]] - resource isolation for containers
- [[CTR-021 - Container Security]] - foundational container security concepts
- [[CTR-023 - Image Scanning]] - vulnerability scanning in the supply chain

**Builds On This (learn these next):**

- [[CTR-051 - Container Security Research (Rootless, gVisor)]] - advanced isolation
- [[CTR-054 - Container Security Mental Model]] - threat model thinking

**Alternatives / Comparisons:**

- [[CTR-022 - Distroless Images]] - reducing image attack surface at the build layer
- [[CTR-040 - Docker Secrets]] - secrets management approach in Compose environments

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Defense-in-depth for containers     │
│ PROBLEM     │ Single control cannot stop all attacks│
│ KEY INSIGHT │ Limit blast radius, not just entry  │
│ USE WHEN    │ Always - baseline for all containers │
│ AVOID WHEN  │ N/A - all layers should be present  │
│ TRADE-OFF   │ Security controls vs. ops overhead  │
│ ONE-LINER   │ Secure image, runtime, net, secrets │
│ NEXT EXPLORE│ CTR-051 Rootless, CTR-054 Threat    │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Containers share the host kernel - runtime controls (seccomp, non-root,
   dropped capabilities) are essential, not optional hardening.
2. Images age - scan continuously in the registry, not just at build time.
3. Admission control in audit mode is not security - graduate to enforce
   mode or it provides no protection.

**Interview one-liner:**
"Container security architecture applies defense-in-depth across five
layers - supply chain, runtime, network, secrets, and admission control -
because a container share the host kernel and a single misconfiguration
in any layer can expose the entire host."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Defense-in-depth means each layer must provide independent protection.
A layer that only works when all other layers are intact is not adding
security - it is adding complexity. Design each security control to
contain a breach that has already bypassed the previous layer.

**Where else this pattern appears:**

- **Web application security:** Input validation (supply chain), WAF
  (admission), RBAC (runtime), secrets management, and logging/alerting
  (detection) mirror the container security layers exactly.
- **Cloud account security:** SCPs (admission), IAM least privilege
  (runtime), VPC security groups (network), Secrets Manager (secrets),
  and CloudTrail (detection) follow the same independent-layers model.
- **Physical security:** Badge access (admission), locked server racks
  (runtime), CCTV (detection), and split-knowledge safe combinations
  (secrets) all apply independent controls that limit blast radius.

---

### 💡 The Surprising Truth

The most common real-world container security failure is not a
sophisticated supply chain attack or a kernel exploit - it is a developer
misconfiguration: a container running as root with `privileged: true`
because the developer could not get the application to work without it
and nobody enforced a policy preventing it. The CNCF Security Audit of
2021 found that the majority of security incidents in Kubernetes
environments were caused by misconfiguration, not vulnerability
exploitation. Admission control that blocks misconfigured workloads
prevents more real-world incidents than any vulnerability scanner.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** Kubernetes Secrets are base64-encoded in
etcd. Why is base64 not encryption? What three mechanisms together
provide actual secrets security in a Kubernetes cluster?
*Hint:* Consider etcd encryption at rest (EncryptionConfiguration + KMS),
Kubernetes RBAC on the Secret resource, and secrets injection method
(env var vs. mounted file). What does each mechanism protect against?

**Q2 (D - Root Cause):** A Falco alert fires: "A shell was spawned in a
container running nginx." This is almost certainly a breach indicator.
What are the 3 most likely attack vectors that would lead to a shell
spawning inside an nginx container?
*Hint:* Consider: remote code execution via nginx vulnerability, command
injection via application code, and developer `kubectl exec` during an
incident. How does Falco distinguish them?

**Q3 (C - Design Trade-off):** An admission webhook (Kyverno) is set to
Enforce mode and blocks any pod without `readOnlyRootFilesystem: true`.
A legacy application writes temporary files to its container filesystem
at startup and fails. How do you satisfy the security control without
modifying the legacy application?
*Hint:* Consider emptyDir volumes mounted at the specific paths the
application writes to. What is the security difference between
readOnlyRootFilesystem with emptyDir mounts vs. a writable root filesystem?