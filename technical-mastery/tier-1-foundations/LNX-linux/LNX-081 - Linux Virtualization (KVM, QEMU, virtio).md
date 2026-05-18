---
id: LNX-081
title: "Linux Virtualization (KVM, QEMU, virtio)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-022, LNX-071
used_by: LNX-106
related: LNX-080, LNX-085, LNX-073
tags: [kvm, qemu, virtio, hypervisor, virt-manager, libvirt, cpu-virtualization, nested-virtualization, vmx, svm, paravirtualization, hardware-assisted-virtualization, live-migration]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 81
permalink: /technical-mastery/lnx/linux-virtualization-kvm-qemu-virtio/
---

## TL;DR

**KVM** (Kernel-based Virtual Machine, kernel module `kvm.ko`) is a Linux
hypervisor that uses CPU hardware extensions (Intel VT-x/AMD-V) to run
VMs at near-native speed. **QEMU** is a userspace device emulator that works
WITH KVM: KVM handles CPU/memory virtualization (hardware-assisted), QEMU
handles device emulation (disk, network, USB). **virtio**: paravirtual device
standard - VMs use virtio drivers for disk/network (faster than emulated
hardware). Check: `lscpu | grep -i virtualization` or `/proc/cpuinfo vmx/svm`.
Manage VMs: `virsh`, `virt-install`, `virt-manager`. Live migration: move
running VM between hosts without downtime. Cloud providers (AWS, GCP, Azure)
use KVM at their core.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-081 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | KVM, QEMU, virtio, hypervisor, libvirt, hardware virtualization, VT-x, SVM, live migration |
| **Prerequisites** | LNX-022 (Process management), LNX-071 (Namespaces) |

---

### The Problem This Solves

**Problem 1**: Running multiple isolated operating systems on shared hardware.
Before KVM: VMware ESXi or Xen (separate, proprietary or complex). After KVM:
the Linux kernel itself IS the hypervisor. KVM (`kvm.ko`) + QEMU provide
full VM capability on any Linux server with VT-x/AMD-V CPUs. Cloud providers
run millions of VMs on KVM (AWS EC2's Xen migrated to KVM via Nitro, Google
GCE uses KVM, OpenStack deploys KVM by default).

**Problem 2**: Near-native I/O performance for VMs. Emulating real hardware
(e.g., Intel e1000 NIC) requires KVM to emulate hardware registers, interrupts,
DMA. Slow. virtio: instead of emulating real hardware, use a simple, optimized
virtual device interface designed for VMs. virtio-net (networking), virtio-blk
(block storage), virtio-scsi, virtio-balloon (memory ballooning). Up to 5x
faster I/O vs full emulation.

---

### Textbook Definition

**KVM (Kernel-based Virtual Machine)**: Linux kernel module (kernel 2.6.20,
2007) that turns Linux into a Type-1 hypervisor using CPU hardware
virtualization extensions. KVM provides: CPU virtualization (via `vmenter`/
`vmexit` for hardware-assisted execution), memory virtualization (EPT/NPT
for nested page tables), and I/O virtualization (emulated by QEMU).

**Hypervisor types:**
- Type 1 (bare-metal): hypervisor runs directly on hardware. Examples: VMware ESXi, Xen, KVM (Linux IS the OS + hypervisor)
- Type 2 (hosted): hypervisor runs on top of host OS. Examples: VirtualBox, VMware Workstation

**QEMU**: Quick Emulator. Userspace program that emulates complete hardware.
With KVM: QEMU handles device emulation, KVM handles CPU/memory (hardware-
assisted). Together: a complete VM environment. QEMU processes appear as
regular Linux processes (with a special `/dev/kvm` file descriptor for the
KVM kernel module).

**virtio**: A standardized interface for paravirtual I/O devices. The guest
OS needs virtio drivers (included in Linux kernel, Windows requires separate
install). Virtio splits I/O into: virtqueues (ring buffers shared between
guest and host), notification mechanisms. Eliminates hardware emulation
overhead for I/O.

**libvirt**: Management API and daemon (`libvirtd`) for KVM, QEMU, Xen,
containers. CLI: `virsh`. GUI: `virt-manager`. Used by OpenStack Nova and
oVirt for VM management.

---

### Understand It in 30 Seconds

