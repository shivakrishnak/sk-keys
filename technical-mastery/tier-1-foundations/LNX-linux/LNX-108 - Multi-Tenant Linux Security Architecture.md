---
id: LNX-108
title: "Multi-Tenant Linux Security Architecture"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-094, LNX-095, LNX-096, LNX-100, LNX-106
used_by: LNX-109
related: LNX-094, LNX-095, LNX-096, LNX-100, LNX-106, LNX-109
tags: [multi-tenancy, container-isolation, vm-isolation, gvisor, kata-containers, seccomp, apparmor, selinux, cpu-side-channels, spectre-meltdown, kpti, l1tf, mds, numa-isolation, tenant-separation, cloud-security, shared-kernel, trusted-execution-environment, sgx, sev, confidential-computing, hardware-isolation, defense-in-depth]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 108
permalink: /technical-mastery/lnx/multi-tenant-linux-security-architecture/
---

## TL;DR

Multi-tenant Linux security solves the problem of running **untrusted workloads
from different tenants on shared hardware** without them compromising each other.
Defense layers (outermost to innermost): **(1) Hardware isolation** - separate
physical machines (strongest, expensive), or VMs with KVM/Intel TDX for hardware-
enforced boundary. **(2) Hypervisor isolation** - KVM+QEMU guest VMs, Kata
Containers (lightweight VM per container). **(3) User-space kernel** - gVisor
intercepts all container syscalls in a Go-based user-space kernel, preventing
kernel exploits. **(4) Container hardening** - seccomp deny-list, AppArmor/SELinux
MAC, capability dropping, user namespaces (rootless). **(5) Side-channel
mitigations** - KPTI for Meltdown, IBRS/IBPB for Spectre, MDS mitigations for
L1TF/RIDL/Fallout (all involve CPU cache/branch prediction attacks where one
tenant's code leaks another tenant's data from shared CPU microarchitecture).
**(6) NUMA isolation** - allocate separate memory domains to prevent cache-timing
attacks. Confidential Computing (Intel TDX, AMD SEV) encrypts VM memory so even
the hypervisor cannot read tenant data.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-108 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | multi-tenancy, gVisor, Kata Containers, seccomp, side-channel attacks, Spectre/Meltdown, KPTI, confidential computing, NUMA isolation |
| **Prerequisites** | LNX-094 (SELinux), LNX-095 (AppArmor), LNX-096 (seccomp), LNX-100 (hardening), LNX-106 (containers) |

---

### The Problem This Solves

**Problem**: Public cloud providers (AWS, Google, Azure) run customer workloads
on shared physical hardware. Tenant A is a healthcare company with HIPAA data.
Tenant B is an attacker who rents the smallest VM on the same physical host.
Security requirement: Tenant B must NEVER be able to read Tenant A's data, even
with a kernel vulnerability.

**Threat models in order of sophistication:**
1. Noisy neighbor: Tenant B consumes all CPU/memory, causing Tenant A degradation
2. Container escape: Tenant B exploits kernel CVE to escape container, read host memory
3. Side-channel: Tenant B measures CPU cache timing to infer Tenant A's data
4. Hypervisor escape: Tenant B exploits QEMU/KVM to escape VM boundaries
5. Hardware backdoor: firmware-level persistence (nation-state level)

Real-world examples:
- Spectre (2018): JavaScript code on a shared browser tab reads other tabs' memory
- L1TF/Foreshadow (2018): VM reads hypervisor memory via L1 data cache
- DirtyCOW (2016): container exploit allowing host filesystem access
- runc CVE-2019-5736: container escape via /proc/self/exe overwrite

---

### Textbook Definition

**Multi-tenancy security**: Isolation between multiple users (tenants) sharing
the same physical infrastructure, such that one tenant cannot access, modify, or
infer the data of another tenant.

**Defense in depth**: Multiple independent security layers, each of which an
attacker must defeat independently. No single layer is assumed to be sufficient.

**Threat isolation levels (weakest to strongest):**

| Level | Mechanism | What it stops | What it misses |
|-------|-----------|---------------|----------------|
| Container | namespaces + seccomp | Most exploits | Kernel CVEs, side-channels |
| gVisor | User-space kernel | Kernel CVE propagation | Side-channels, slower |
| Kata Containers | Lightweight VM | Container escapes | Hypervisor escapes, side-channels |
| Full VM | KVM + dedicated CPU | Hypervisor exploits (rare) | Side-channels, HW exploits |
| TDX/SEV | Encrypted VM memory | Hypervisor memory access | Physical attacks |
| Separate HW | No sharing | Everything | Cost, efficiency |

---

### Understand It in 30 Seconds

