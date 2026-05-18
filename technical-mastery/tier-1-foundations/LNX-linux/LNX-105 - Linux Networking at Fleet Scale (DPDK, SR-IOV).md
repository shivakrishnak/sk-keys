---
id: LNX-105
title: "Linux Networking at Fleet Scale (DPDK, SR-IOV)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-037, LNX-092, LNX-101
used_by: LNX-106
related: LNX-037, LNX-092, LNX-101, LNX-106
tags: [dpdk, sr-iov, kernel-bypass, user-space-networking, huge-pages, virtio, vhost, vfio, pmd, poll-mode-driver, rte-eal, open-vswitch, ovs-dpdk, mellanox-rdma, roce, infiniband, af-xdp, xdp-redirect, network-function-virtualization, nfv, high-performance-networking, packet-processing, pps, latency, numa-networking, zerocopy]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 105
permalink: /technical-mastery/lnx/linux-networking-fleet-scale-dpdk-sriov/
---

## TL;DR

Standard Linux networking (kernel network stack) tops out at ~1-2 million
packets per second (Mpps) per core, with ~5-50 microsecond latency. For
10Gbps+ at line rate or sub-microsecond latency: kernel bypass technologies
are required. **DPDK** (Data Plane Development Kit) moves packet processing
entirely to user space, achieving 30+ Mpps per core with ~1 microsecond
latency by: (1) bypassing the kernel stack via VFIO driver, (2) polling the
NIC instead of interrupts (poll-mode driver), (3) huge pages for DMA (2MB
pages instead of 4KB). **SR-IOV** (Single Root I/O Virtualization) creates
hardware virtual functions from a single NIC, allowing VMs/containers direct
NIC access (no hypervisor overhead). **XDP** (with AF_XDP socket) is the
kernel-side alternative: 10-20 Mpps without leaving the kernel, useful for
packet filtering and load balancing (Cilium XDP, XDP load balancer). Use:
DPDK for NFV/firewall/VPN appliances. XDP/AF_XDP for Kubernetes networking.
SR-IOV for VMs requiring bare-metal NIC performance.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-105 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | DPDK, SR-IOV, kernel bypass, XDP, high-performance networking, huge pages, poll-mode driver, NFV |
| **Prerequisites** | LNX-037 (networking), LNX-092 (namespaces), LNX-101 (eBPF/XDP) |

---

### The Problem This Solves

**Problem 1**: A 5G mobile core network needs to process 100Gbps of user plane
traffic (packet forwarding, NAT, GTP tunneling). Standard Linux kernel network
stack: interrupt-driven, requires syscall per send/receive, processes packets
in kernel context then copies to user space. Peak: ~2M packets/second per core
at 100% CPU. For 100Gbps at 1500-byte packets: 8.3M pps required. Needs 5+
cores just for packet forwarding! With DPDK: 30M+ pps per core via poll-mode
driver and zero-copy. One core handles what previously needed 15.

**Problem 2**: A high-frequency trading firm routes financial market data through
Linux servers. Standard network stack adds 10-50 microseconds of latency (DMA,
interrupt, kernel processing, syscall, memory copy). Every microsecond costs
money in HFT. With DPDK + 10GbE SR-IOV NIC: latency drops to 1-2 microseconds
(NIC -> user-space application, no kernel involvement).

---

### Textbook Definition

**DPDK (Data Plane Development Kit)**: A set of libraries and drivers for fast
packet processing in user space. Originally developed by Intel (2010), now an
open-source Linux Foundation project. Core concept: bypass the kernel entirely
for data plane operations.

**SR-IOV (Single Root I/O Virtualization)**: A PCI-SIG standard allowing a single
physical PCIe device (NIC) to present multiple virtual functions (VFs) to the
OS/hypervisor. Each VF is a lightweight hardware-level representation of the NIC
that can be assigned directly to a VM or container.

**Key performance comparison:**

| Approach | Mpps (per core) | Latency | Kernel involvement |
|----------|----------------|---------|-------------------|
| Standard Linux | 1-2 | 5-50 us | Full stack |
| XDP | 10-20 | 1-5 us | Partial bypass |
| AF_XDP | 10-20 | 1-5 us | Minimal |
| DPDK | 30-80 | 0.5-2 us | None |
| RDMA/InfiniBand | 100+ | <1 us | None |

---

### Understand It in 30 Seconds

