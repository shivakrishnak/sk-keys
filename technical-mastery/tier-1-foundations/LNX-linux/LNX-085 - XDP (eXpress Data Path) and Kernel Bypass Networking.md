---
id: LNX-085
title: "XDP (eXpress Data Path) and Kernel Bypass Networking"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-073, LNX-084
used_by: LNX-105
related: LNX-073, LNX-084, LNX-091, LNX-101
tags: [xdp, kernel-bypass, dpdk, af-xdp, ebpf-networking, packet-processing, high-performance-networking, userspace-networking, rx-offload, nfp, tc-bpf, xdp-pass, xdp-drop, xdp-redirect, zero-copy]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 85
permalink: /technical-mastery/lnx/xdp-kernel-bypass-networking/
---

## TL;DR

**XDP (eXpress Data Path)** runs eBPF programs at the EARLIEST point in
the NIC driver - before any kernel buffer allocation, sk_buff creation, or
protocol stack processing. Packet handling at 10-100 Mpps with sub-microsecond
latency. XDP actions: `XDP_PASS` (normal kernel stack), `XDP_DROP` (drop in
kernel, 14 Mpps DDoS mitigation), `XDP_REDIRECT` (redirect to another
interface/CPU/AF_XDP socket), `XDP_TX` (bounce packet back out same NIC).
**AF_XDP** sockets: zero-copy packet delivery to userspace using shared
UMEM. **DPDK**: alternative kernel-bypass via UIO/VFIO driver - process
runs an NIC driver in userspace, polling mode, 70+ Mpps per core. Use XDP
for in-kernel eBPF logic. Use DPDK for custom userspace packet processing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-085 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | XDP, kernel bypass, DPDK, AF_XDP, eBPF networking, packet processing, DDoS mitigation, zero-copy |
| **Prerequisites** | LNX-073 (eBPF), LNX-084 (Network performance) |

---

### The Problem This Solves

**Problem 1**: DDoS attack with 10M packets/second of SYN flood. Normal
Linux network stack: each packet allocates an `sk_buff` (600+ bytes), goes
through IP routing, TCP, and reaches the application. At 10 Mpps: 6GB/sec
of sk_buff allocation alone. CPU fully saturated just doing stack processing.
With XDP: an eBPF program runs in the NIC driver before ANY kernel allocation.
It inspects the packet header, identifies SYN flood pattern, returns `XDP_DROP`.
Cost: ~50 ns per packet (instruction decode + return). 14+ Mpps drop rate per
core. DDoS mitigated without impacting legitimate traffic.

**Problem 2**: A financial exchange needs to process market data at 70+ Mpps
(millions of packets per second) with deterministic sub-100ns latency.
The Linux network stack (sk_buff path, NAPI, IRQ) adds 10-50 microseconds
of jitter. DPDK: moves the NIC driver entirely to userspace. A single process
in busy-poll mode reads packets directly from NIC ring buffers, processes
them in a tight loop. No interrupt latency, no kernel context switch, no
sk_buff. 70+ Mpps at < 1 microsecond latency.

---

### Textbook Definition

**XDP (eXpress Data Path)**: An eBPF-based framework (kernel 4.8, 2016)
that allows running custom packet processing logic at the NIC driver level.
XDP programs execute at the first opportunity after a packet arrives, before
the kernel allocates an `sk_buff`. Three XDP hook points: native XDP (in NIC
driver, fastest), offloaded XDP (on NIC SmartNIC hardware, zero CPU cost),
generic XDP (after sk_buff allocation, fallback for unsupported NICs).

**XDP return codes:**
| Code | Meaning |
|------|---------|
| `XDP_PASS` | Pass packet to normal kernel stack |
| `XDP_DROP` | Drop packet (no memory freed, just discarded) |
| `XDP_TX` | Bounce packet out the same interface |
| `XDP_REDIRECT` | Redirect to different interface, CPU, or AF_XDP socket |
| `XDP_ABORTED` | Drop + tracepoint (for debugging) |

**AF_XDP**: A specialized socket type that receives packets via XDP_REDIRECT
without passing through the kernel stack. Uses a shared UMEM (user memory)
ring buffer. Packet data is placed directly into application-controlled memory
(zero-copy from NIC to application).