```bash
# === Check KVM availability ===
# Check CPU supports virtualization:
lscpu | grep -i virtualization
# Virtualization: VT-x    <- Intel
# Virtualization: AMD-V   <- AMD

# Check /proc/cpuinfo for vmx (Intel) or svm (AMD):
grep -E "vmx|svm" /proc/cpuinfo | head -1
# flags: ... vmx ...  <- VT-x present

# Check KVM kernel module is loaded:
lsmod | grep kvm
# kvm_intel            380928  0
# kvm                  950272  1 kvm_intel

# Load if not loaded:
modprobe kvm_intel   # Intel
modprobe kvm_amd     # AMD

# Check KVM device:
ls -la /dev/kvm
# crw-rw----. 1 root kvm 10, 232 Nov  1 10:00 /dev/kvm

# === Create and manage VMs with virsh ===
# List running VMs:
virsh list
# Id  Name            State
# 1   ubuntu-22-04    running
# 2   centos-7        paused

# List all VMs (including stopped):
virsh list --all

# VM lifecycle:
virsh start ubuntu-22-04
virsh shutdown ubuntu-22-04   # graceful
virsh destroy ubuntu-22-04    # forced off
virsh reboot ubuntu-22-04
virsh suspend ubuntu-22-04
virsh resume ubuntu-22-04

# Console access:
virsh console ubuntu-22-04
# (Ctrl+] to exit)

# VM info:
virsh dominfo ubuntu-22-04
# Id: 1
# Name: ubuntu-22-04
# UUID: 1a2b3c4d-...
# OS Type: hvm
# State: running
# CPU(s): 4
# CPU time: 1234.5s
# Max memory: 8192000 KiB
# Used memory: 6291456 KiB

# === Create a VM with virt-install ===
virt-install \
    --name myvm \
    --memory 2048 \
    --vcpus 2 \
    --disk size=20,format=qcow2,bus=virtio \  # virtio disk
    --network network=default,model=virtio \   # virtio network
    --os-variant ubuntu22.04 \
    --cdrom /iso/ubuntu-22.04.3-live-server.iso \
    --graphics none \
    --console pty,target_type=serial

# === qcow2 image management ===
# Create a new qcow2 disk:
qemu-img create -f qcow2 myvm.qcow2 20G

# Check disk info:
qemu-img info myvm.qcow2
# file format: qcow2
# virtual size: 20 GiB (21474836480 bytes)
# disk size: 2.1 GiB   <- actual space used (sparse)
# cluster_size: 65536

# Resize disk:
qemu-img resize myvm.qcow2 +10G   # expand by 10G
# (also need to expand partition inside VM)

# Convert formats:
qemu-img convert -f vmdk -O qcow2 vmware.vmdk kvm.qcow2
qemu-img convert -f qcow2 -O raw kvm.qcow2 flat.img

# === Live migration ===
# Migrate VM between KVM hosts (shared storage):
virsh migrate \
    --live \
    --verbose \
    myvm \
    qemu+ssh://destination-host/system

# === View VM network and disk usage ===
virsh domstats myvm
# block.0.rd.bytes: 1234567    <- disk reads
# block.0.wr.bytes: 9876543    <- disk writes
# net.0.rx.bytes: 1234567      <- network RX
# net.0.tx.bytes: 9876543      <- network TX

# CPU accounting:
virsh cpu-stats myvm
```

---

### First Principles