```bash
# === Isolation layer demo ===

# Standard container: shared kernel, namespaces only
docker run --rm ubuntu cat /proc/version
# Linux version 6.1.0-17-amd64 (debian@...)  <- HOST kernel!
# Container shares host kernel -> kernel CVE affects all containers

# gVisor: user-space kernel intercepting syscalls
# Run container with gVisor runtime:
docker run --runtime=runsc --rm ubuntu cat /proc/version
# Linux version 4.4.0 ...  <- gVisor's fake kernel version!
# Container syscalls -> gVisor's Go kernel -> host kernel (filtered)
# Kernel CVE in host kernel? gVisor's syscall interceptor blocks the path

# Kata Containers: each container gets a lightweight VM
docker run --runtime=kata-runtime --rm ubuntu cat /proc/version
# Linux version 6.1.0-kata (kata@...)  <- Kata's own kernel!
# Container inside lightweight QEMU-KVM VM
# Host kernel CVE does not affect: different kernel binary in VM

# === Side-channel mitigations ===

# Check current CPU mitigations:
cat /sys/devices/system/cpu/vulnerabilities/spectre_v2
# Mitigation: Enhanced IBRS, IBPB: conditional, RSB filling, PBRSB-eIBRS

cat /sys/devices/system/cpu/vulnerabilities/meltdown
# Mitigation: PTI

cat /sys/devices/system/cpu/vulnerabilities/l1tf
# Mitigation: PTE Inversion; VMX: cache flushes, SMT disabled

# KPTI (Kernel Page Table Isolation) for Meltdown:
# Without KPTI: kernel memory mapped in user process page tables
# Allows CPU speculative execution to read kernel memory from user space
# With KPTI: kernel pages unmapped when running user code (slower, safe)

# SMT (hyperthreading) vulnerability:
# Two HTs of same core share L1 cache
# Attacker on HT0 can observe cache state modified by HT1 (tenant)
# Mitigation: disable SMT per VM (nosmt kernel parameter)
# For highest security: disable SMT globally (halves CPU capacity!)

# Check SMT status:
cat /sys/devices/system/cpu/smt/control
# on  <- hyperthreading enabled (less secure for multi-tenant)
# notsupported  <- no HT (secure)
# off  <- disabled (security mode)

# For cloud providers: disable SMT per-VM using cpu_flags:
# KVM: set 'noht' in VM CPU flags to prevent HT sharing between VMs

# === NUMA isolation ===

# Allocate separate NUMA nodes per tenant (prevent shared LLC attack):
# Tenant A: NUMA node 0 (CPUs 0-7, 64GB RAM)
# Tenant B: NUMA node 1 (CPUs 8-15, 64GB RAM)
# Shared LLC (L3 cache) still shared WITHIN a NUMA node - not fully isolated
# Only separate physical sockets (or cache partitioning) fully isolates

# Intel CAT (Cache Allocation Technology) for LLC partitioning:
# Divide L3 cache between tenants using cache ways
cat /sys/fs/resctrl/info/L3/cbm_mask
# fffff  <- 20 cache ways available

# Assign 10 ways to tenant A, 10 ways to tenant B:
mkdir /sys/fs/resctrl/tenant_a
echo "L3:0=003ff" > /sys/fs/resctrl/tenant_a/schemata  # ways 0-9
# Add tenant A's tasks to this group:
echo <pid> > /sys/fs/resctrl/tenant_a/tasks

mkdir /sys/fs/resctrl/tenant_b
echo "L3:0=ffc00" > /sys/fs/resctrl/tenant_b/schemata  # ways 10-19
```

---

### First Principles