**DPDK (Data Plane Development Kit)**: A userspace framework for high-performance
packet processing. Moves NIC driver to userspace via UIO (Userspace I/O) or
VFIO. Eliminates kernel crossings for the data path. Busy-polls NIC in an
infinite loop. Uses huge pages, NUMA-aware memory, and lock-free queues.
Used by: OVS-DPDK (Open vSwitch), VPP (Vector Packet Processor), Suricata
IDS, most telco NFV platforms.

---

### Understand It in 30 Seconds

```bash
# === XDP: load a simple packet counter ===

# Write an XDP program (kernel headers required):
cat > xdp_counter.bpf.c << 'EOF'
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u64);
} pkt_count SEC(".maps");

SEC("xdp")
int count_packets(struct xdp_md *ctx) {
    __u32 key = 0;
    __u64 *count;
    
    count = bpf_map_lookup_elem(&pkt_count, &key);
    if (count)
        __sync_fetch_and_add(count, 1);
    
    return XDP_PASS;   // pass all packets to kernel stack
}

char _license[] SEC("license") = "GPL";
EOF

# Compile and load:
clang -O2 -target bpf -c xdp_counter.bpf.c -o xdp_counter.bpf.o
ip link set dev eth0 xdp obj xdp_counter.bpf.o sec xdp

# Verify XDP program is attached:
ip link show eth0
# eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 xdp ...
#   link/ether 00:11:22:33:44:55 brd ff:ff:ff:ff:ff:ff
#   prog/xdp id 42 tag a04f5eef06a7f555  <- XDP program attached

# Remove XDP program:
ip link set dev eth0 xdp off

# === XDP DDoS drop: drop all UDP packets ===
# Common use case: drop a specific attack pattern
cat > xdp_drop_udp.bpf.c << 'EOF'
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <bpf/bpf_helpers.h>

SEC("xdp")
int drop_udp(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    struct ethhdr *eth = data;
    
    // Bounds check required by BPF verifier:
    if (data + sizeof(*eth) > data_end)
        return XDP_PASS;
    
    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;
    
    struct iphdr *iph = data + sizeof(*eth);
    if ((void *)iph + sizeof(*iph) > data_end)
        return XDP_PASS;
    
    if (iph->protocol == IPPROTO_UDP)
        return XDP_DROP;  // drop all UDP packets
    
    return XDP_PASS;
}
char _license[] SEC("license") = "GPL";
EOF

# === XDP with bpftool ===
# Load XDP program:
bpftool prog load xdp_drop_udp.bpf.o /sys/fs/bpf/xdp_drop_udp \
    type xdp
bpftool net attach xdp id $(bpftool prog show name drop_udp -j | jq .[0].id) \
    dev eth0

# View attached programs:
bpftool net list dev eth0
# xdp:
#     eth0(2) driver id 42

# XDP stats (via perf events):
bpftool prog show id 42
# 42: xdp  name drop_udp  tag a1b2c3d4e5f6...
#     loaded_at 2024-11-01T10:00:00+0000  uid 0
#     xlated 160B  jited 98B  memlock 4096B

# === Userspace: check if NIC supports native XDP ===
ethtool -i eth0 | grep driver
# driver: i40e   <- Intel i40e: supports native XDP
# driver: virtio_net  <- virtio-net: supports XDP in kernel 4.14+
# driver: e1000   <- older emulated: generic XDP only (slower)

# === DPDK: quick check ===
# List DPDK-bound NICs:
dpdk-devbind.py --status
# Network devices using DPDK-compatible driver
# 0000:00:05.0 'Virtio network device 1000' drv=vfio-pci unused=virtio-pci

# Bind a NIC to DPDK:
dpdk-devbind.py --bind=vfio-pci 0000:00:05.0

# Basic DPDK l2fwd example:
dpdk-l2fwd -- -p 0x3   # enable ports 0 and 1, L2 forwarding
```

---

### First Principles