```bash
# === DPDK setup ===

# Install DPDK:
yum install -y dpdk dpdk-devel dpdk-tools

# Step 1: Configure huge pages (DPDK requirement)
# Huge pages: 2MB pages instead of 4KB
# DMA from NIC needs physically contiguous memory
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
# 1024 * 2MB = 2GB of huge pages for DPDK buffers

# Mount hugepage filesystem:
mkdir /mnt/huge
mount -t hugetlbfs nodev /mnt/huge

# Verify:
cat /proc/meminfo | grep -i huge
# HugePages_Total:    1024
# HugePages_Free:     1024

# Step 2: Bind NIC to DPDK PMD (not kernel driver)
# Check current NIC:
./dpdk-devbind.py --status
# 0000:03:00.0 Mellanox MT27800 (mlx5_core) - ACTIVE (kernel driver)

# Bind to VFIO-PCI (required for DPDK, allows user-space device access):
modprobe vfio-pci
./dpdk-devbind.py --bind vfio-pci 0000:03:00.0

# Verify binding:
./dpdk-devbind.py --status
# 0000:03:00.0 Mellanox MT27800 (vfio-pci) - DPDK-managed

# Step 3: Basic DPDK application (testpmd for testing)
./testpmd -l 0-3 -n 4 --socket-mem=2048 \
    -- --auto-start --forward-mode=io
# -l 0-3: use CPU cores 0-3
# -n 4: 4 memory channels
# --socket-mem=2048: 2GB from NUMA socket 0
# --forward-mode=io: I/O forwarding (benchmark mode)
# Output: Rx: 29.4 Mpps, Tx: 29.4 Mpps

# === SR-IOV setup ===

# Check if NIC supports SR-IOV:
cat /sys/bus/pci/devices/0000:03:00.0/sriov_totalvfs
# 64  <- can create up to 64 Virtual Functions

# Create 4 Virtual Functions:
echo 4 > /sys/bus/pci/devices/0000:03:00.0/sriov_numvfs

# List created VFs:
ip link show ens3f0  # physical function
# ens3f0: <...>
#     vf 0     link/ether 00:11:22:33:44:55 brd ff:ff:ff:ff:ff:ff
#     vf 1     link/ether 00:11:22:33:44:56 brd ff:ff:ff:ff:ff:ff
# ...

# Assign VF to VM or container:
# For QEMU VM:
# -device vfio-pci,host=03:10.0  (bind VF to VM via VFIO)

# For Kubernetes pod (with SRIOV Network Device Plugin):
# annotations:
#   k8s.v1.cni.cncf.io/networks: sriov-network

# === XDP / AF_XDP: kernel-side high-performance ===

# XDP program in eBPF (drop all packets from specific IP):
# Programs written in C, compiled to BPF bytecode
# Attached at driver level: fastest possible kernel processing

# AF_XDP socket: user-space receives packets via shared memory (zero-copy)
# Much simpler than DPDK: still using kernel, but zero-copy to user-space

# OVS-DPDK: Open vSwitch with DPDK for software-defined networking
# Standard OVS: kernel-based, ~2 Mpps
# OVS-DPDK: user-space, 10-30 Mpps per core

ovs-vsctl show
# Open vSwitch Bridge:
# Bridge br-dpdk
#   Port dpdk0  (DPDK-backed port, bypasses kernel)
#   Port dpdk1

# Latency comparison (same NIC):
# Standard UDP send: ~15 microseconds
# DPDK UDP send: ~1.5 microseconds
# RDMA write (RDMA NIC): ~0.5 microseconds
```

---

### First Principles