**KVM architecture and hardware virtualization:**
```
CPU Hardware Virtualization (Intel VT-x):

Two modes:
  VMX Root Mode: host (Linux kernel + KVM module) runs here
    Normal kernel execution, privilege rings 0-3
    KVM module has full hardware access
  
  VMX Non-Root Mode: guest OS runs here
    Guest thinks it has full hardware control
    Actually: all privileged operations trigger VMExits

VMENTER / VMEXIT cycle:
  
  Host (KVM) -> Guest:
    Load VMCS (Virtual Machine Control Structure):
      - Guest registers (RIP, RSP, CR3, RFLAGS, ...)
      - Guest state (IA32_EFER, PDPTE, ...)
      - Control fields (exit on INT, halt, I/O, ...)
    
    Execute VMLAUNCH/VMRESUME instruction
    CPU transitions to VMX Non-Root mode
    Guest code runs at near-native speed
  
  Guest -> Host (VMExit):
    Triggered by: 
      - Privileged instructions (HLT, MOV to CR3)
      - I/O operations (IN/OUT)
      - Interrupts, exceptions
      - Page faults that escape guest page tables
      - CPUID, RDTSC (depending on config)
    
    CPU saves guest state to VMCS
    CPU transitions back to VMX Root mode
    KVM handles the exit cause:
      I/O operation -> hand to QEMU device model
      Page fault -> EPT (Extended Page Tables) walk
      Interrupt -> inject into guest
      CPUID -> return configured values
    KVM resumes guest (VMRESUME)

Memory virtualization (EPT/NPT):
  
  Without EPT: software-managed shadow page tables
    KVM must intercept every guest page table modification
    Very high overhead (10-20x slower than native)
  
  With EPT (Intel) / NPT (AMD):
    Two-level page table walk in hardware:
      Guest virtual -> Guest physical (guest page tables)
      Guest physical -> Host physical (EPT)
    CPU walks both levels in hardware
    Only faults to KVM when EPT entry is missing (EPT violation)
    Near-native memory access (1-5% overhead typically)

I/O virtualization (QEMU device emulation):
  
  Guest writes to I/O port (e.g., IDE disk 0x1F0):
  1. VMExit: I/O port access intercepted by KVM
  2. KVM signals QEMU (via /dev/kvm ioctl)
  3. QEMU device model handles the I/O:
     - Disk: reads from qcow2 file on host
     - Network: sends packet via tap device
  4. QEMU signals completion
  5. KVM resumes guest with I/O result
  
  This is slow (1-2 round trips through kernel+userspace per I/O)

virtio optimization:
  
  virtio-net (paravirtual NIC):
    Guest and host share ring buffer (virtqueue)
    Guest: puts packets in virtqueue, kicks host via single write
    Host: reads virtqueue, sends packets, puts completions back
    One notification covers many packets (batching)
    Result: ~5x faster than emulated e1000 NIC
  
  VHOST: kernel-space virtio backend
    Move virtio processing from QEMU (userspace) to kernel (vhost)
    Guest to kernel directly (bypass QEMU for data path)
    Even faster: used for high-performance networking
    SR-IOV: even further - guest directly accesses physical NIC hardware
```

---

### Thought Experiment

Live migration internals:

```bash
# What happens during KVM live migration:
# 
# Setup: VM (myvm) running on host1, migrate to host2
# Shared storage (NFS/Ceph): both hosts access same qcow2 file
#
# Phase 1: PRE-COPY (iterative memory copy)
#   KVM enables dirty page tracking on source
#   KVM sends ALL guest memory pages to host2 over TCP
#   While sending: guest keeps running
#   KVM tracks which pages were MODIFIED (dirtied) during copy
#
# Phase 2: ITERATIVE DIRTY COPY
#   KVM resends only modified (dirty) pages
#   Repeat until: dirty set is small enough to migrate quickly
#   (typically 3-5 iterations, getting smaller each time)
#
# Phase 3: STOP-AND-COPY (downtime)
#   Pause the VM on host1
#   Send remaining dirty pages (very small at this point)
#   Send VM state: CPU registers, VMCS, device state
#   Total downtime: typically 50-200ms
#
# Phase 4: RESUME on host2
#   Start VM on host2 with transferred state
#   VM resumes from exactly where it was paused
#   Applications see brief pause (TCP retransmits, etc.)
#
# Migration monitoring:
virsh migrate-stats myvm   # during migration
# Data remaining: 512 MB -> 128 MB -> 32 MB -> (paused) -> done

# What makes migration fail:
# 1. CPU model mismatch: if host1 has newer CPU features that host2 lacks
#    Fix: pin VM to CPU model: <cpu mode='custom' match='exact'>
#         or use CPU model pinning in libvirt
# 2. Disk not shared: if using local disk (not NFS/Ceph)
#    Fix: use block migration (slower, copies disk too)
#         virsh migrate --live --copy-storage-all myvm ...
# 3. Network bandwidth: memory copy rate must exceed dirty rate
#    Fix: compress migration data, increase bandwidth
#         virsh migrate-setspeed myvm 1024   # 1 GB/s
```

---

### Mental Model / Analogy