**XDP packet processing path vs normal kernel path:**
```
Normal kernel network receive path:
  NIC DMA packet -> NIC ring buffer
  Hardware interrupt -> CPU context switch to softirq
  NAPI poll:
    alloc sk_buff (600+ bytes heap allocation)
    copy packet to sk_buff
    Ethernet driver processing
    IP stack (routing lookup, netfilter hooks)
    TCP/UDP stack
    Socket receive buffer
    wake application
  
  Cost per packet: ~1-3 microseconds
  Bottleneck: sk_buff allocation + memory copies

XDP path:
  NIC DMA packet -> NIC ring buffer
  Hardware interrupt -> CPU context switch to softirq  <- same
  NIC driver (early hook, before sk_buff allocation):
    Execute XDP eBPF program:
      Read packet header (direct pointer, no copy)
      Make decision (50-200 ns total)
    
    XDP_DROP: return, packet discarded (no allocation happened!)
    XDP_PASS: continue normal sk_buff path
    XDP_TX: bounce packet back out same NIC
    XDP_REDIRECT: redirect to another queue/CPU
  
  Cost per dropped packet: ~50-100 ns  (vs 1-3 us normal path)
  Cost per forwarded packet: ~200-500 ns (vs 1-3 us normal path)
  
  Key insight: XDP_DROP at ~10 ns overhead + 40 ns driver hook = 50 ns
               Normal sk_buff alloc alone = 200+ ns
               XDP avoids the expensive allocation for dropped packets

XDP offload (SmartNIC):
  XDP program compiled to native NIC instruction set
  Runs ON THE NIC HARDWARE
  CPU is not involved AT ALL for dropped packets
  Available on: Netronome NFP, Mellanox ConnectX-5+
  Cost per dropped packet: 0 CPU cycles (NIC does it)

AF_XDP zero-copy path:
  
  Application allocates UMEM (user memory, registered with kernel):
    UMEM = large pre-allocated buffer pool
    Registered via setsockopt(AF_XDP_UMEM)
    Kernel and userspace share this memory
  
  AF_XDP socket created, linked to XDP program:
    XDP program: bpf_redirect_map() -> AF_XDP socket
    Kernel places packet data DIRECTLY into UMEM
    (no sk_buff allocation, no copy)
  
  Application reads from UMEM via ring buffer:
    RX ring: kernel fills with packet offsets in UMEM
    Application reads offset, processes raw packet data
    Returns buffer to FILL ring
  
  Zero-copy = one DMA (NIC to UMEM) + ring update
  vs normal: DMA + sk_buff alloc + copy + socket copy = 3-4 memory ops

DPDK architecture:
  Bind NIC to VFIO (bypass kernel NIC driver):
    echo 1 > /sys/bus/pci/devices/0000:00:05.0/driver_override
    dpdk-devbind.py --bind=vfio-pci 0000:00:05.0
    Now: no kernel IP/TCP/Ethernet stack for this NIC
  
  DPDK PMD (Poll Mode Driver) in userspace:
    C library that directly reads NIC ring buffers via mmap of VFIO
    No interrupt: tight polling loop
    while (true) {
        nb_rx = rte_eth_rx_burst(port, queue, mbufs, MAX_BURST);
        // process mbufs: routing, encapsulation, etc.
        rte_eth_tx_burst(port, queue, tx_mbufs, nb_tx);
    }
  
  Performance: 70+ Mpps per core (vs 1-10 Mpps with XDP)
  Latency: < 1 microsecond per packet
  CPU cost: 1 core at 100% per NIC queue (polling)
  Memory: huge pages required (2MB or 1GB pages for mbuf pools)
```

---

### Thought Experiment

Building a DDoS mitigation with XDP:

```bash
# Scenario: 20 Gbps UDP flood attack targeting a single IP:port

# Step 1: Observe the attack:
# Network interface RX errors:
ethtool -S eth0 | grep -i "drop\|miss"
# rx_miss: 1234567   <- NIC dropping packets (ring full)

# CPU usage:
top  # or mpstat -P ALL 1
# CPU 0: 100% si (softirq) <- overwhelmed by interrupts

# Step 2: Write XDP program to identify and drop attack traffic:
cat > ddos_mitigation.bpf.c << 'EOF'
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

// Map: blocked source IPs (set by userspace control plane)
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 100000);
    __type(key, __u32);   // source IP
    __type(value, __u64); // packet count
} blocked_ips SEC(".maps");

// Stats map:
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 2);
    __type(key, __u32);
    __type(value, __u64);
} stats SEC(".maps");  // [0]=passed [1]=dropped

SEC("xdp")
int ddos_filter(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    
    // Parse Ethernet header:
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) return XDP_PASS;
    if (eth->h_proto != bpf_htons(ETH_P_IP)) return XDP_PASS;
    
    // Parse IP header:
    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end) return XDP_PASS;
    
    // Check blocklist:
    __u64 *blocked = bpf_map_lookup_elem(&blocked_ips, &iph->saddr);
    if (blocked) {
        __sync_fetch_and_add(blocked, 1);
        __u32 stat_key = 1;
        __u64 *dropped = bpf_map_lookup_elem(&stats, &stat_key);
        if (dropped) __sync_fetch_and_add(dropped, 1);
        return XDP_DROP;
    }
    
    __u32 stat_key = 0;
    __u64 *passed = bpf_map_lookup_elem(&stats, &stat_key);
    if (passed) __sync_fetch_and_add(passed, 1);
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
EOF

# Compile and load:
clang -O2 -target bpf -c ddos_mitigation.bpf.c -o ddos_mitigation.bpf.o
ip link set dev eth0 xdp obj ddos_mitigation.bpf.o sec xdp

# Control plane: add attacker IPs to blocklist:
# (using bpf_map_update_elem via bpftool or custom C program)
bpftool map update id $(bpftool map show name blocked_ips -j | jq .[0].id) \
    key hex c0 a8 01 01   # 192.168.1.1 in hex
    value hex 00 00 00 00 00 00 00 00

# Measure effectiveness:
bpftool map dump id $(bpftool map show name stats -j | jq .[0].id)
# Per-CPU stats: [0]=passed [1]=dropped
# Before: CPU 0 at 100%, RX drops
# After: CPU 0 at 15%, no RX drops, attack traffic dropped at wire speed
```