```
THE MULTI-TENANT ATTACK SURFACE:

Linux kernel is the shared resource. All processes (regardless of
namespace, cgroup, or container) execute Linux kernel code for:
- File I/O
- Network I/O
- Memory allocation
- Process management
- Everything

Container "isolation": only changes what the PROCESS CAN SEE
                       (different namespace IDs, different cgroup)
Container security: DOES NOT prevent malicious process from exploiting
                   kernel vulnerabilities to gain host kernel access

Kernel attack surface per syscall:
  ~350 syscalls in Linux kernel
  Each syscall is code running in kernel mode
  Any bug in kernel code = potential privilege escalation
  CVE database: ~100+ kernel CVEs per year
  Even "hardened" kernel has unknown vulnerabilities

Defense layer analysis:

LAYER 1: Container (namespaces + seccomp + capabilities)
  What it stops:
  - Application-level exploits (incorrect isolation, overly privileged app)
  - "Accidental" resource access (mount namespace prevents seeing /etc)
  - Information leakage via /proc (PID namespace hides processes)
  
  What it does NOT stop:
  - Kernel vulnerability exploitation (attacker calls syscall with crafted
    arguments to trigger kernel bug, gain kernel privileges)
  - Side-channel attacks (namespaces don't isolate CPU cache)
  
  Cost: minimal (native Linux performance)

LAYER 2: seccomp filter (syscall allowlist)
  Idea: container only NEEDS ~50 syscalls, block the other 300
  Block unused syscalls -> reduce kernel attack surface by ~85%
  
  Effectiveness: CVE requires specific syscall to trigger
  If that syscall is blocked by seccomp: CVE cannot be triggered!
  
  Example: CVE-2017-5123 (waitid overflow) - blocked by seccomp
  because waitid is not in Docker's default allowed list
  
  Limitation: some CVEs are in always-needed syscalls (read, write, mmap)
  Cannot block ALL dangerous syscalls without breaking the application
  
  Cost: syscall overhead slightly increased (BPF filter evaluation per syscall)

LAYER 3: gVisor (user-space kernel)
  Architecture:
  Container syscall -> gVisor sentry (Go user-space kernel) -> host kernel
  
  Security model:
  Container never calls HOST KERNEL directly
  gVisor intercepts, validates, and implements the syscall in user space
  gVisor's synthetic kernel: implements Linux ABI in Go
  Only a small set of host syscalls used (read/write, mmap, futex, etc.)
  
  Effectiveness:
  Container exploit: calls CRAFT_SYSCALL to exploit kernel
  gVisor: "I don't know CRAFT_SYSCALL, this is an error" -> container gets error
  Host kernel never sees the malicious syscall
  Isolation: even if gVisor sentry has a bug, attacker needs SECOND exploit
  to break out of gVisor sentry (defense in depth)
  
  Limitation:
  Performance: 10-30% overhead for syscall-heavy workloads
  Compatibility: some syscalls not fully implemented (edge cases)
  Side-channels: gVisor doesn't prevent CPU cache timing attacks
  
  Cost: moderate (syscall overhead, Go sentry process, some incompatibility)

LAYER 4: Kata Containers (VM per container)
  Architecture:
  Container -> QEMU-KVM VM (lightweight, 256MB overhead) -> host kernel
  
  Security model:
  Each container runs in isolated VM
  Container's kernel = Kata's own kernel binary (not host kernel)
  KVM hardware virtualization boundary between container and host
  
  Effectiveness:
  Container exploit: kernel CVE in Kata's kernel = Kata VM compromised
  But: Kata VM kernel ≠ host kernel (different code, different version)
  Even if VM kernel compromised: hypervisor (KVM) boundary remains
  Hypervisor escapes are EXTREMELY rare (QEMU/KVM CVEs are far fewer than
  kernel CVEs)
  
  Side-channels: still shared CPU microarchitecture (partial mitigation with SMT)
  
  Cost: higher (VM startup time ~1s vs container <100ms, memory overhead per VM)

LAYER 5: Side-channel attacks (hardware level)
  Spectre/Meltdown class: exploit CPU speculative execution
  
  Meltdown (CVE-2017-5754):
  CPU speculatively executes code with kernel memory access
  (before privilege check catches it and reverses the access)
  Result: kernel memory temporarily in L1 cache
  Attacker reads cache timing: infers kernel memory content
  
  Fix: KPTI (Kernel Page Table Isolation)
  Kernel pages removed from user-space page tables
  Speculative execution can't access kernel pages (they're not mapped)
  Cost: ~5-30% performance hit on syscall-heavy workloads
  
  Spectre v1/v2: branch prediction cache pollution
  Attacker trains CPU branch predictor to speculatively access victim memory
  Fix: IBRS (Indirect Branch Restricted Speculation), retpoline
  
  L1TF/MDS: L1 data cache and microarchitectural data sampling
  Shared L1 cache across hyperthreaded cores
  One HT core reads data recently used by other HT core
  Fix: flush L1 cache on VM context switch (costly), or disable SMT
  
  Full mitigation: disable hyperthreading (halves CPU capacity) AND KPTI
  Cloud providers: accept some performance hit, enable all mitigations
  Performance-critical deployments: partially disable mitigations (risk trade-off)

CONFIDENTIAL COMPUTING (state of the art):
  Intel TDX (Trust Domain Extensions) / AMD SEV-SNP:
  VM memory encrypted by hardware
  Encryption key: generated inside CPU, not accessible to hypervisor
  Even cloud provider (hypervisor operator) CANNOT read VM memory
  
  Use case: "Even your cloud provider cannot read your data"
  Financial services, healthcare, government workloads on public cloud
  
  Status: production in Azure (Confidential VMs), Google (Confidential GKE),
          AWS (Nitro Enclaves for specific compute, not full VM yet)
```

---

### Thought Experiment

Multi-tenant Kubernetes with different trust levels:

```bash
# === Kubernetes multi-tenancy: namespace-based vs hard tenancy ===

# Soft tenancy (namespace isolation): 
# Multiple tenants in same cluster, separated by RBAC + NetworkPolicy
# Shared kernel: a kernel CVE affects all tenants

kubectl create namespace tenant-a
kubectl create namespace tenant-b

# RBAC: restrict tenant A from seeing tenant B's resources
kubectl apply -f - <<'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: tenant-a-developer
  namespace: tenant-a
subjects:
  - kind: Group
    name: tenant-a-developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: developer
  apiGroup: rbac.authorization.k8s.io
EOF

# NetworkPolicy: tenant A cannot talk to tenant B's pods
kubectl apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-tenant
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: tenant-a  # only allow from same namespace
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: tenant-a
EOF

# Hard tenancy: RuntimeClass for workload isolation level

# Option 1: gVisor for untrusted workloads
kubectl apply -f - <<'EOF'
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc  # gVisor's OCI handler
EOF

# Require gVisor for certain tenants:
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: untrusted-workload
  namespace: tenant-b
spec:
  runtimeClassName: gvisor  # gVisor isolation
  containers:
  - name: app
    image: untrusted-code:latest
EOF

# Option 2: Kata Containers for VM-level isolation
kubectl apply -f - <<'EOF'
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata
handler: kata  # Kata Containers OCI handler
overhead:
  podFixed:
    memory: "256Mi"  # overhead for Kata VM
    cpu: "250m"
EOF

# Kata pod:
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: financial-workload
  namespace: tenant-a
spec:
  runtimeClassName: kata  # VM-level isolation for financial data
  containers:
  - name: payment-processor
    image: payment-app:v2.1.0@sha256:abc...
EOF

# === CPU side-channel mitigation in KVM ===

# QEMU/KVM: disable SMT per VM (prevent L1TF cross-HT attacks):
# In libvirt XML:
# <cpu mode='host-passthrough'>
#   <topology sockets='1' cores='4' threads='1'/>  <- threads=1: no HT
# </cpu>

# Flush L1 cache on VM entry/exit (mitigate L1TF without disabling SMT):
# KVM kernel module parameter:
cat /sys/module/kvm_intel/parameters/vmentry_l1d_flush
# cond  <- conditional flush (default, flushes when known-risky)
# always <- always flush on every VM entry (more secure, ~10% slower)
echo "always" > /sys/module/kvm_intel/parameters/vmentry_l1d_flush

# Check all CPU vulnerability mitigations:
for f in /sys/devices/system/cpu/vulnerabilities/*; do
    echo "$f: $(cat $f)";
done
# /sys/devices/system/cpu/vulnerabilities/gather_data_sampling: Not affected
# /sys/devices/system/cpu/vulnerabilities/itlb_multihit: Not affected
# /sys/devices/system/cpu/vulnerabilities/l1tf: Mitigation: PTE Inversion
# /sys/devices/system/cpu/vulnerabilities/meltdown: Mitigation: PTI
# /sys/devices/system/cpu/vulnerabilities/mmio_stale_data: Mitigation
# /sys/devices/system/cpu/vulnerabilities/retbleed: Mitigation: IBRS
# /sys/devices/system/cpu/vulnerabilities/spec_store_bypass: Mitigation
# /sys/devices/system/cpu/vulnerabilities/spectre_v1: Mitigation
# /sys/devices/system/cpu/vulnerabilities/spectre_v2: Mitigation: IBRS
# /sys/devices/system/cpu/vulnerabilities/srbds: Not affected
# /sys/devices/system/cpu/vulnerabilities/tsx_async_abort: Mitigation
```

