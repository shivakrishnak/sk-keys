---
id: OSY-122
title: Container vs VM Isolation
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-105, OSY-106, OSY-118, OSY-119
used_by: []
related: OSY-118, OSY-119, OSY-123
tags:
  - container
  - VM
  - isolation
  - security
  - hypervisor
  - Kata
  - gVisor
  - trade-off
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 122
permalink: /technical-mastery/osy/container-vs-vm-isolation/
---

## TL;DR

Containers share the host kernel (namespace + cgroup sandbox);
VMs have separate guest kernels (hardware-level isolation via
hypervisor). Containers: faster start (~100ms), less overhead
(~1-3% CPU), smaller footprint. VMs: stronger isolation, kernel
exploit cannot cross VM boundary. For untrusted workloads: use
Kata Containers or gVisor (VM-level isolation with container UX).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-122 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | container isolation, VM isolation, hypervisor, gVisor, Kata Containers, security boundary |
| **Prerequisites** | OSY-105, OSY-106, OSY-118, OSY-119 |

---

### Isolation Boundary Comparison

```
Container isolation stack:
  
  Physical Hardware
  └── Host Linux Kernel (SHARED by ALL containers)
        ├── Container A
        │     ├── pid namespace (own PID tree)
        │     ├── net namespace (own network)
        │     ├── mnt namespace (own filesystem view)
        │     ├── cgroup (CPU/memory limits)
        │     └── seccomp (syscall filter)
        └── Container B
              └── (same as above)
              
  Security property:
    Container A syscall -> Host Kernel
    Kernel exploit in Container A -> affects Host + Container B
    Namespaces: "what you can SEE" is limited
    Cgroups: "how much you can USE" is limited
    Seccomp: "what you can DO" is filtered
    But: same kernel code path for all containers
    
VM isolation stack:
  
  Physical Hardware
  └── Hypervisor (KVM, VMware, Xen, Hyper-V)
        ├── VM A
        │     ├── Virtual CPUs
        │     ├── Virtual RAM
        │     ├── Virtual Disk
        │     └── Guest OS + Kernel A (completely separate)
        │           └── App A
        └── VM B
              └── Guest OS + Kernel B (completely separate)
                    └── App B
                    
  Security property:
    App A in VM A -> Guest Kernel A
    Kernel exploit in VM A: escapes to Hypervisor (not VM B)
    Hypervisor exploits: extremely rare; much smaller attack surface
    VM A and VM B: completely separate kernels; no shared code
```

---

### Quantitative Comparison

```
Startup time:
  Container: ~100-500ms (process start; kernel already running)
  VM (full OS): 30-120 seconds (BIOS + kernel boot + OS init)
  VM (microVM Firecracker): 100-300ms (minimal kernel, fast boot)
  
Memory overhead:
  Container: ~50-100MB overhead per container (no guest OS)
  VM: 300MB-2GB (guest OS RAM + kernel + overhead)
  MicroVM (Firecracker): 5-20MB overhead (minimal guest kernel)
  
CPU overhead:
  Container: < 1-3% overhead (namespaces are near-zero cost)
  VM (hardware virtualization): 2-8% overhead (vCPU scheduling)
  VM (full emulation): 10-50%+ overhead (avoid in production)
  
Storage:
  Container image: 5-500MB (layers; shared base)
  VM image: 1-20GB (full OS disk image)
  
Density (workloads per host, 64GB RAM):
  Containers: hundreds to thousands (shared OS)
  VMs (full): 10-30 (each needs 2GB+ RAM for OS)
  MicroVMs: 100-500 (minimal kernel overhead)

Network:
  Container: veth pairs + iptables (100-500us overhead)
  VM: virtio-net (100-400us overhead)
  Both: comparable latency for most workloads
```

---

### Middle Ground: Kata Containers and gVisor