---

### Mental Model / Analogy

```
Normal networking = full customs inspection for every traveler

Network = international airport
Packets = travelers arriving on flights
NIC = arrivals gate
Kernel stack = full customs hall (passport control, X-ray, immigration)

Normal process:
  Traveler lands (NIC receives packet)
  Get a boarding card (allocate sk_buff)
  Walk through entire customs hall (full kernel stack)
  Even if traveler is obviously unauthorized, full process runs

Cost: each traveler takes 5 minutes (1-3 microseconds)
With 10M travelers/sec: 50M person-minutes/sec -> impossible!

XDP = customs officer AT THE GATE (before customs hall):
  Traveler lands
  Gate officer glances at passport (XDP eBPF program, ~50ns)
  
  If obviously unauthorized (attack traffic):
    XDP_DROP: "Go back on the plane" (no sk_buff, no stack)
    Takes 5 seconds (50ns) vs 5 minutes (full customs)
    
  If obviously fine:
    XDP_PASS: "Welcome, proceed to customs" (normal sk_buff path)
  
  If this specific fast-track traveler:
    XDP_REDIRECT -> AF_XDP: direct to VIP lounge (userspace bypass)
    Skip customs entirely, application gets packet directly

XDP offload on SmartNIC = robotic border scanners AT THE RUNWAY:
  Before the gate even, on the tarmac
  Completely automated (NIC hardware)
  CPU has zero involvement

DPDK = a country with NO customs process:
  Build your own mini-country (private userspace network stack)
  Only your approved travelers can enter (you control everything)
  No bureaucracy (no kernel stack at all)
  Much faster but: you must implement ALL the rules yourself
  Used by: airlines (telco NFV), financial exchanges

AF_XDP = the VIP direct transfer:
  UMEM = VIP lounge pre-booked by your application
  NIC delivers passengers directly to lounge (DMA to UMEM)
  No customs forms filled (no sk_buff)
  Application sees raw passenger data (raw packet bytes)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept: kernel bypass for high-performance networking. XDP as eBPF at the
NIC driver. XDP_DROP for DDoS mitigation. DPDK as full kernel bypass.
Use cases: load balancing, DDoS mitigation, telco packet processing.

**Level 2:**
XDP return codes (PASS/DROP/TX/REDIRECT). Native vs generic vs offloaded
XDP. AF_XDP for userspace packet delivery. bpftool/ip link set xdp to
load programs. DPDK basics: UIO/VFIO binding, polling mode driver concept.
Performance characteristics: XDP ~10 Mpps, DPDK ~70 Mpps.

**Level 3:**
XDP program structure (xdp_md context, data/data_end pointers). eBPF
verifier checks for XDP (bounds checking mandatory). BPF maps in XDP (LRU_HASH
for blocklists, PERCPU_ARRAY for stats). `bpf_redirect_map()` for XDP_REDIRECT.
`XSK_UMEM` structure for AF_XDP. DPDK rte_mbuf, rte_eth_rx_burst, huge pages
requirement. TC BPF (tc-bpf): another hook after sk_buff, supports classifiers
and actions.

**Level 4:**
XDP program attachment (sk/tc/xdp hooks comparison). XDP in Cilium (Kubernetes
CNI): load balancing at XDP layer. Katran (Facebook's L4 load balancer): XDP-
based. XDP chaining (multiple XDP programs). DPDK multi-queue architecture:
RSS + DPDK queues. DPDK EAL (Environment Abstraction Layer). DPDK rte_ring
(lock-free SPSC ring). SR-IOV with DPDK: virtual functions for DPDK. Memory
pool (`rte_mempool`) with lockless allocation. OVS-DPDK (Open vSwitch with
DPDK data plane).

**Level 5:**
XDP frame layout: packet data + metadata in xdp_frame. xdp_buff vs xdp_frame
lifecycle. XDP busy poll integration. Virtio-net XDP support. XDP prog maps:
BPF_MAP_TYPE_PROG_ARRAY for tail calls. DPDK Flow API: hardware flow steering.
DPDK Rte Security: IPsec offload to hardware. SmartNIC XDP offload: P4 programs
on Netronome Agilio. RDMA + XDP: receive packets AND RDMA messages in one
framework. VPP (Vector Packet Processing): alternative to DPDK, vector-oriented
packet batching. P4 language for programmable NIC data plane.

---

### Code Example

**BAD - misusing XDP:**
```c
// BAD: XDP program without bounds checking (verifier will reject):
SEC("xdp")
int bad_xdp(struct xdp_md *ctx) {
    struct iphdr *iph = (void *)(long)ctx->data + sizeof(struct ethhdr);
    // Missing bounds check! BPF verifier REJECTS this program:
    // "invalid mem access 'inv' at off=14"
    
    if (iph->protocol == IPPROTO_UDP)
        return XDP_DROP;
    return XDP_PASS;
}
// Error on load: "libbpf: Error loading .../bad_xdp.bpf.o:
//   Bad address (14)"