---

### Mental Model / Analogy

```
Multi-tenant security = shared apartment building with different security zones

Entire building = physical server
Building foundation = CPU hardware
Building walls = Linux kernel
Building management = hypervisor (KVM)
Apartments = VMs or containers

STANDARD CONTAINERS = rooms in shared apartment (weak isolation)
  Tenants share: all building walls (kernel code), HVAC (CPU cache),
                 electrical wiring (memory bus), building foundation (CPU)
  Namespaces: each tenant has their own room NUMBER (PID, network),
              but walls are thin (same kernel code)
  
  Vulnerability: if there's a hidden passage in the wall (kernel CVE),
  any tenant who finds it can walk into other rooms (container escape)

GVISOR = tenant-operated apartment with private reception desk
  Tenant has their own receptionist (gVisor sentry)
  All requests: "I want to leave the apartment" go through the receptionist
  Receptionist knows all legitimate requests (implements Linux ABI)
  Malicious request: "Please trigger kernel bug 5754" -> 
    receptionist says "I don't do that" -> request blocked
  Tenant never directly accesses building management
  Two barriers: break through tenant's reception AND then building management
  
  BUT: receptionist sits in shared HVAC (same CPU cache as others)
  Cannot prevent listening through HVAC (side-channel attacks)

KATA CONTAINERS = private apartment WITHIN the apartment building
  Tenant has their own apartment (lightweight VM) within the building
  Apartment has its own walls and doors (Kata kernel)
  To reach building infrastructure: go through apartment walls,
  THEN through building walls (KVM hypervisor)
  
  Significantly harder: must break through TWO separate wall systems
  Side-channels still possible: both apartments share HVAC (L1 cache)

FULL VM ISOLATION = entire floor of the building is yours
  Dedicated floor: own elevator, own HVAC, own structural section
  Building management (hypervisor) is very trustworthy (rarely has bugs)
  
SIDE-CHANNEL ATTACKS = listening through shared HVAC ducts
  Even with walls, apartments share HVAC (L1/L2/L3 cache, branch predictor)
  Tenant in one apartment can measure airflow changes (cache timing)
  Infer what tenant in next apartment is doing (data leakage)
  
  Mitigation: flush HVAC between tenants (cache flush on VM switch)
  Full fix: separate HVAC per tenant (disable hyperthreading, or Cat partitioning)
  
  Spectre: I manipulate the HVAC settings (branch predictor training)
  to trick your apartment into "accidentally" pulling air from my duct
  Then I measure what came through (speculative execution data leak)
  Fix: each apartment has its own HVAC control (IBRS: indirect branch restriction)

CONFIDENTIAL COMPUTING = apartment with encrypted ducts
  Even building management cannot read what flows through your ducts
  Encryption key: inside your lock, never given to building management
  Physical duct access still blocked: hardware encryption in CPU
  Cloud provider (building owner): cannot read your data even if they wanted to
```

---

### Gradual Depth - Five Levels

**Level 1:**
What multi-tenancy means: multiple untrusted tenants on shared hardware.
Why containers alone are insufficient (shared kernel). The three isolation
technologies: seccomp/capabilities (hardening), gVisor (user-space kernel),
Kata (VM-per-container). Spectre/Meltdown: the concept that CPU hardware
can leak data between processes.

**Level 2:**
gVisor architecture: sentry + gofer + ptrace/KVM mode. Kata Containers:
QEMU-KVM VM per container, Kata kernel. Kubernetes RuntimeClass for
selecting isolation level. Seccomp default profile: which syscalls are
blocked. KPTI: page table isolation for Meltdown. SMT and L1TF relationship.
Container escape techniques and mitigations.