```
Why standard Linux networking has overhead:

Normal packet receive path (simplified):
  1. Packet arrives at NIC
  2. NIC DMA copies packet to kernel ring buffer
  3. NIC raises hardware interrupt
  4. CPU stops current task, saves context
  5. Kernel interrupt handler runs: acknowledge interrupt
  6. Kernel softirq: process packet in network stack
     - L2 demux (Ethernet)
     - L3 demux (IP)
     - L4 demux (TCP/UDP)
     - Deliver to socket buffer
  7. Application: read() or recvfrom() system call
     - Context switch kernel -> user
     - Copy from socket buffer to application buffer
  8. Process data

Overhead sources:
  Step 3-5: interrupt handling overhead = 1-3 microseconds
  Step 6: kernel network stack = 2-10 microseconds per packet
  Step 7: syscall + memory copy = 1-5 microseconds
  
  Total: 4-18 microseconds per packet minimum
  At 1Gbps 1500-byte packets: 83,333 pps
  At 10Gbps 1500-byte packets: 833,333 pps
  At 10Gbps 64-byte packets: 14.8 Mpps  <- interrupt storm!
  
  For 64-byte packets at 10Gbps: ~14.8 million interrupts/second
  CPU cannot handle 14.8M interrupts/second (each takes ~200 cycles)
  This is the "interrupt wall" that limits standard networking

DPDK solution: ELIMINATE the overhead sources

  Poll-mode driver (PMD):
    Instead of: interrupt when packet arrives (wait and react)
    Instead: CONTINUOUSLY poll the NIC ring buffer
    Core dedicated to polling: checks NIC 10M times/second
    No interrupt, no context switch, no softirq
    Packet available? Process immediately.
    Cost: one CPU core fully busy (100% CPU even when idle)
    Benefit: near-zero latency, maximum throughput
    
  User-space networking:
    DPDK PMD runs in user space via VFIO
    VFIO: framework allowing user-space safe access to physical devices
    No kernel involvement in data path
    No syscall, no context switch for each packet
    
  Huge pages:
    DMA from NIC requires physically contiguous memory
    Standard 4KB pages: Linux may not have 1MB contiguous for DMA
    Huge pages (2MB/1GB): preallocated contiguous memory for DMA buffers
    Also: fewer TLB (Translation Lookaside Buffer) entries for same memory
    TLB savings reduce CPU cycles for address translation
    
  NUMA awareness:
    NIC on NUMA node 0: packets arrive in NUMA node 0 memory
    If application runs on NUMA node 1: cross-NUMA memory access
    DPDK: bind application to same NUMA as NIC
    --socket-mem: allocate memory from NIC's NUMA socket

SR-IOV hardware virtualization:
  Problem: VM wants to use the NIC
  Old way: hypervisor emulates NIC -> too slow for 10/25/100Gbps
  
  SR-IOV: NIC hardware creates multiple "Virtual Functions":
  Physical Function (PF): full NIC, hypervisor/host OS manages
  Virtual Functions (VF): lightweight NIC representation
    Each VF has: own MAC address, own hardware queues, own interrupt
    VF directly accessible by guest VM via VFIO passthrough
    
  Guest VM sees VF as: real NIC (just a simpler one)
  Packets: NIC -> VF hardware queues -> VM DMA directly
  No hypervisor in the data path!
  
  SR-IOV performance: near-bare-metal NIC performance in VMs
  Use case: VMs that need 10/25Gbps NIC performance (NFS storage VMs,
            HPC clusters, telco NFV virtual network functions)

XDP as middle ground:
  XDP hook runs BEFORE Linux network stack:
  Packet arrives -> XDP hook runs in driver context
  Decision: DROP, PASS (continue to kernel), REDIRECT, TX
  No kernel stack overhead for dropped/redirected packets
  
  XDP performance: 10-20 Mpps per core (vs DPDK 30-80 Mpps)
  XDP advantage: still uses kernel interfaces (simpler ops),
                 works with existing tools (tcpdump, netfilter)
  
  AF_XDP (socket family):
  User-space application uses shared memory ring buffers
  Zero-copy: DMA directly to user-space mapped memory
  Kernel minimal involvement: just coordination, no per-packet syscall
  Performance: 10-20 Mpps to user space (DPDK-class for many use cases)
```

---

### Thought Experiment

Network function virtualization with DPDK:

```bash
# Build a software router/NAT using DPDK
# Requirements: 40Gbps throughput, <2 microsecond latency, IPv4 routing

# Hardware: 2-socket server
#   CPU: 2x 16-core Xeon (32 cores total)
#   NIC: 2x 40GbE Mellanox ConnectX-5 (SR-IOV capable)
#   RAM: 256GB DDR4
#   OS: RHEL 8

# Step 1: NUMA topology awareness
numactl --hardware
# available: 2 nodes (0-1)
# node 0 cpus: 0-15, 32-47  <- CPUs 0-15 + HT
# node 1 cpus: 16-31, 48-63
# node 0 memory: 128 GB
# node 1 memory: 128 GB

lspci -v -s 0000:03:00.0 | grep NUMA
# Node 0  <- NIC0 on NUMA node 0
# Node 1  <- NIC1 on NUMA node 1

# Step 2: Huge page allocation (per NUMA node)
echo 4096 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
echo 4096 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
# 4096 * 2MB = 8GB per NUMA node = 16GB total for DPDK buffers

# Step 3: CPU isolation (prevent OS from scheduling on DPDK cores)
# /etc/default/grub:
# GRUB_CMDLINE_LINUX="... isolcpus=2-15,18-31 nohz_full=2-15,18-31"
# Core 0: kernel/OS on NUMA0, Core 16: kernel/OS on NUMA1
# Cores 2-15: DPDK on NUMA0, Cores 18-31: DPDK on NUMA1

# Step 4: DPDK application (l3fwd - Layer 3 forwarding)
./l3fwd \
    -l 2-7 \                    # use cores 2-7 (NUMA node 0 side)
    -n 4 \                      # 4 memory channels
    --socket-mem=4096,4096 \    # 4GB per NUMA socket
    -- \
    -p 0x3 \                    # port bitmask: ports 0 and 1
    --config="(0,0,2),(0,1,3),(1,0,4),(1,1,5)"
    # port 0, queue 0 -> core 2
    # port 0, queue 1 -> core 3
    # port 1, queue 0 -> core 4
    # port 1, queue 1 -> core 5

# Step 5: Verify performance
# Watch Rx/Tx statistics:
# Port 0: Rx-pps=18,234,567  Tx-pps=18,234,200  <- ~18M pps on one port
# Port 1: Rx-pps=18,150,234  Tx-pps=18,150,100
# Total: ~36M pps = 40Gbps at ~1100 byte average packet size!

# Latency measurement with DPDK latency benchmark:
# E2E latency: min=892ns, avg=1234ns, max=4567ns, p99=2100ns
# 892ns to 2.1 microseconds -> 10-50x improvement over kernel stack!
```