// GOOD: bounds checking required by verifier:
SEC("xdp")
int good_xdp(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    
    struct ethhdr *eth = data;
    // Every pointer dereference: check bounds first:
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;  // too short, pass upstream
    
    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return XDP_PASS;
    
    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;
    
    if (iph->protocol == IPPROTO_UDP)
        return XDP_DROP;
    return XDP_PASS;
}
// Verifier accepts: all pointer accesses are bounds-checked
```

**GOOD - XDP for high-performance load balancing:**
```c
// XDP ECMP load balancer:
// Direct return XDP_TX after rewriting destination MAC
SEC("xdp")
int lb_forward(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    struct ethhdr *eth = data;
    
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;
    
    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;
    
    // Select backend: simple hash of source IP
    __u32 backend_idx = bpf_get_hash_recalc(ctx) % NUM_BACKENDS;
    
    // Lookup backend MAC from map:
    struct backend *be = bpf_map_lookup_elem(&backends, &backend_idx);
    if (!be)
        return XDP_PASS;
    
    // Rewrite destination MAC:
    __builtin_memcpy(eth->h_dest, be->mac, ETH_ALEN);
    __builtin_memcpy(eth->h_source, LOCAL_MAC, ETH_ALEN);
    
    // Redirect to backend NIC:
    return bpf_redirect(be->ifindex, 0);
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "XDP can replace the entire kernel network stack" | XDP operates at one hook point (NIC driver) and handles decisions for individual packets. It cannot replace the full kernel stack: TCP connection state management, socket API, routing table updates, DHCP, ARP responses, TLS - all require the full kernel stack. XDP is most powerful as a FAST PATH for specific traffic patterns: DDoS mitigation (drop attack traffic before it costs CPU), load balancing (redirect TCP flows to backends), firewalling (block specific IPs/ports). Normal application traffic still goes through the kernel stack. The architecture: XDP makes a fast per-packet decision (DROP/PASS/REDIRECT). Dropped packets never see the kernel stack. Passed packets proceed normally. A well-designed XDP + kernel stack system handles both high-speed filtering AND full TCP application support. |
| "DPDK applications always outperform XDP" | DPDK achieves higher raw packet rates (70+ Mpps vs XDP's 10-30 Mpps) because DPDK uses polling mode (continuous ring polling vs interrupt-driven). However: DPDK's CPU cost is a DEDICATED CORE at 100% - even when receiving 1 packet/second, the polling core is at 100% CPU. XDP uses the normal interrupt-driven kernel path plus BPF overhead only when packets arrive. For bursty traffic patterns: XDP is often more practical. For maximum sustained throughput: DPDK wins. Additionally: DPDK requires userspace implementation of networking protocols (ARP, routing, TCP if needed) - significant development complexity. XDP works with existing kernel networking, adding only the fast-path filter/redirect. |
| "XDP programs run with full kernel privileges" | XDP programs are eBPF programs and are subject to the eBPF verifier's safety checks. They cannot: dereference arbitrary memory pointers (verifier requires bounds checks), make unbounded loops (verifier ensures termination), call arbitrary kernel functions (only BPF helper functions). The verifier rejects any program that might crash the kernel. Additionally: loading XDP programs requires `CAP_BPF` (kernel 5.8+) or `CAP_SYS_ADMIN`. XDP programs run in the kernel's context but are verified to be safe. This is fundamentally different from a kernel module, which can do anything. The safety properties of eBPF are what make XDP trustworthy - the kernel can verify the program is safe before running it at high speed on every packet. |
| "You need special hardware for XDP to be effective" | XDP has three modes: offloaded (requires SmartNIC), native (in NIC driver, most modern NICs support it: i40e, mlx5, bnxt, virtio-net), and generic (fallback, works with any NIC but slower). Native XDP works with most production NICs and achieves 10+ Mpps. SmartNIC offloaded XDP (Netronome NFP, Mellanox ConnectX-5 Rx steering) achieves line-rate processing with zero CPU involvement. For many use cases (DDoS mitigation at 10 Gbps, load balancing at moderate rate): native XDP on a standard Intel or Mellanox NIC is sufficient. The requirement: kernel 4.8+ (XDP support), a NIC driver with XDP support (check with `ip -details link show eth0`). Most modern cloud instances (AWS, GCP, Azure) support native XDP. |

---

### Failure Modes & Diagnosis

**XDP program loading and operation issues:**
```bash
# Symptom: XDP program fails to load
ip link set dev eth0 xdp obj my_program.bpf.o sec xdp
# Error: "cannot attach to XDP"
# OR: bpftool prog load fails with verifier error

# Diagnosis 1: BPF verifier rejection:
# Load with verbose output:
bpftool prog load my_program.bpf.o /sys/fs/bpf/myxdp \
    type xdp 2>&1 | head -30
# Look for: "invalid mem access" -> missing bounds check
# Look for: "program too large" -> simplify XDP program
# Look for: "back-edge from insn X to Y" -> unbounded loop

# Fix: add bounds checks for every pointer dereference

# Diagnosis 2: NIC doesn't support native XDP:
ip -details link show eth0 | grep "xdp_features"
# xdp_features NETDEV_XDP_ACT_XDP_TX NETDEV_XDP_ACT_REDIRECT...
# If no xdp_features: generic XDP only (much slower)

# Diagnosis 3: XDP_DROP not working (packets still arriving):
# Verify program is actually attached:
ip link show eth0 | grep -i xdp
# If no xdp line: program not loaded

# Check program stats:
bpftool prog show name my_xdp
# Shows: jited bytes, loaded timestamp, run count

# Symptom: XDP program attached but performance not improving
# Check if generic XDP is being used (slower path):
bpftool net list dev eth0
# xdp:
#     eth0(2) generic id 42  <- generic! Not native
# vs:
#     eth0(2) driver id 42   <- native (faster)

# Force native XDP (fails if NIC doesn't support):
ip link set dev eth0 xdp obj prog.bpf.o sec xdp native
# If this fails: NIC only supports generic XDP

# Symptom: XDP causing packet drops for legitimate traffic
# Temporarily disable XDP to verify:
ip link set dev eth0 xdp off
# If issue resolves: XDP program logic error (dropping too much)

# Debug with trace pipe:
# In XDP program: add bpf_trace_printk for debugging
# Then: cat /sys/kernel/debug/tracing/trace_pipe
# (very slow, for debugging only)
```

---

### Related Keywords

**Foundational:**
LNX-073 (eBPF), LNX-084 (Network performance)

**Builds on this:**
LNX-101 (eBPF for platform engineering), LNX-105 (Linux networking at fleet scale)

**Related:**
LNX-091 (Traffic control/qdisc), LNX-092 (Network namespaces)

---

### Quick Reference Card

| Concept | Command / Note |
|---------|----------------|
| Load XDP program | `ip link set dev eth0 xdp obj prog.bpf.o sec xdp` |
| Remove XDP program | `ip link set dev eth0 xdp off` |
| View attached programs | `bpftool net list dev eth0` |
| Check XDP mode | `ip -details link show eth0 \| grep xdp_features` |
| XDP_DROP | No sk_buff allocated, ~50ns per packet |
| XDP native mode | In NIC driver, fastest, most NICs support |
| XDP offloaded | Runs on SmartNIC hardware, zero CPU |
| DPDK binding | `dpdk-devbind.py --bind=vfio-pci BDF` |
| AF_XDP | Zero-copy to userspace via UMEM |

**3 things to remember:**
1. XDP runs before `sk_buff` allocation - `XDP_DROP` is ~10x cheaper than dropping in the kernel stack; ideal for DDoS mitigation
2. Three XDP modes: offloaded (on NIC HW) > native (in NIC driver) > generic (after sk_buff, slow fallback)
3. DPDK = complete kernel bypass via polling; highest throughput but dedicated CPU core at 100% - use for maximum sustained PPS

---

### Transferable Wisdom

XDP's architecture (filter/action at ingress, early exit to avoid expensive
path) is the same pattern as: WAF (block at edge before application), CDN
edge caching (serve from cache before reaching origin), Kubernetes admission
webhooks (reject early before persisting to etcd), API gateway authentication
(reject unauthenticated requests before routing to services). The eBPF
verifier's safety model (prove correct before running) is the same as:
type systems in statically-typed languages, Rust's borrow checker, Java
bytecode verification, WebAssembly sandbox. You trade some expressiveness
for guaranteed safety properties. The DPDK polling model (busy-wait vs
interrupt-driven) appears in: io_uring `IORING_SETUP_SQPOLL` (kernel thread
polls submission queue), Kafka consumer tight-poll, real-time systems. XDP's
XDP_REDIRECT is the kernel-level equivalent of hardware port forwarding on
a switch: redirect at the lowest layer for maximum efficiency. Cilium (Kubernetes
CNI): uses XDP for pod-to-pod routing, TC BPF for network policy enforcement,
eBPF for service load balancing. XDP/eBPF is increasingly the primary tool
for cloud-native networking.

---

### The Surprising Truth

Facebook (Meta) built Katran, their entire Layer 4 load balancing infrastructure,
using XDP eBPF. Before Katran: traditional L4 load balancers required dedicated
appliances or kernel module-based solutions. Katran runs as an XDP program
on commodity Linux servers, provides consistent hashing for load distribution,
and handles Facebook's actual production traffic. The key metric: before XDP,
adding a new load balancer required days of hardware provisioning. With XDP
on commodity servers: deploy in minutes. The same pattern at Google: Maglev
(their L4 load balancer) influenced XDP's design; Google contributed TCP
segmentation offload improvements to XDP upstream. Cloudflare was one of
the first public adopters of XDP for DDoS mitigation: their blog (2017)
documented dropping 320 Gbps of attack traffic using XDP on commodity servers,
with CPU usage of 15-25% instead of 100%+ with traditional iptables. The
surprising truth: XDP is not just a niche technology for telco NFV. It's
now embedded in Kubernetes CNI plugins (Cilium), cloud provider load
balancers, and CDN edge infrastructure worldwide. If you're using a
Kubernetes cluster with Cilium networking: XDP is likely processing your
pod network traffic right now.

---

### Mastery Checklist

- [ ] Understands XDP's position in the receive path: before sk_buff allocation, in NIC driver
- [ ] Knows the 5 XDP return codes and their use cases (PASS/DROP/TX/REDIRECT/ABORTED)
- [ ] Can load and unload XDP programs using `ip link set` and `bpftool`
- [ ] Understands the difference between XDP native/offloaded/generic modes
- [ ] Knows when to use XDP vs DPDK (in-kernel filtering vs full userspace packet processing)

---

### Think About This

1. Design an XDP-based DDoS mitigation system for a 100 Gbps DDoS attack.
   The attack uses randomly spoofed source IPs (different source every packet).
   Explain why a simple IP blocklist (LRU_HASH map) won't work for this
   attack pattern, what alternative approach you'd use (rate limiting per
   destination port? connection rate tracking? packet signature matching?),
   and what the XDP program logic would look like. What are the limits of
   what XDP can detect vs what the kernel TCP stack needs to do?