**Level 3:**
gVisor performance characteristics and compatibility limitations. Kata
overhead: memory per VM, startup latency. CPU vulnerability mitigations
and their performance cost. Intel CAT (Cache Allocation Technology) for
LLC partitioning. NUMA isolation strategy: binding tenant VMs to NUMA nodes.
Kubernetes OPA/Kyverno policies to enforce RuntimeClass by namespace.
Pod Security Admission for hardening.

**Level 4:**
Confidential Computing: Intel TDX architecture, AMD SEV-SNP. Remote
attestation: cryptographic proof of what code is running (Intel DCAP, AMD
attestation). Nitro Enclaves (AWS): isolated execution environment within
EC2 instance. TPM (Trusted Platform Module) for measured boot in multi-tenant
environments. Intel SGX (Software Guard Extensions) for secure enclaves.
Hypervisor security: QEMU/KVM CVE history and architectural mitigations.

**Level 5:**
Transient execution attacks: Retbleed, SRBDS, MMIO Stale Data - newest
generation side-channels targeting microarchitectural buffers. Microcode
updates vs kernel mitigations: trade-offs and deployment strategies.
Side-channel-resistant cryptography: constant-time implementations in Linux
kernel (why critical crypto must not branch on secret data). Hypervisor
design for maximum security: minimizing TCB (Trusted Computing Base) in
Type 1 vs Type 2 hypervisors. RISC-V's security model and why it was
designed to be side-channel resistant at architecture level.

---

### Code Example

**BAD - multi-tenant cluster without isolation:**
```yaml
# BAD: All tenants in same cluster with weak isolation
# Tenant B can potentially exploit kernel CVE to access Tenant A's data

# Tenant B's pod: no runtime isolation
apiVersion: v1
kind: Pod
metadata:
  name: tenant-b-workload
  namespace: tenant-b
spec:
  # BAD: no runtimeClassName = default (runc, shared kernel)
  containers:
  - name: b-app
    image: tenant-b-code:latest  # runs directly on host kernel
    # If tenant-b-code contains kernel exploit: game over for tenant A
    
    # BAD: excessive permissions increase attack surface
    securityContext:
      privileged: true  # BAD: direct kernel access
    
# Tenant A's confidential workload runs in SAME threat domain:
apiVersion: v1
kind: Pod
metadata:
  name: tenant-a-confidential
  namespace: tenant-a  
spec:
  # Same nodes, same kernel, no stronger isolation
  containers:
  - name: a-app
    image: tenant-a-payment-processing:latest
    # If tenant-b exploits kernel: can read this pod's memory
```

```yaml
# GOOD: Defense-in-depth multi-tenant architecture

# RuntimeClass definitions (cluster admin):
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: untrusted-workload   # for external/tenant code
handler: runsc               # gVisor: user-space kernel
scheduling:
  nodeSelector:
    sandbox.gke.io/runtime: gvisor  # only on gVisor-enabled nodes

---
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: financial-sensitive  # for regulated/financial data
handler: kata-qemu           # Kata: VM-level isolation
overhead:
  podFixed:
    memory: "256Mi"
    cpu: "250m"

---
# OPA/Kyverno: ENFORCE RuntimeClass selection by namespace:
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: enforce-runtime-class
spec:
  rules:
  - name: require-kata-for-financial
    match:
      resources:
        kinds: [Pod]
        namespaces: [financial-services, healthcare]
    validate:
      message: "Financial workloads must use Kata Containers runtime"
      pattern:
        spec:
          runtimeClassName: "financial-sensitive"
  
  - name: require-gvisor-for-external
    match:
      resources:
        kinds: [Pod]
        namespaces: [customer-sandbox, ci-runners]
    validate:
      message: "External code must use gVisor runtime"
      pattern:
        spec:
          runtimeClassName: "untrusted-workload"

---
# Hardened pod for financial tenant (Kata + strict security context):
apiVersion: v1
kind: Pod
metadata:
  name: payment-processor
  namespace: financial-services
spec:
  runtimeClassName: financial-sensitive  # Kata VM isolation
  
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: payment
    image: payment-app:v2@sha256:abc123...
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "RBAC and NetworkPolicy are sufficient for multi-tenant Kubernetes" | RBAC and NetworkPolicy provide application-layer isolation (who can call the Kubernetes API, which pods can communicate). They do NOT provide kernel-level isolation. If a pod in one namespace has a kernel exploit: it can escape its container entirely, regardless of RBAC permissions or NetworkPolicy rules. True multi-tenancy requires runtime isolation (gVisor, Kata) to enforce a hardware or software boundary between tenant code and the host kernel. RBAC + NetworkPolicy are necessary but NOT sufficient for strong multi-tenancy. The correct layering: RBAC + NetworkPolicy (application-layer isolation) PLUS RuntimeClass with gVisor or Kata (kernel-layer isolation). Companies running untrusted user code (GitHub Actions, AWS Lambda) all use VM-level isolation per function, not just RBAC. |
| "gVisor provides the same isolation as a VM" | gVisor is NOT a VM. gVisor (runsc) is a user-space process that intercepts syscalls and implements them in Go. The gVisor sentry process runs as a user-space process on the HOST kernel. If an attacker: (1) escapes the container into gVisor's sentry process, then (2) finds a vulnerability in the gVisor sentry itself to execute arbitrary code in the sentry context, they can then (3) attack the host kernel from the sentry process. This two-step attack is significantly harder than a direct kernel exploit (no gVisor) but is not equivalent to KVM-level VM isolation. gVisor's TCB (Trusted Computing Base) includes: the host kernel + gVisor sentry Go code. VM isolation TCB: host kernel + KVM + QEMU (hypervisor). For most threat models, gVisor provides sufficient isolation at better performance than Kata. For high-assurance (classified, financial), Kata is preferred. |
| "Spectre/Meltdown were patched in 2018 and are no longer a threat" | Spectre/Meltdown (2018) were a class of vulnerability, not specific bugs with a single fix. The underlying cause: CPU speculative execution sharing microarchitectural state (L1 cache, branch predictor, store buffer) across privilege boundaries. Since 2018: SRBDS (2020), RetBleed (2022), MMIO Stale Data (2022), Gather Data Sampling (2023), Downfall (2023) - all new variants of the same fundamental transient execution vulnerability class. Each new variant requires a new mitigation: microcode update + kernel patch + possible performance hit. The vulnerability class is architectural: affects all processors that use speculative execution (essentially all modern CPUs). Intel has redesigned newer CPUs (Alder Lake, Sapphire Rapids) with hardware mitigations built in, reducing software mitigation overhead. But for existing CPUs: mitigations are ongoing, performance-impacting, and new variants continue to emerge. The correct posture: enable all kernel mitigations, accept the performance cost (~5-15% on syscall-heavy workloads), pin kernel to latest with security patches. |
| "Confidential Computing (TDX/SEV) makes the hypervisor untrusted, so cloud providers can't see your data" | Confidential Computing does cryptographically protect VM memory from hypervisor access - but the trust model is more nuanced. The hypervisor (cloud provider) can still: (1) observe VM behavior through timing analysis (when does it request CPU time, I/O patterns), (2) control VM networking, I/O, and interrupt delivery, (3) deny service (just stop the VM). What confidential computing guarantees: the cloud provider CANNOT READ the contents of VM memory or CPU registers. What it does NOT guarantee: data confidentiality during I/O (VM must explicitly encrypt data before writing to disk or network), freedom from side-channel attacks (confidential VMs still share physical CPU microarchitecture with other VMs). Remote attestation is the companion technology: cryptographic proof from the CPU that the VM is running specific, unmodified code - this is what makes the trust model meaningful. Full confidential computing stack: TDX + encrypted storage + remote attestation + secure key management.  |

---

### Failure Modes & Diagnosis

```bash
# === Failure: gVisor incompatibility with application ===
# Pod with runtimeClassName: gvisor crashes at startup

