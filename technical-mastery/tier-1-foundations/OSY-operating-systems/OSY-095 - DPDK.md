---
id: OSY-095
title: DPDK - Data Plane Development Kit
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-014, OSY-015, OSY-068
used_by: []
related: OSY-094, OSY-096, OSY-097
tags:
  - DPDK
  - kernel-bypass
  - networking
  - userspace
  - low-latency
  - high-throughput
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 95
permalink: /technical-mastery/osy/dpdk/
---

## TL;DR

DPDK (Data Plane Development Kit) bypasses the Linux kernel
network stack entirely. Packets go directly from NIC to
userspace via DMA. Eliminates: interrupt overhead, context
switches, protocol stack processing per packet. Achieves
tens of millions of packets/second per core. Used in 5G,
cloud networking (AWS VPC, SR-IOV), HFT, and load balancers.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-095 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | DPDK, kernel bypass, userspace networking, packet processing |
| **Prerequisites** | OSY-014, OSY-015, OSY-068 |

---

### Why Kernel Network Stack Is Slow

```
Normal packet path (kernel network stack):
  
  1. Packet arrives at NIC
  2. NIC DMA to kernel ring buffer (kernel memory)
  3. NIC raises hardware interrupt -> CPU interrupted
  4. Interrupt handler: runs interrupt service routine
     - Saves registers, disables local interrupts
     - Processes interrupt; schedules NAPI softirq
  5. NAPI softirq: reads packets from ring buffer
     - Passes up the protocol stack
  6. TCP stack processes: checksum, state machine, flow control
  7. Socket buffer: packet enqueued in socket receive buffer
  8. Syscall: application calls recv() -> kernel -> user copy
  9. Application processes packet data
  
  Cost per packet:
    - 2 memory copies: NIC -> kernel, kernel -> user
    - 1 interrupt + context switch overhead
    - Full TCP/IP stack processing (~10000 instructions per packet)
    - Cache pollution: packet data goes through kernel stack
    
  Throughput limits:
    At 10Gbps: 14.88M packets/second (64-byte packets)
    Kernel stack: typically caps at 1-3M packets/second per core
    For 10M pps: need 3-10 cores just for networking
    
DPDK approach:
  
  1. Kernel driver replaced: DPDK PMD (Poll Mode Driver)
  2. NIC DMA: directly to DPDK mempool (userspace hugepage memory)
  3. NO interrupt: polling mode (busy loop on RX ring)
  4. NO kernel: packet passed directly to DPDK application
  5. Custom protocol stack (optional): or raw ethernet processing
  
  Cost per packet:
    - 1 memory copy: NIC -> DPDK mempool
    - 0 interrupts, 0 context switches
    - Processing: only what your code does
    
  Throughput: 40-100M packets/second per core (small packets)
```

---

### DPDK Architecture

```
Traditional Linux path:
  
  NIC -> kernel ring buffer -> TCP/IP stack -> socket -> app
  [hardware]  [kernel memory]  [kernel code]  [syscall] [user]
  
DPDK path:
  
  NIC -> DPDK hugepage mempool -> DPDK PMD -> app code
  [hardware] [user hugepage mem] [user code] [user code]
  
  No kernel involved at all in packet processing.
  
Key DPDK components:
  
  1. EAL (Environment Abstraction Layer):
     DPDK runtime; CPU and memory affinity management
     Allocates hugepages; initializes PMD devices
     
  2. PMD (Poll Mode Driver):
     NIC driver running in userspace (DPDK replaces kernel driver)
     Polls NIC RX ring (busy loop, not interrupt-driven)
     CPU dedicates 100% to polling -> predictable latency
     
  3. mempool:
     Pre-allocated pool of fixed-size packet buffers (mbufs)
     Backed by hugepages (2MB pages for DMA efficiency)
     No malloc per packet: just acquire/release from pool
     
  4. rte_ring:
     Lock-free ring buffer for inter-core packet passing
     SPSC (Single Producer Single Consumer): truly lock-free
     MPMC: uses CAS; still faster than mutex
     
  5. rte_flow (hardware offload):
     NIC classifies packets by rules (5-tuple: src/dst IP/port/proto)
     Routes to specific RX queues per flow
     Different CPU cores process different flows
     Hardware does the work (not software)
```