2. You need to choose between XDP and DPDK for a new application that:
   (a) receives 5 million packets/second at peak, (b) must support TCP
   with full connection state, (c) runs on a 32-core server. Analyze the
   trade-offs: XDP can only run BPF programs (limited logic), DPDK requires
   userspace TCP stack implementation. Which would you choose for each of
   these components: packet ingress filtering, TCP connection management,
   and SSL/TLS termination? Write the hybrid architecture.

3. Explain why the eBPF verifier's bounds checking requirement (every
   pointer must be validated before dereference) is actually a feature
   rather than a limitation for XDP programs. Compare this with C kernel
   modules that have no such restriction. What class of bugs does the
   verifier prevent? What types of XDP programs does the verifier make
   impossible to write, and how do XDP developers work around these
   limitations?

---

### Interview Deep-Dive

**Foundational:**
Q: What is XDP and how does it achieve better performance than traditional packet filtering (iptables)?
A: XDP (eXpress Data Path) is an eBPF-based framework that attaches a packet processing program to the NIC driver level - the earliest point in the Linux kernel receive path. COMPARISON WITH IPTABLES: iptables operates AFTER the full kernel receive path: NIC DMA -> sk_buff allocation (600+ bytes) -> Ethernet processing -> IP routing -> netfilter/iptables. By the time iptables sees a packet: ~200-500ns have been spent on allocations and processing. Dropping a packet in iptables frees the sk_buff after this cost. XDP operates BEFORE sk_buff allocation. The XDP program sees raw packet data via a pointer to the NIC ring buffer. For XDP_DROP: the packet is discarded without any heap allocation. Total cost: ~50ns (BPF program execution). PERFORMANCE RATIO: iptables drop: 3-5 Mpps per core. XDP drop: 14+ Mpps per core (native), potentially line-rate with SmartNIC offload. EXAMPLE: DDoS mitigation. iptables `-j DROP` for attack IPs: at 10 Mpps, CPU is at 100% just processing iptables rules. XDP with LRU_HASH blocklist: at 10 Mpps, CPU is at 15-20%. MECHANISMS: XDP modes - native (in NIC driver, most modern NICs), offloaded (on NIC hardware, zero CPU), generic (after sk_buff, fallback). XDP programs: eBPF with verifier-enforced bounds checking, access raw packet bytes. Return codes determine fate: PASS (normal stack), DROP (discard), TX (bounce back), REDIRECT (to other NIC/CPU/AF_XDP socket). LIMITATIONS: XDP runs per-packet, stateless by default. Maps (BPF_MAP_TYPE_LRU_HASH) enable stateful processing. Cannot replace TCP stack for connection-oriented protocols.