---

### Mental Model / Analogy

```
Standard Linux networking = traditional postal service:

Packet arrives = letter arrives at post office
Interrupt = bell rings (someone comes to check every time a letter arrives)
Kernel network stack = postal workers sort: zip code -> street -> name
Syscall + copy = customer walks to counter, postal worker hands over letter

Overhead: interrupt response time + sorting + customer service time
Volume limit: number of postal workers * speed of manual sorting
At high volume: workers overwhelmed, letters pile up (packet drops)

DPDK = automated sorting facility:

Poll-mode driver = robot that CONTINUOUSLY watches the incoming mail conveyor:
  Robot never sleeps: checks conveyor 10M times/second
  Letter arrives -> robot grabs it immediately (no bell, no delay)
  One robot = one CPU core dedicated to watching

User-space = postal facility inside the customer's building:
  Customer's building is adjacent to post office conveyor
  No walking to counter: letter goes directly to customer's desk
  No postal service involvement (no kernel overhead)

Huge pages = industrial-size cargo containers:
  Standard pages (4KB): small boxes, many separate DMA transactions
  Huge pages (2MB): big containers, one DMA for 512 small boxes
  Fewer DMA operations = less CPU overhead

SR-IOV = post office rents counters INSIDE customer buildings:
  Standard: customer comes to post office (hypervisor mediated)
  SR-IOV: post office sets up mini-counter in customer's lobby
  Mail delivered directly, no trip to main office
  Customer (VM) gets near-real post office speed
  
XDP = smart mail room at building entrance:
  Still uses the post office (kernel)
  BUT: smart room at door drops known junk mail BEFORE it goes upstairs
  Reduces work for upstairs office (reduces kernel processing)
  Faster than standard sorting but slower than DPDK's private conveyor

RDMA (InfiniBand) = direct telepathy between buildings:
  No postal service at all
  Remote machine writes DIRECTLY to your RAM
  Your CPU not involved until after data arrives
  Fastest possible (<1 microsecond)
  But: requires special cables, same vendor hardware often

AF_XDP = express window at post office:
  Still the post office (kernel) but dedicated express window
  Shared memory ring: post office and customer share a bin
  Customer grabs letters directly from bin (zero-copy)
  No individual letter handing (no per-packet syscall)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Why standard Linux networking tops out. The interrupt problem at high packet
rates. DPDK concept: bypass kernel, poll NIC in user space. SR-IOV: hardware
VFs for direct NIC access in VMs. XDP: kernel-level early drop/redirect.
Use cases: HFT latency, telco NFV, DDoS mitigation.

**Level 2:**
DPDK setup: huge pages, VFIO binding, testpmd. Poll-mode driver concept.
SR-IOV setup: creating VFs, assigning to VMs. XDP attach points: native,
generic, offload. AF_XDP socket for user-space zero-copy. OVS-DPDK for
software-defined networking. NUMA awareness for NIC-CPU affinity.

**Level 3:**
DPDK memory model: mempool, mbuf (message buffer structure). DPDK ring buffers:
lock-free SPSC/MPMC queues. Multiple queue configuration: RSS (Receive Side
Scaling) to distribute packets across cores. CPU isolation with isolcpus
for DPDK cores. DPDK pipeline model vs run-to-completion. DPDK crypto library
(hardware AES acceleration). OVS-DPDK bond modes.

**Level 4:**
DPDK PMD internals: register-level NIC programming, DMA descriptor rings.
RDMA/RoCE architecture: Queue Pairs, Work Requests, Completion Queues. RDMA
programming with libibverbs. Smart NICs (DPU - Data Processing Units):
offload packet processing to NIC ASIC (Mellanox BlueField). P4 programmable
NICs: define forwarding pipeline in P4 language. eBPF at XDP with AF_XDP:
combined approach where XDP filters and AF_XDP receives selected packets.
IOMMU/VFIO security model for user-space device access.

**Level 5:**
DPDK in 5G vRAN/vCU/vDU architectures: CPRI/eCPRI fronthaul processing, strict
timing requirements (O-RAN specifications). DOCA (Data Center Infrastructure-on-a-Chip
Architecture): BlueField DPU programming model. Network disaggregation: commodity
server + DPDK replacing purpose-built networking hardware. Kernel Bypass for
databases: SPDK (Storage Performance Development Kit) - same bypass principle
for NVMe storage. Kernel TLS: TLS offload to NIC. SmartNIC programmability
comparison: P4, eBPF, FPGA, ASIC for different flexibility/performance trade-offs.

---

### Code Example

**BAD - naive high-volume packet processing in Python (kernel stack):**
```python
# BAD: Python socket for high-throughput packet processing
import socket