```
Problem: want container UX (fast, small) + VM security (kernel isolation)

Solution 1: Kata Containers
  Each container runs in its own lightweight VM (QEMU/Firecracker)
  Container runtime API: same as Docker/CRI-O
  Inside: proper guest kernel (not shared with host)
  
  Architecture:
    Host Kernel
    └── QEMU/Firecracker (Kata VMM)
          └── Guest Kernel (tiny; Kata-specific)
                └── Container (OCI-compatible)
  
  Strengths:
    Full kernel isolation (like VMs)
    CRI-compatible: works with Kubernetes
    < 500ms startup (Firecracker VMM)
    
  Weaknesses:
    50-100MB overhead per container (guest kernel)
    Cannot do privileged operations (mount, iptables) inside
    Requires: hardware virtualization support (nested KVM for cloud)
    
Solution 2: gVisor (Google)
  User-space kernel: implements Linux syscall interface in Go
  Container syscalls: handled by gVisor Sentry (user-space)
  Only ~50 syscalls pass through to host kernel (vs 300+)
  
  Architecture:
    Host Kernel
    └── gVisor Sentry (user-space Linux kernel impl in Go)
          └── Container application
          
  Strengths:
    Dramatically reduced host kernel attack surface
    Fast startup (no VM overhead)
    Native container UX
    
  Weaknesses:
    NOT complete isolation (still shares host kernel, via Sentry)
    Some syscalls not implemented (check compatibility list)
    10-30% performance overhead (all syscalls through Sentry)
    Go GC in Sentry: periodic pause

When to choose what:
  Trusted workloads, same team: standard containers
  Untrusted code, multi-tenant SaaS: Kata Containers
  Untrusted code, high density: gVisor (or Kata+Firecracker)
  Maximum isolation, compliance (FedRAMP): VMs or Kata
  Cloud Functions/Lambda: Firecracker microVMs (AWS Lambda internally)
```

---

### Side-Channel Attack Considerations

```
Spectre/Meltdown and containers:
  Both attacks: exploit speculative execution to read
  kernel memory from userspace
  
  Container mitigation:
    KPTI (kernel page table isolation): already default on kernels
    Mitigations: grep 'Spectre\|Meltdown' /sys/devices/system/cpu/vulnerabilities/*
    
  BUT: KPTI does NOT protect between containers
  Container A can still read Container B's memory
  if both containers run on same physical core
  
  VM mitigation:
    Hardware virtualization: different VMs use different PTEs
    L1TF/MDS patches: required for cross-VM isolation
    
  For high-security multi-tenant: use VMs
  "noisy neighbor" side-channel: unavoidable in containers
  
  Java-specific:
    JIT cache: shared code cache in JVM can leak timing info
    For cryptographic isolation: separate JVM per tenant
    Or: constant-time crypto libraries (BouncyCastle timing-safe)
```

---

### Comparison Table

| Property | Container | VM (Full) | MicroVM | Kata | gVisor |
|----------|-----------|-----------|---------|------|--------|
| Startup | 100ms | 60s | 200ms | 500ms | 100ms |
| Memory overhead | 50MB | 512MB | 50MB | 100MB | 30MB |
| CPU overhead | < 1% | 5% | 3% | 5% | 15% |
| Kernel shared? | Yes | No | No | No | Partial |
| Container UX | Yes | No | Yes | Yes | Yes |
| Trusted workloads | Excellent | Good | Good | Good | Good |
| Untrusted workloads | Poor | Good | Good | Excellent | Good |
| Kubernetes support | Native | Via kubeadm | Firecracker CRI | Yes | Yes |

---

### Decision Guide

| Workload | Isolation Needed | Recommendation |
|----------|----------------|----------------|
| Your own Java service | Team trust | Standard containers |
| Multi-tenant SaaS | Tenant isolation | Kata Containers |
| Lambda-style functions | Code isolation | Firecracker/gVisor |
| FedRAMP/regulated | Compliance mandate | VMs or Kata |
| Edge, resource limited | Min overhead | gVisor or containers |
| Dev/staging | Low risk | Standard containers |