**Expert:**
Q: How does AF_XDP achieve zero-copy packet delivery to userspace, and how does it compare to DPDK?
A: AF_XDP (Address Family XDP) is a socket type that enables applications to receive packets in userspace memory without any kernel copies. MECHANISM: (1) Application allocates UMEM (User Memory): a large buffer pool registered with the kernel via `setsockopt(AF_XDP_UMEM_REG)`. (2) UMEM is mapped into both kernel and userspace address space (shared memory, no copy). (3) AF_XDP socket is created and bound to a specific queue of a NIC. (4) An XDP program (loaded on the NIC) uses `bpf_redirect_map()` to direct packets to the AF_XDP socket. (5) When a packet arrives: NIC DMA's it directly into a UMEM buffer (from the FILL ring that the application pre-populated). (6) Kernel writes the buffer offset to the RX ring. (7) Application reads RX ring: gets offset into UMEM pointing to packet data. One DMA (NIC to UMEM), zero kernel copies. RING STRUCTURE: FILL ring (app pre-allocates buffers for incoming packets), RX ring (kernel fills with received packets), TX ring (app enqueues packets to send), COMPLETION ring (NIC notifies of TX completion). COMPARISON WITH DPDK: AF_XDP advantages: works with existing kernel network stack (other traffic on the same NIC goes through normal path), coexists with iptables/tc, uses normal kernel interrupt model. AF_XDP limitations: still involves kernel context switches for ring signaling, ~10-30 Mpps peak. DPDK advantages: 70+ Mpps per core, deterministic latency (no kernel involvement at all), mature ecosystem for telco/HPC. DPDK limitations: dedicates entire NIC to userspace (no kernel networking on that NIC), requires reimplementing protocols (ARP, routing, TCP if needed), dedicated polling core at 100% CPU. USE CASE GUIDE: DDoS mitigation, Kubernetes CNI, in-kernel filtering: XDP. Maximum raw throughput, telco NFV, custom protocol: DPDK. Middle ground (custom app needs raw packets but coexists with kernel networking): AF_XDP.