# Processing 1M packets/second with this code is impossible:
# Each recvfrom() = one syscall = ~200 nanoseconds minimum
# Plus: kernel network stack processing = another 1-5 microseconds
# Plus: Python GIL, Python interpreter overhead
# Maximum realistic throughput: ~100K packets/second (10x too slow)

sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
sock.bind(("eth0", 0))

packet_count = 0
while True:
    data, addr = sock.recvfrom(65535)  # one syscall per packet!
    packet_count += 1
    # Process packet...
# At 1Gbps with 64-byte packets: 14.8M pps required
# This code: ~100K pps -> 148x too slow!

# BAD: raw socket send loop (kernel path):
# Each send() = context switch user->kernel->user = ~1-5 microseconds
# For 10Gbps requires 14.8M sends/second: 14.8 seconds/second of overhead!
```

```bash
# GOOD: DPDK-based packet processing (C application)
# This is necessarily C code - DPDK is a C library
# Showing the key patterns that make it performant

# 1. DPDK initialization (one-time setup):
rte_eal_init(argc, argv);
# ^ Initializes huge pages, NUMA-aware allocators, VFIO device access

# 2. Create packet buffer pool from huge pages:
mbuf_pool = rte_pktmbuf_pool_create(
    "MBUF_POOL",
    NUM_MBUFS,      # number of buffers (e.g., 8192)
    MBUF_CACHE_SIZE, # per-core cache size (reduce contention)
    0,               # private data size
    RTE_MBUF_DEFAULT_BUF_SIZE,
    rte_socket_id()  # allocate from SAME NUMA as NIC
);
# ^ All buffers pre-allocated from huge pages
# ^ DMA-compatible: NIC can directly write into these buffers

# 3. Poll-mode receive loop (runs continuously on dedicated core):
while (1) {
    // Receive burst of up to 32 packets from port 0, queue 0:
    nb_rx = rte_eth_rx_burst(port_id, queue_id,
                              rx_pkts, BURST_SIZE);  // BURST_SIZE=32
    
    // No interrupt, no syscall: just read NIC ring buffer
    // If nb_rx == 0: NIC has no packets (still polling, wasting CPU)
    // This "wasted" CPU is the cost of near-zero latency
    
    for (i = 0; i < nb_rx; i++) {
        // Process each packet: pure user-space memory operations
        struct rte_ether_hdr *eth_hdr = rte_pktmbuf_mtod(
            rx_pkts[i], struct rte_ether_hdr *);
        // Zero copy: rx_pkts[i] points directly to DMA buffer!
        // No copy from kernel to user space!
        
        // Route/forward/NAT/filter...
    }
    
    // Transmit in burst (amortizes per-call overhead):
    rte_eth_tx_burst(tx_port, queue_id, tx_pkts, nb_tx);
}