---

### DPDK Code Sketch

```c
// Simplified DPDK receive loop
// Shows the core polling pattern

#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_mempool.h>

#define RX_BURST_SIZE 32   // Process up to 32 packets at once
#define PORT_ID 0
#define QUEUE_ID 0

// Main packet processing loop (runs on dedicated core)
static int packet_processing_loop(void *arg) {
    struct rte_mbuf *pkts[RX_BURST_SIZE];
    
    while (running) {
        // Poll NIC ring (no interrupt; pure busy-loop)
        uint16_t nb_rx = rte_eth_rx_burst(
            PORT_ID,       // NIC port
            QUEUE_ID,      // RX queue
            pkts,          // array to fill with packets
            RX_BURST_SIZE  // max packets to dequeue
        );
        
        if (nb_rx == 0) {
            continue;  // No packets: keep polling
        }
        
        // Process each received packet
        for (int i = 0; i < nb_rx; i++) {
            struct rte_mbuf *pkt = pkts[i];
            
            // Access packet data directly (zero-copy from NIC)
            uint8_t *data = rte_pktmbuf_mtod(pkt, uint8_t *);
            uint16_t len  = rte_pktmbuf_pkt_len(pkt);
            
            // Your packet processing here:
            // parse_ethernet(data, len);
            // forward_packet(pkt);
            
            // Return buffer to pool (no free())
            rte_pktmbuf_free(pkt);
        }
    }
    return 0;
}
```

---

### Use Cases and Trade-offs

| Use Case | Why DPDK? | Alternatives |
|----------|-----------|--------------|
| 5G UPF (User Plane Function) | 10M pps per core needed | VPP (DPDK-based) |
| Cloud networking (AWS) | VPC virtual switch needs line rate | SR-IOV, XDP |
| HFT (High-Frequency Trading) | Microsecond packet latency | Solarflare OpenOnload (similar) |
| Load balancer | L4 packet forwarding at line rate | XDP (simpler, kernel-level) |
| Firewall/IDS | Deep packet inspection at 40Gbps | Snort + PF_RING |

---

### DPDK vs XDP Comparison

| Feature | DPDK | XDP (eBPF) |
|---------|------|------------|
| Architecture | Kernel bypass | Early kernel hook |
| Programming | C library | eBPF (C subset) |
| CPU model | Polling (dedicated core) | Interrupt + hook |
| Performance | Highest (40-100M pps/core) | High (10-40M pps/core) |
| Complexity | High | Medium |
| Integration | Standalone | Works with kernel stack |
| Use case | Dedicated packet processing | Filtering, routing in Linux |
| Deployment | Replaces kernel driver | Loads into running kernel |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "DPDK is just for network vendors" | DPDK is production technology in cloud computing. AWS uses DPDK (or similar kernel bypass) for VPC networking inside their hypervisors. OpenStack/OVS-DPDK: virtual switch in cloud environments. NGINX Plus uses DPDK for high-performance load balancing. |
| "DPDK wastes CPU (polling loop)" | Yes: DPDK dedicates CPU cores to polling. But for applications that need 10M+ pps, those cores would be saturated processing packets anyway. The trade-off: predictable microsecond latency vs interrupt-based overhead. For < 1M pps: XDP or standard kernel is more efficient. |
| "XDP replaced DPDK" | XDP is a complement, not a replacement. XDP hooks into the kernel before the network stack; still uses interrupts; cannot match DPDK raw throughput on dedicated hardware. XDP's advantage: works WITH Linux networking; DPDK replaces it entirely. |

---

### Quick Reference Card

| Concept | DPDK Detail |
|---------|-------------|
| Packet path | NIC -> hugepage mempool -> DPDK app (no kernel) |
| CPU model | Polling (busy loop; dedicated core per queue) |
| Memory | Hugepages (pre-allocated; no malloc per packet) |
| Interrupt | None (polling replaces interrupt-driven I/O) |
| Performance | 40-100M packets/second per core |
| Alternative | XDP (kernel-integrated; lower throughput) |
| Use cases | 5G, VPC networking, HFT, software load balancers |
| Deployment | Replaces kernel NIC driver (rte_vfio or rte_igb_uio) |