```
KVM + QEMU = apartment building with special architecture

Physical server = land + foundation
KVM kernel module = building management authority (the hypervisor layer)
  Has master keys to all resources
  Controls who gets what resources

QEMU process = apartment unit manager (one per VM)
  Manages one specific apartment (VM)
  Requests resources from building management
  Handles all day-to-day operations for that unit

VM = apartment
  Has its OWN address space (like a private home within the building)
  Guest OS = the residents (think they own the whole house)
  
Hardware virtualization (VT-x) = magic architecture:
  Residents think they control the building infrastructure
  (heating, electricity, plumbing = privileged operations)
  
  When residents try to control infrastructure directly:
    Building management is secretly notified (VMExit)
    Building management handles it correctly
    Residents never know they don't have real control
  
  This is so fast: residents don't notice the delay
  (VT-x handles this in hardware, not slow software interception)

virtio = standardized utility interfaces:
  Old way: apartments simulate a specific real appliance brand
    (emulated e1000 NIC = IKEA clone of a specific vintage refrigerator)
    Works but inefficient: lots of translation overhead
  
  virtio way: standardized building utility interface
    Power: standard 220V socket (standard interface, any device works)
    Internet: standard ethernet port (virtio-net)
    Storage: standard USB3 port (virtio-blk)
    
    Residents (guest OS) use standard interfaces -> fast
    Building manager handles the actual utility delivery -> efficient

Live migration = moving residents to a new building while they sleep:
  Phase 1: clone the furniture in the new apartment (copy memory)
  Phase 2: track what residents moved/changed
  Phase 3: pause briefly, move the final changes + residents themselves
  Phase 4: residents wake up in new apartment, don't even notice
  (TCP connections resume, applications see brief stall)
```

---

### Gradual Depth - Five Levels

**Level 1:**
KVM concept: Linux as hypervisor. Check for VT-x/AMD-V support. VMs vs
containers. `virsh list`, `virsh start/stop`. QEMU as device emulator. qcow2
image format.

**Level 2:**
KVM architecture: KVM kernel module + QEMU userspace. Hardware-assisted
virtualization (VT-x/AMD-V). virtio devices: virtio-net, virtio-blk. `virt-install`
to create VMs. `virsh dominfo`, `virsh dumpxml`. libvirt and `libvirtd`. qcow2
features: sparse allocation, snapshots, copy-on-write.

**Level 3:**
VMX root/non-root modes. VMExit causes and handling. EPT/NPT for memory
virtualization. QEMU device model: emulated vs virtio vs SR-IOV. Live migration
phases (pre-copy, stop-and-copy). KVM NUMA topology (vNUMA). CPU pinning:
`virsh vcpupin`. Huge pages for VMs: `hugetlbfs`. vhost-net and vhost-user.

**Level 4:**
VMCS (Virtual Machine Control Structure) fields. EPT page walks and EPT
violations. KVM dirty page tracking for migration. OVMF/UEFI for VMs. Virtio
ring buffer protocol. SR-IOV (Single Root I/O Virtualization): physical
function + virtual functions, guest directly accesses PCIe VF. KVM debugging:
`kvm_stat`, perf KVM events. Intel VT-d (IOMMU for PCI passthrough). Nested
virtualization: running KVM inside KVM (`kvm_intel.nested=1`).

**Level 5:**
KVM kernel code: `virt/kvm/` in Linux source. kvm_run structure (shared
between kernel/userspace). KVM paravirtual features: kvmclock (guest clock),
KVM steal time. Spectre/Meltdown mitigations in KVM: L1TF (L1 Terminal Fault),
MDS mitigations, retpoline in KVM. Virtio 1.0/1.1 spec. Virtio-fs (virtiofsd):
host filesystem sharing via DAX. QEMU monitor protocol (QMP). Live snapshot:
`virsh snapshot-create-as --live`. Open vSwitch + KVM network integration.
SEV (AMD Secure Encrypted Virtualization): encrypted VM memory.

---

### Code Example