# Performance result: 30+ million packets/second per core
# Latency: ~1.5 microseconds NIC-to-application
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "DPDK is only needed for 100Gbps networks" | DPDK (and kernel bypass in general) is useful when you need sub-microsecond latency OR when you need to process millions of small packets efficiently, regardless of total bandwidth. Example: high-frequency trading at 10Gbps but processing 64-byte UDP market data packets at 14.8 Mpps - the kernel interrupt storm at this packet rate (14.8M interrupts/second) saturates a CPU core regardless of bandwidth. Standard kernel: one core can handle ~1-2 Mpps at 100% CPU. DPDK: one core handles 30 Mpps at 100% CPU. For applications needing <10Gbps but processing millions of small packets: DPDK is appropriate. Also: latency. Financial services use DPDK for sub-microsecond latency even at <1Gbps of traffic because every microsecond matters. |
| "SR-IOV is only for bare-metal servers, not useful in cloud environments" | SR-IOV is exactly how cloud providers deliver high-performance networking to VMs. AWS Enhanced Networking (ENA) and Intel VF driver, Azure Accelerated Networking, and GCP VirtIO-Net with SR-IOV all use SR-IOV or similar PCIe passthrough technologies to deliver near-bare-metal NIC performance to VMs. When you enable "Enhanced Networking" on an AWS instance: you're enabling SR-IOV. The VM gets direct access to hardware NIC queues (bypassing hypervisor in the data path), which is why AWS Enhanced Networking achieves 25Gbps+ with <100 microsecond latency vs the ~5-10Gbps max of non-enhanced networking. Container environments also use SR-IOV: Kubernetes SRIOV Network Device Plugin allows pods to request SR-IOV VFs directly, enabling pod-to-pod networking at near-NIC speeds. |
| "XDP is just iptables replacement" | XDP (and eBPF) can REPLACE iptables for some use cases (packet filtering, NAT), but the capability is much broader. XDP operates at the earliest possible kernel hook (before memory allocation, before iptables), making it dramatically faster: XDP can drop packets at 10-20 Mpps, while iptables drop rate is ~1-2 Mpps. But XDP also enables: load balancing (Cilium's DSR/DNAT uses XDP), DDoS mitigation (drop spoofed SYN flood before kernel processes it), traffic shaping, tunnel encapsulation/decapsulation. AF_XDP extends XDP to allow user-space applications to receive filtered packets with zero-copy. Use case: a network monitoring application uses XDP to filter only packets matching specific flows, and receives only those via AF_XDP socket - avoiding the cost of delivering ALL packets to user space. |
| "DPDK applications are difficult to write and require NIC vendor expertise" | DPDK provides high-level APIs that abstract NIC-specific details. Writing a DPDK packet forwarding application requires understanding the DPDK API, but not NIC register-level programming. DPDK includes: ready-to-use example applications (l2fwd, l3fwd, ipsec-secgw, vhost), extensive documentation, PMD abstractions (same code works with Intel, Mellanox, Broadcom NICs). Modern frameworks further simplify: SPDK (storage), VPP (Vector Packet Processing), OVS-DPDK, FD.io. In practice: most networking companies using DPDK are not writing from scratch - they're customizing example applications or using VPP as a framework. The expertise required is network engineering + C programming, not NIC driver development. Cloud-native alternatives (Cilium XDP, AWS VPC) abstract DPDK entirely, so application developers never see it. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: DPDK not achieving expected performance ===
# testpmd shows only 5Mpps instead of expected 30Mpps

# Diagnosis 1: NUMAnode mismatch
# NIC on NUMA 0, DPDK using memory from NUMA 1:
numactl -H  # check NUMA topology
lspci -v -s 0000:03:00.0 | grep NUMA
# Node 0  <- NIC is on NUMA 0

# Verify DPDK is using correct socket memory:
./testpmd -l 0-3 --socket-mem=2048,0 ...
#                                    ^ 0 on NUMA1: don't allocate there
# Wrong: --socket-mem=0,2048 (allocates from NUMA1, NIC is on NUMA0!)

# Diagnosis 2: Huge pages not configured correctly:
cat /proc/meminfo | grep Huge
# HugePages_Total: 1024
# HugePages_Free:  0  <- all used! Or no huge pages for DPDK

# Diagnosis 3: IRQ affinity (kernel stealing CPU):
# If DPDK cores are getting interrupted by other IRQs:
cat /proc/interrupts | grep "eth0"
# 12345: 56789 0 0 2 0 0 3 0... eth0-rx-0
# ^ if non-zero on DPDK cores: kernel IRQs competing

# Fix: pin IRQs to non-DPDK cores:
# /proc/irq/12345/smp_affinity: set to bitmask of NON-DPDK cores

# Diagnosis 4: CPU frequency scaling:
cat /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
# powersave <- WRONG for DPDK! Must be performance or set to max

echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# === Failure: SR-IOV VF not visible in guest ===
# VM started with SR-IOV VF passthrough but network not working

# On host: verify VF is created:
cat /sys/bus/pci/devices/0000:03:00.0/sriov_numvfs
# 0  <- VFs not created! Must set > 0

echo 4 > /sys/bus/pci/devices/0000:03:00.0/sriov_numvfs

# Verify IOMMU enabled (required for VFIO):
dmesg | grep -i iommu
# [  0.001234] DMAR: IOMMU enabled
# If not: enable in BIOS (VT-d on Intel, AMD-Vi on AMD)
# And in kernel parameters: intel_iommu=on (or amd_iommu=on)
cat /proc/cmdline | grep iommu
# intel_iommu=on  <- required

# Verify VF is bound to vfio-pci:
./dpdk-devbind.py --status | grep vfio
# 0000:03:10.0 'VF' drv=vfio-pci  <- VF bound, ready for passthrough
```

---

### Related Keywords

**Foundational:**
LNX-037 (networking), LNX-092 (namespaces), LNX-101 (eBPF)

**Builds on this:**
LNX-106 (container platform architecture)

**Related:**
LNX-106 (container platform on Linux)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `./dpdk-devbind.py --status` | Show NIC DPDK binding status |
| `./dpdk-devbind.py --bind vfio-pci BDF` | Bind NIC to DPDK |
| `echo 2048 > /sys/kernel/mm/hugepages/.../nr_hugepages` | Configure huge pages |
| `cat /proc/meminfo | grep Huge` | Verify huge page availability |
| `echo N > /sys/bus/pci/devices/BDF/sriov_numvfs` | Create N SR-IOV VFs |
| `cat /sys/bus/pci/devices/BDF/sriov_totalvfs` | Max VFs supported |
| `./testpmd ... --forward-mode=io` | DPDK performance benchmark |
| `numactl --hardware` | Show NUMA topology |

**3 things to remember:**
1. DPDK requires huge pages (2MB) for NIC DMA. Without huge pages, DPDK cannot allocate contiguous memory for packet buffers. Configure with `echo N > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages` before starting DPDK.
2. NUMA affinity is critical: DPDK memory allocation and CPU cores MUST be on the same NUMA node as the NIC. Cross-NUMA access adds ~100ns latency per memory access, destroying DPDK's latency advantage. Use `--socket-mem=N,0` to allocate only from NIC's NUMA node.
3. SR-IOV requires IOMMU (intel_iommu=on or amd_iommu=on in kernel parameters). Without IOMMU, VFs cannot be safely passed through to VMs. Enable VT-d/AMD-Vi in BIOS and add the kernel parameter.

---

### Transferable Wisdom

DPDK's bypass philosophy transfers broadly: SPDK (Storage Performance
Development Kit) applies the same concept to NVMe storage (bypass kernel
filesystem stack for databases), io_uring (reduced syscall overhead for I/O
by batching operations), Java NIO off-heap buffers (bypass GC and OS copy for
network I/O), kernel TLS (offload TLS to NIC, bypass OpenSSL in kernel path).
The poll-mode driver concept (dedicated thread polling vs interrupt-driven) is
the same as: event loop model in Node.js/Nginx (single thread polling vs
multi-thread blocking I/O), busy-waiting vs condition variable in concurrent
programming (CPU wasted for lowest latency), Kafka broker I/O thread polling.
SR-IOV's "give hardware access directly to consumer" pattern is: vDPA (virtual
Data Path Acceleration), SmartNIC workload offload, and GPU passthrough for ML
training. NUMA awareness in DPDK is the same challenge as: database NUMA-aware
memory allocation (PostgreSQL huge_pages, Oracle NUMA), JVM heap NUMA binding
(-XX:+UseNUMA), HPC MPI process placement on NUMA nodes. The huge page
requirement (physically contiguous DMA-capable memory) maps to: GPU pinned
memory for CUDA zero-copy transfers, DMA in kernel drivers, RDMA memory
registration requirements.

---

### The Surprising Truth

The Linux kernel's network stack, which DPDK bypasses entirely, handles
the entirety of the world's internet traffic for most of its history - and
does so efficiently enough that most workloads never need anything more.
The kernel stack processes 1-2 million packets per second per core, which
translates to roughly 12Gbps of 1500-byte Ethernet frames per core. A
typical web server with 8 cores can push 96Gbps of traffic through the
kernel stack - far beyond what most servers ever need.

DPDK becomes necessary only at the extremes: packet rates above 2 Mpps per
core, or latency requirements below 10 microseconds. In the entire internet
infrastructure, perhaps 5% of servers require DPDK. But those 5% are the
most critical: the routers, firewalls, load balancers, and 5G core network
functions that process traffic for the other 95%. DPDK is the invisible
infrastructure that makes modern telecommunications, cloud networking, and
high-frequency trading possible - most developers will never write a line
of DPDK code, but the systems they build run on infrastructure that depends
on it.

---

### Mastery Checklist

- [ ] Understands why standard Linux networking tops out and what the overhead sources are
- [ ] Can explain the three approaches: DPDK (user-space bypass), SR-IOV (hardware VFs), XDP (kernel early hook)
- [ ] Can configure huge pages and bind a NIC to DPDK for testing
- [ ] Understands NUMA awareness requirements for DPDK applications
- [ ] Can explain when DPDK vs XDP vs standard Linux networking is the right choice

---

### Think About This

1. Design the networking architecture for a telco 5G mobile core running on
   commodity x86 servers. Requirements: 100Gbps user plane, <2 microsecond
   latency for GTP-U tunnel forwarding, support for 1 million simultaneous
   PDU sessions. How would you partition the workload across DPDK cores?
   What NIC features are required? How would you handle the control plane
   (signaling) vs data plane (forwarding) differently? What is your high
   availability strategy when a DPDK process crashes?

2. A security team wants to deploy DDoS mitigation that can absorb a 100Gbps
   volumetric attack. They debate: (a) hardware DDoS appliance (fixed pipeline),
   (b) DPDK on commodity servers (flexible, programmable), (c) XDP/eBPF in
   kernel (simpler ops, integrated with Linux). Compare these approaches for:
   performance ceiling, programmability (can you update mitigation rules in
   real-time?), operational complexity, and total cost. What factors determine
   which approach is appropriate for a given organization?

3. Cloud providers use SR-IOV internally to deliver "Enhanced Networking" to
   customers. But customers who deploy Kubernetes on cloud VMs then add
   another networking layer (Cilium, Calico, flannel) on top of the already-
   high-performance SR-IOV network. Is this double-abstraction wasteful?
   What is the performance overhead of Kubernetes pod networking on top of
   SR-IOV? When does it make sense to expose SR-IOV VFs directly to pods
   (SRIOV Network Device Plugin) vs using standard Kubernetes CNI networking?

---

### Interview Deep-Dive

**Foundational:**
Q: Why does standard Linux networking become a bottleneck for high-performance networking, and what are the alternatives?
A: KERNEL STACK OVERHEAD SOURCES: Standard Linux networking has four sources of overhead: (1) INTERRUPT OVERHEAD: When a packet arrives, the NIC raises a hardware interrupt. CPU must stop current execution, save context, run interrupt handler, return. This context switch takes 1-3 microseconds. At 10Gbps with 64-byte packets: 14.8 million interrupts/second. Each interrupt is ~200 CPU cycles. At 3GHz: 14.8M * 200 cycles = 986 billion cycles/second needed just for interrupts - more than the CPU has! Linux uses NAPI (New API) to mitigate this with interrupt coalescing, but this adds latency. (2) KERNEL NETWORK STACK: Every packet traverses Ethernet, IP, UDP/TCP demux layers in the kernel. Approximately 2-10 microseconds per packet. (3) SYSCALL + COPY: Application reads with recv(). Kernel-to-user context switch: ~200ns. Memory copy (kernel buffer to user buffer): bandwidth and CPU overhead. (4) MEMORY ALLOCATION: Small 4KB pages require many TLB entries and DMA scatter-gather. THREE HIGH-PERFORMANCE ALTERNATIVES: (1) DPDK (Data Plane Development Kit): poll-mode driver runs in user space, NIC bound to VFIO driver, application continuously polls NIC ring buffer instead of using interrupts. Achieves 30-80 Mpps per core. Cost: one CPU core 100% busy even when idle (polling). Use for: network functions, HFT, anywhere latency <2 us or >10 Mpps required. (2) XDP (eXpress Data Path): eBPF program runs in NIC driver context (before kernel stack). Can drop/redirect 10-20 Mpps without kernel processing. Use for: DDoS mitigation, load balancing, Kubernetes networking (Cilium). AF_XDP extends to zero-copy user-space receive. (3) SR-IOV: NIC creates hardware Virtual Functions assigned directly to VMs/containers. VM accesses NIC hardware queues directly, no hypervisor in data path. Use for: VMs requiring near-bare-metal NIC performance. DECISION FRAMEWORK: <2 Mpps or latency >10us tolerance: standard Linux is fine. 2-20 Mpps or 1-10 us latency: XDP/AF_XDP. >20 Mpps or <1 us latency: DPDK. VM NIC performance: SR-IOV.

**Expert:**
Q: Explain NUMA awareness in DPDK and why incorrect NUMA configuration can completely negate DPDK's performance benefits.
A: NUMA ARCHITECTURE CONTEXT: Modern multi-socket servers have Non-Uniform Memory Access (NUMA) topology. In a 2-socket system: Socket 0 (NUMA node 0) has CPUs 0-15 + local RAM (128GB). Socket 1 (NUMA node 1) has CPUs 16-31 + local RAM (128GB). Key property: accessing local NUMA memory takes ~60ns. Accessing remote NUMA memory (cross-socket) takes ~130-180ns. That's ~2-3x higher latency for remote access. PCIE DEVICES AND NUMA: Every PCIe device (NIC) is physically connected to one CPU socket, placing it in that NUMA node. DMA from the NIC writes to NUMA-local memory first. If packet buffers are in NUMA node 0 and NIC is on node 0: DMA writes to local memory, CPU 0 reads local memory = fast. WHAT HAPPENS WITH WRONG NUMA: If DPDK allocates packet buffers from NUMA node 1 but NIC is on node 0: (1) NIC DMA writes to NUMA 1 memory (crosses QPI/UPI interconnect: +60-100ns per 64-byte cache line). (2) CPU on NUMA 0 reads packet buffer from NUMA 1 (another cross-NUMA access: +60-100ns). (3) For 30M pps: 30M * (100ns + 100ns) = 6 seconds of cross-NUMA overhead PER SECOND! CPU cannot keep up. Effective throughput: drops from 30 Mpps to <10 Mpps. HOW TO GET NUMA CONFIGURATION RIGHT: (1) Identify NIC's NUMA node: `lspci -v -s <BDF> | grep NUMA`. (2) Allocate DPDK memory from same NUMA: `--socket-mem=2048,0` (node0=2GB, node1=0). (3) Pin DPDK threads to CPUs on same NUMA: `-l 0-7` (CPUs 0-7, assuming they're all NUMA 0). (4) Verify with: `numastat` (should show NIC NUMA node matching DPDK allocation NUMA). VERIFICATION: testpmd showing expected Mpps (30+) = NUMA is correct. testpmd showing <10 Mpps = likely NUMA misconfiguration. Check: `numastat -p <pid>` for DPDK process - should show local accesses >> foreign accesses. This is the most common DPDK performance issue encountered in practice: engineers configure DPDK correctly but forget to verify NUMA alignment, getting 1/3 of expected performance.