# Check pod events:
kubectl describe pod myapp -n tenant-sandbox
# Events:
#   Warning  Failed  5s  kubelet  Error: failed to create containerd task: ...
#   OCI runtime exec failed: exec failed: container_linux.go:...: 
#   starting container process caused: process_linux.go:...: 
#   unable to start container process: error during container init:
#   error mounting ... not supported in runsc

# gVisor compatibility issue: some syscalls or kernel features not supported

# Test which syscall is failing:
# Run test container with gVisor and strace:
docker run --runtime=runsc -e GOTRACEBACK=all myapp:latest 2>&1 | tail -30

# Check gVisor syscall coverage:
# gVisor tracks unsupported syscalls - check logs:
docker run --runtime=runsc \
    -v /tmp/runsc-logs:/tmp/logs \
    -e RUNSC_OVERLAY_LAYERS=1 \
    myapp:latest
cat /tmp/runsc-logs/*.log | grep "UNIMPLEMENTED"
# [SyscallDebug] UNIMPLEMENTED: io_uring_setup(...)  <- io_uring not supported

# io_uring (new Linux async I/O) is NOT supported by gVisor
# Fix: configure app to not use io_uring, OR use Kata Containers instead

# === Failure: Side-channel mitigation performance degradation ===
# After kernel update with new Spectre mitigations, latency increased 30%

# Check which mitigations are active:
for f in /sys/devices/system/cpu/vulnerabilities/*; do
    echo "$(basename $f): $(cat $f)"
done

# Check if KPTI is causing overhead:
# KPTI adds TLB flush on every user<->kernel transition
# For syscall-heavy apps (many small I/Os): significant overhead

# Measure overhead:
# Before mitigation: syscall benchmark
sysbench --test=fileio --file-num=4 --file-block-size=16K \
    --file-total-size=2G --file-test-mode=rndrw --time=60 run

# Options to reduce overhead (with security trade-offs):
# mitigations=off: disables ALL CPU mitigations (DANGEROUS for multi-tenant!)
# nosmt: disables hyperthreading (halves CPU capacity but eliminates many attacks)
# nopti: disables KPTI (removes Meltdown mitigation - only safe on AMD CPUs)

# For single-tenant dedicated servers: acceptable to tune mitigations
# For multi-tenant shared infrastructure: NEVER disable mitigations
cat /proc/cmdline | grep mitigations
# mitigations=auto  <- default: enables all applicable mitigations
```

---

### Related Keywords

**Foundational:**
LNX-094 (SELinux), LNX-095 (AppArmor), LNX-096 (seccomp), LNX-100 (hardening), LNX-106 (containers)

**Builds on this:**
LNX-109 (Linux kernel history)

**Related:**
LNX-109 (kernel history), LNX-110 (GNU/Linux story)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `cat /sys/devices/system/cpu/vulnerabilities/*` | Check all CPU mitigations |
| `docker run --runtime=runsc ...` | Run with gVisor |
| `docker run --runtime=kata-runtime ...` | Run with Kata Containers |
| `kubectl get runtimeclass` | List available runtime classes |
| `echo "always" > /sys/module/kvm_intel/parameters/vmentry_l1d_flush` | Enable L1D flush |
| `cat /sys/devices/system/cpu/smt/control` | Check SMT status |
| `cat /sys/fs/resctrl/info/L3/cbm_mask` | Intel CAT cache ways |

**3 things to remember:**
1. Containers do NOT provide kernel isolation - a kernel CVE breaks containment for ALL containers on the host. For multi-tenant security: use gVisor (user-space kernel, prevents kernel exploit propagation) or Kata Containers (VM-per-container, hardware isolation boundary). Defense in depth: use BOTH container hardening AND runtime isolation.
2. Spectre/Meltdown (2018) were the first of a class of CPU side-channel vulnerabilities still being discovered today. All arise from speculative execution sharing microarchitectural state (cache, branch predictor) across privilege boundaries. Current mitigations (KPTI, IBRS, IBPB) carry 5-15% performance cost. New variants continue to emerge; keep kernel patched.
3. For true multi-tenant isolation at cloud scale: gVisor is appropriate for most untrusted workloads (lower overhead). Kata Containers for regulated/financial data. Confidential Computing (Intel TDX, AMD SEV-SNP) for environments where even the cloud provider must be untrusted (classified, healthcare, financial).

---

### Transferable Wisdom

Multi-tenant isolation principles transfer directly to: cloud provider
security architecture (all public clouds use these exact mechanisms),
browser security (same-origin policy = namespace isolation; site isolation
= VM-per-site in Chrome, gVisor-like in Firefox WebAssembly), database
multi-tenancy (row-level security = namespace/RBAC, connection pooling
resource limits = cgroups), JVM security manager (deprecated - same concept
of software-layer capability restriction, replaced by OS-level container
isolation). The "defense in depth" principle (multiple independent layers, each
must fail independently) applies to: security architecture in general (WAF +
IDS + firewall + application auth), nuclear plant safety systems (multiple
independent shutdown mechanisms), aviation safety (TCAS + ATC + visual
separation - each independent), API security (OAuth token + API gateway +
application auth + database row security). Side-channel attacks illustrate
"information leaks via unintended channels": timing-based password oracle
attacks (measure how long authentication takes to infer if first N chars are
correct), power analysis attacks on hardware crypto, disk access patterns
leaking file structure to unprivileged observer. The confidential computing
model (hardware-enforced memory encryption, remote attestation) is the
foundation for: blockchain trusted execution environments (Intel SGX-based
TEEs), secure key storage (AWS CloudHSM, Azure Dedicated HSM), zero-knowledge
proof systems.

---

### The Surprising Truth

The Spectre vulnerability (2018) required modifying not just the Linux
kernel, but also GCC, LLVM, JavaScript engines (V8, SpiderMonkey), Java JIT,
and almost every other JIT-compiling language runtime - because Spectre
attacks work by controlling the code that a VICTIM process runs speculatively.
Any JIT compiler that generates code from untrusted input (like JavaScript
code from a web page) must now emit "retpoline" sequences (specially crafted
indirect jumps that prevent speculative execution across privilege boundaries),
making JIT-compiled code slightly larger and slower for security.

The deeper revelation from Spectre/Meltdown: modern CPU performance
optimizations (speculative execution, out-of-order execution, caching) are
fundamentally incompatible with perfect information isolation. The CPU was
designed assuming that the programmer controlling the CPU also controlled all
the code and data. Multi-tenancy (running code from mutually untrusted parties
on the same CPU) is architecturally in tension with the performance features
that make modern CPUs fast. There is no free lunch: either accept some
isolation leakage, or accept some performance degradation. Cloud providers
typically accept 5-15% performance degradation to run with full mitigations.

---

### Mastery Checklist

- [ ] Understands the threat model: what specifically can a kernel CVE enable (container escape, memory reading)
- [ ] Can explain gVisor and Kata Containers, their architectures, and when to choose each
- [ ] Understands Spectre/Meltdown conceptually: how speculative execution causes data leakage
- [ ] Can configure Kubernetes to enforce different RuntimeClasses by namespace or policy
- [ ] Knows the performance cost of CPU side-channel mitigations and when they can be tuned

---

### Think About This

1. You are building a managed Kubernetes service (similar to GKE, EKS) where
   customers run arbitrary containerized workloads. Design your multi-tenant
   isolation architecture. What is your default RuntimeClass for customer pods?
   How do you handle customers who request higher isolation (gVisor vs Kata)?
   How do you allocate physical nodes to customer clusters to prevent
   side-channel attacks? What CPU mitigations do you enable and what performance
   SLA can you still offer? How do you detect if a customer is attempting a
   container escape or side-channel attack?

2. A security researcher reports that they can use a Flush+Reload cache
   side-channel attack to read memory across containers on your Kubernetes
   cluster. Containers run on the same node and share L3 cache. The attack
   requires: running a container with specific CPU affinity and making ~1000
   memory probes per second. What is your immediate mitigation? Long-term
   mitigation? Performance trade-off of each option (cache partitioning via
   Intel CAT, disabling hyperthreading, migrating to Kata Containers, moving
   each tenant to dedicated nodes)? How do you validate that a mitigation
   actually prevents the specific attack?

3. Intel TDX and AMD SEV claim "even the cloud provider cannot read your
   VM's memory." But your security team argues: "We still don't trust it
   because the cloud provider controls the network, storage, and platform."
   Build both sides of this argument. What specific guarantees does
   Confidential Computing provide? What does it explicitly NOT protect against?
   For a healthcare company with HIPAA requirements: is Confidential Computing
   on a public cloud sufficient? What complementary controls are needed?

---

### Interview Deep-Dive

**Foundational:**
Q: Why are containers insufficient for strong multi-tenant isolation and what are the alternatives?
A: CONTAINERS: SHARED KERNEL IS THE FUNDAMENTAL ISSUE. A container is a Linux process with additional namespace and cgroup wrapping. The container process executes on the HOST Linux kernel. When the container calls open() or mmap(): that syscall runs in the HOST kernel code. A kernel vulnerability is a bug in kernel code. If an attacker in a container can craft a syscall argument that triggers a kernel bug: they can gain kernel-mode execution and escape all container boundaries (read other containers' memory, modify host filesystem, kill any process). This is why every major container escape CVE (runc CVE-2019-5736, runC vulnerability in 2024) exploits kernel or runtime bugs. ALTERNATIVE 1 - SECCOMP + CAPABILITY DROPPING (defense, not isolation): Reduce kernel attack surface by blocking unused syscalls. If a CVE is in a syscall that seccomp blocks: CVE cannot be triggered. But: CVEs in frequently-used syscalls (mmap, read, write) cannot be blocked. Best defense layer, but not sufficient alone. ALTERNATIVE 2 - gVisor (SOFTWARE ISOLATION): gVisor's sentry process intercepts ALL container syscalls and implements them in Go user space. Container never calls host kernel directly. Result: even if container code triggers a gVisor syscall implementation bug, attacker is in gVisor's Go process, not in kernel mode. Two exploits required to reach host kernel. Cost: ~10-30% performance overhead on syscall-heavy workloads. Best for: untrusted code execution (CI/CD, sandboxing). ALTERNATIVE 3 - Kata Containers (HARDWARE ISOLATION): Each container runs in a lightweight QEMU-KVM VM (256MB overhead). Container has its own kernel (different binary than host). KVM hardware virtualization provides isolation boundary. To escape: exploit container's kernel, then exploit KVM hypervisor (separate, much harder). Historical KVM/QEMU CVEs: far fewer and less severe than kernel CVEs. Best for: financial data, healthcare, compliance-sensitive workloads. Cost: ~500ms startup latency, 256MB+ memory per container. DECISION: Untrusted third-party code or CI runners: gVisor. Financial, healthcare, regulated data: Kata Containers. Defense-in-depth: Kata + seccomp + capability dropping + non-root + read-only rootfs.

**Expert:**
Q: Explain the Spectre and Meltdown vulnerabilities conceptually and how Linux mitigates them for multi-tenant environments.
A: ROOT CAUSE - SPECULATIVE EXECUTION: Modern CPUs aggressively speculate: before a privilege check completes, the CPU runs the instructions after the check speculatively (in case the check passes). If the check fails: speculative results are discarded (the architectural state). BUT: the MICROARCHITECTURAL state (L1 cache state, branch predictor state) is NOT rolled back. An attacker can observe microarchitectural state via timing. MELTDOWN (CVE-2017-5754): Attack: (1) Userspace code reads kernel memory address: `mov rax, [kernel_address]`. (2) CPU raises privilege exception (user can't read kernel). (3) BUT: CPU has already SPECULATIVELY executed the read (and subsequent code using the value). (4) Before exception is fully processed: CPU has loaded kernel data into L1 cache. (5) Attacker: measure timing of accessing cache lines (Flush+Reload): "cache hit = data value bit was 1, cache miss = bit was 0." Result: kernel memory read from userspace. MELTDOWN MITIGATION - KPTI: Kernel Page Table Isolation. When running user code: kernel pages are UNMAPPED from the page table. CPU cannot even speculatively access kernel pages (they're not in the TLB). On every syscall: switch page tables (expensive). Overhead: 5-30% on syscall-heavy workloads. SPECTRE (CVE-2017-5753/5715): Attack: Train CPU branch predictor to speculatively execute code in victim process's address space. (1) Attacker: repeatedly performs branch operation X (trains predictor). (2) In victim context: trigger same branch X in victim's code. (3) CPU speculatively executes victim's code past the branch (predictor says "branch not taken"). (4) Speculative execution accesses victim's private data (training set the predictor to speculate into the wrong code path). (5) Attacker: read microarchitectural state to infer victim's data. SPECTRE MITIGATION: (a) IBRS/IBPB (Indirect Branch Restricted Speculation): flush branch predictor state on context switch. Prevents attacker training from affecting victim. (b) Retpolines (Return Trampoline): replace indirect jumps with sequence that CPU cannot speculate through. (c) SMEP/SMAP: prevent kernel from speculatively executing user code. MULTI-TENANT IMPLICATION: L1TF (L1 Terminal Fault): in a VM, a hypervisor-level attack via shared L1 cache between different VMs running on the same hyperthreaded cores. Mitigation: flush L1 cache on VM context switch (`vmentry_l1d_flush=always`), or disable SMT (hyperthreading) to prevent HT core sharing. Performance cost: L1 flush adds ~100-200ns per VM switch. SMT disable: 50% fewer logical CPUs = 50% cost increase.