**BAD - KVM configuration mistakes:**
```bash
# BAD 1: Using emulated disk bus instead of virtio (slow I/O):
virt-install \
    --disk size=20,format=qcow2,bus=ide   # emulated IDE = slow!
# IDE emulation: each I/O request = VMExit + QEMU device emulation
# ~5x slower than virtio

# GOOD: Always use virtio for KVM disk and network:
virt-install \
    --disk size=20,format=qcow2,bus=virtio \  # virtio-blk
    --network network=default,model=virtio    # virtio-net

# BAD 2: Not allocating huge pages for VMs (memory performance):
# Default: VMs use 4KB pages
# Each guest page access = EPT walk through many 4KB host pages
# For a 4GB VM: 1 million 4KB pages to manage

# GOOD: Use huge pages (2MB) for VMs:
# On host - allocate huge pages:
echo 2048 > /proc/sys/vm/nr_hugepages   # 2048 * 2MB = 4GB
# In libvirt VM XML:
# <memoryBacking>
#   <hugepages/>
# </memoryBacking>

# Verify:
grep HugePages /proc/meminfo
# HugePages_Total: 2048
# HugePages_Free: 2048
# After VM starts:
# HugePages_Free: 0   <- VM allocated all huge pages

# BAD 3: Using qcow2 without preallocation for I/O-intensive VMs:
qemu-img create -f qcow2 vm.qcow2 50G
# qcow2 sparse: allocates blocks as written
# Metadata updates on every new block write = extra I/O overhead
# For databases: causes write amplification

# GOOD: Use preallocation=metadata (pre-allocate qcow2 metadata):
qemu-img create -f qcow2 -o preallocation=metadata vm.qcow2 50G
# Or: raw format for maximum performance (no qcow2 overhead):
qemu-img create -f raw vm.raw 50G
# Raw = no copy-on-write, no snapshots, but maximum I/O performance
```

**GOOD - VM management automation:**
```bash
# Create a template VM and clone from it:
# Step 1: Create template:
virt-install \
    --name ubuntu-template \
    --memory 1024 \
    --vcpus 2 \
    --disk /var/lib/libvirt/images/ubuntu-template.qcow2,size=10,bus=virtio \
    --os-variant ubuntu22.04 \
    --location 'https://archive.ubuntu.com/ubuntu/dists/jammy/main/installer-amd64/' \
    --extra-args "console=ttyS0 auto=true" \
    --graphics none

# After installation: sysprep the template (generalize it):
virt-sysprep -d ubuntu-template \
    --operations machine-id,ssh-hostkeys,udev-persistent-net

# Seal the template:
virsh shutdown ubuntu-template
virsh domxml-to-native qemu-argv --domain ubuntu-template > /dev/null

# Step 2: Clone from template:
virt-clone \
    --original ubuntu-template \
    --name myvm-01 \
    --auto-clone

virt-clone \
    --original ubuntu-template \
    --name myvm-02 \
    --auto-clone

# The clone has:
# - New MAC address (different network identity)
# - New UUID
# - Copy of the template's disk (independent)

# Snapshot workflow:
# Create snapshot before a risky operation:
virsh snapshot-create-as myvm-01 \
    "before-update-$(date +%Y%m%d)" \
    "Before OS upgrade" \
    --atomic

# List snapshots:
virsh snapshot-list myvm-01

# Revert if something goes wrong:
virsh snapshot-revert myvm-01 "before-update-20241101"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "KVM and QEMU are the same thing" | KVM and QEMU are separate components that work together. KVM is a Linux kernel module (`kvm.ko`) that uses CPU hardware extensions (VT-x/AMD-V) to provide hardware-assisted CPU and memory virtualization. KVM without QEMU: just the CPU/memory virtualization, no devices. QEMU is a userspace process that emulates a complete hardware platform (disk controller, network card, USB, etc.). QEMU without KVM: pure software CPU emulation (very slow, 50-100x slower). Together: KVM handles what CPUs do natively (near-native speed), QEMU handles device emulation. When you see a QEMU process in `ps aux`: that's one VM. The QEMU process holds the VM's device state and communicates with the KVM kernel module via `/dev/kvm` ioctls. |
| "Containers and VMs provide equivalent isolation" | VMs provide hardware-level isolation via a hypervisor barrier. Containers share the host kernel. A KVM VM escape requires exploiting: the QEMU device model (userspace), OR the KVM kernel module, AND bypassing the hardware virtualization layer (VMExit handling). Container escapes require: exploiting a namespace bug, OR a capability misconfiguration, OR a kernel vulnerability accessible from inside the container. In practice: VM escapes are rarer and harder; container escapes have a larger attack surface. For multi-tenant workloads (especially processing untrusted code): VMs or VM-backed containers (Kata Containers, Firecracker) provide substantially better isolation than standard Linux containers. The cloud providers' multi-tenancy model uses VMs (not containers) at the customer isolation boundary for this reason. |
| "Live migration requires no downtime at all" | Live migration achieves very short downtime (50-200ms typically) but not zero downtime. The stop-and-copy phase (when the VM is paused to transfer final state) creates a brief pause. During this pause: ongoing TCP connections see a brief stall (not disconnect - modern TCP retransmits). For most applications: this is imperceptible (a user on a web app doesn't notice 100ms). For real-time applications (VoIP, financial trading, game servers): even 50ms is unacceptable. Storage migration (without shared storage) has significantly longer downtime. The downtime depends on: dirty page rate (how fast the guest modifies memory), network bandwidth for migration, and VM memory size. Pre-copy migration with a high dirty rate (e.g., database with heavy writes) may struggle to converge because pages are being dirtied faster than they're being migrated. |
| "virtio is just a performance optimization - functionally equivalent to emulated devices" | virtio changes the fundamental interface model between guest and host. Emulated devices (e1000 NIC, IDE disk) implement the complete behavior of specific hardware including registers, interrupts, timing, and quirks. The guest uses a real device driver designed for that hardware. virtio devices expose a SIMPLIFIED API: virtqueues (ring buffers), notification ports, feature bits. The guest requires a VIRTIO-SPECIFIC driver (not the driver for any real hardware). This means: virtio requires guest driver support (Linux kernel has virtio drivers; Windows requires separate virtio driver package from RedHat). Benefit: virtio's simplicity allows significant optimization - batching multiple I/O requests in one notification, larger transfer sizes, direct DMA without translation. For high-I/O workloads: virtio can achieve 80-90% of native hardware performance; emulated devices typically achieve 20-40%. |

---

### Failure Modes & Diagnosis

**KVM performance and management issues:**
```bash
# Symptom: VM is slow, high CPU usage on host
# Check for excessive VMExits:
kvm_stat   # requires kvm-tools package
# Shows VMExit counts per type:
# VMEXIT_CPUID: 1234/s   <- guest calling CPUID frequently
# VMEXIT_IO: 45678/s     <- high I/O VMExits (check virtio vs emulated)
# VMEXIT_HLT: 234/s      <- guest CPU idle (normal)

# Check vCPU steal time (host not giving VMs promised CPU):
virsh domstats myvm | grep cpu
# cpu.time: (nanoseconds of vCPU time)
# For normalized steal time: use top inside VM
# top: %st column = steal time (how much CPU time was "stolen" by hypervisor)
# Steal time > 5-10%: host is overcommitted

# Symptom: VM disk I/O slow
# Verify virtio is being used:
virsh dumpxml myvm | grep -A3 "disk type"
# <disk type='file' device='disk'>
#   <driver name='qemu' type='qcow2' cache='writeback'/>
#   <target dev='vda' bus='virtio'/>  <- good (virtio)
# If bus='ide': change to virtio

# Check disk cache mode:
virsh dumpxml myvm | grep cache
# cache='none': bypass page cache, direct to disk
#   -> best for databases (avoids double buffering)
# cache='writeback': write through host page cache
#   -> best for general workloads
# cache='unsafe': maximum performance, data loss on crash

# Symptom: VM won't start, "insufficient permissions"
# Check /dev/kvm permissions:
ls -la /dev/kvm
# crw-rw---- 1 root kvm
# Current user must be in 'kvm' group:
id | grep kvm
# If not: usermod -aG kvm $USER; newgrp kvm

# Symptom: live migration fails with "CPU model mismatch"
# Check CPU models on source and destination:
virsh capabilities | grep -A5 "model name"
# Hosts have different CPU generations
# Fix: pin to common CPU model in VM XML:
virsh edit myvm
# Change:
#   <cpu mode='host-passthrough'>
# To:
#   <cpu mode='custom' match='exact'>
#     <model fallback='allow'>Skylake-Client-noTSX</model>
#   </cpu>
# virsh define myvm.xml
```

---

### Related Keywords

**Foundational:**
LNX-022 (Process management), LNX-071 (Namespaces), LNX-072 (Cgroups)

**Builds on this:**
LNX-080 (Container internals), LNX-106 (Container platform architecture)

**Related:**
LNX-085 (XDP, kernel bypass networking), LNX-073 (eBPF)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `lscpu \| grep Virtualization` | Check CPU virtualization support |
| `virsh list --all` | List all VMs |
| `virsh start/shutdown/destroy NAME` | VM lifecycle |
| `virsh dominfo NAME` | VM resource info |
| `virsh console NAME` | Serial console access |
| `qemu-img info FILE` | qcow2 image info |
| `qemu-img create -f qcow2 FILE SIZE` | Create disk image |
| `virsh migrate --live` | Live migrate VM |
| `kvm_stat` | Real-time KVM VMExit stats |

**3 things to remember:**
1. KVM = kernel module for CPU/memory virtualization (hardware-assisted); QEMU = userspace device emulator; together = full VM
2. Always use virtio for disk and network (5x faster than emulated hardware)
3. qcow2 = flexible (snapshots, sparse); raw = maximum I/O performance (databases)

---

### Transferable Wisdom

KVM/QEMU architecture (kernel module + userspace daemon, communicating
via ioctls) appears in: DPDK (kernel module + userspace data plane),
eBPF (kernel programs + userspace control), io_uring (kernel ring buffer
+ userspace). The virtio ring buffer (shared memory ring between guest
and host for I/O) is the same pattern as: SPSC (single-producer single-
consumer) queues in lock-free programming, DPDK's rte_ring, AF_XDP socket
zero-copy networking. Live migration (iterative dirty copy + brief pause)
appears in: Redis BGSAVE + AOF replay, Kafka log replication (leader sends
existing log, follower catches up), distributed database leader failover
(replicate writes, pause briefly, cut over). VM CPU model pinning for
live migration = same problem as: microservice compatibility matrices
(service A requires feature X, service B doesn't have feature X, can't
migrate workloads between them). The solution pattern is also the same:
agree on a common baseline. Cloud engineers: AWS EC2 instance types
(c5, r5, m5) are built on KVM-based Nitro hypervisor + Nitro cards for
I/O. Understanding KVM/QEMU/virtio helps explain AWS NVMe SSD performance,
Enhanced Networking (SR-IOV), and why bare-metal instances (`i3.metal`)
are offered for I/O-critical workloads.

---

### The Surprising Truth

AWS, the world's largest cloud provider, ran on Xen hypervisor from 2006
to ~2017, then spent years migrating all of their infrastructure to KVM
via their custom "Nitro" platform. The migration was not primarily about
performance (both are mature hypervisors) but about SECURITY and FEATURE
VELOCITY. Xen's large attack surface (the Xen hypervisor process is
large and complex) was a security concern in a multi-tenant environment.
The Nitro platform moves almost all I/O handling OUT of the hypervisor
into dedicated Nitro cards (custom ASICs for networking and storage).
The result: the main CPU hypervisor becomes minimal (small attack surface),
while I/O is handled by dedicated hardware (near bare-metal performance,
up to 100 Gbps networking on some instance types). This is the evolution
of virtio taken to its logical conclusion: instead of QEMU userspace device
emulation, use dedicated hardware. The KVM kernel module remains, but the
"QEMU" layer was replaced with Nitro hardware. This architectural insight -
move I/O to dedicated hardware, keep the hypervisor minimal - is also behind
Azure's FPGA-based networking (Azure Accelerated Networking) and Google's
Jupiter network fabric. The cloud computing revolution runs almost entirely
on Linux KVM, custom hardware, and the virtio protocol.

---

### Mastery Checklist

- [ ] Can check CPU virtualization support (`lscpu`, `/proc/cpuinfo vmx/svm`) and KVM module status
- [ ] Can create and manage VMs with `virsh` and `virt-install`
- [ ] Knows why virtio devices are faster than emulated hardware
- [ ] Understands KVM's VMExit mechanism: what triggers exits and how KVM handles them
- [ ] Can use `qemu-img` for disk management and knows when to use qcow2 vs raw format

---

### Think About This

1. You're planning to run a database (PostgreSQL) inside a KVM VM. You need
   to choose between: (a) qcow2 format with cache=writeback, (b) raw format
   with cache=none, (c) raw format with cache=writeback. Explain the I/O
   path for each option (how a write reaches the physical disk), the
   durability implications (what data is at risk during a crash), and which
   you'd choose for production with reasons.

2. A VM on your KVM host has `%st` (steal time) > 20% as shown by `top`
   inside the VM. The host has 8 physical CPUs and runs 10 VMs each allocated
   2 vCPUs (20 vCPUs total). Explain what steal time means at the hardware
   level (VMExit, vCPU scheduling), what the performance impact is on
   applications inside the VM, and what options you have to resolve this
   (vCPU pinning, CPU overcommit reduction, priority changes).

3. Compare container escape and VM escape attack surfaces. A malicious
   workload is running in (a) a standard Docker container on Ubuntu, (b)
   a KVM VM, (c) a Kata Container (container using KVM-backed isolation).
   For each: what kernel/hypervisor code must be vulnerable for an escape
   to succeed? Which provides the strongest isolation and why? When would
   you choose each in a multi-tenant environment?

---

### Interview Deep-Dive

**Foundational:**
Q: What is KVM and how does it differ from containers for workload isolation?
A: KVM (Kernel-based Virtual Machine) is a Linux kernel module that turns the Linux kernel into a Type-1 hypervisor by leveraging CPU hardware virtualization extensions (Intel VT-x or AMD-V). KVM provides hardware-assisted isolation at the CPU and memory level. ARCHITECTURE: KVM module (`kvm.ko`) + QEMU (userspace device emulator) = complete VM environment. The VM's CPU execution happens in hardware "VMX Non-Root mode" - guest code runs directly on the physical CPU at near-native speed. Privileged operations cause "VMExits" - hardware traps to KVM for handling. Memory isolation: EPT (Extended Page Tables) creates a hardware-enforced translation from guest physical to host physical addresses. Devices: QEMU emulates disk, network, USB etc. in userspace. CONTAINERS vs VMs: Containers share the HOST KERNEL. They use namespace isolation (PID, network, mount, etc.) and cgroups for resource limits. Containers are processes on the host with restricted views of system resources. VMs have their own kernel. A KVM VM escape requires exploiting the QEMU device model or KVM kernel module - both are complex but well-audited. A container escape requires exploiting namespace isolation, capability misconfiguration, or a kernel vulnerability accessible from a container. PRACTICAL GUIDANCE: Same-tenant workloads (your own microservices): containers are appropriate. Multi-tenant untrusted code: VMs or VM-backed containers (Kata Containers, Firecracker) provide substantially better isolation. Cloud providers: KVM VMs are the customer isolation boundary. Containers run WITHIN those VMs. Performance: containers start in milliseconds, VMs in seconds. Containers have negligible overhead; VMs have 2-5% CPU overhead (from VMExits) and 10-20% I/O overhead without virtio.

**Expert:**
Q: Explain the virtio protocol and why it achieves better performance than emulated devices in KVM.
A: Virtio (Virtual I/O) is a standardized paravirtual device interface that eliminates the overhead of hardware emulation. EMULATED DEVICE PROBLEM: Emulating an Intel e1000 NIC means simulating every register access, DMA operation, interrupt timing, and quirk of the physical device. A single network packet send: guest writes to e1000 memory-mapped registers (VMExit #1), QEMU processes the write (kernel/user context switch), guest triggers DMA (VMExit #2), QEMU copies data (another context switch), guest polls for completion or waits for interrupt (VMExit #3). 3+ VMExits per packet. Each VMExit involves: hardware state save/restore (~100-500ns), context switch to KVM kernel module, potentially to QEMU userspace. High-throughput networking: 10Gbps = millions of packets/second = millions of VMExits/second = severe CPU overhead. VIRTIO SOLUTION: Shared ring buffer (virtqueue) between guest and host. Guest and host share a ring buffer via mapped memory (no VMExit for data path). Guest: puts descriptors in virtqueue ring, writes 1 byte to notification port (ONE VMExit). Host: reads all pending descriptors from ring (processes N packets in response to 1 VMExit). Completions: host puts completions in "used ring", guest reads without VMExit. Result: 1 VMExit can trigger N packet sends (amortized cost). VHOST OPTIMIZATION: Move virtio processing from QEMU userspace to kernel (vhost module). Guest virtqueue -> kernel vhost -> host network stack. Eliminates QEMU context switches for I/O data path. SR-IOV NEXT LEVEL: Physical NIC creates multiple "virtual functions" (VFs). Guest maps VF directly into its address space. Guest sends packet by writing to VF BAR memory - NO VMExit at all. Near-bare-metal performance. BENCHMARKS PATTERN (not guarantees): emulated e1000: ~1Gbps maximum (CPU bound). virtio-net: ~8-10Gbps (limited by network, not CPU). vhost-net: ~15-20Gbps. SR-IOV: ~line rate (25/40/100Gbps depending on NIC).
