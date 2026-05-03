---
layout: default
title: "Overlay Networks"
parent: "Networking"
nav_order: 200
permalink: /networking/overlay-networks/
number: "0200"
category: Networking
difficulty: ★★★
depends_on: IP Addressing, Network Topologies, Kubernetes
used_by: Kubernetes, Docker Compose, Distributed Systems, Cloud — AWS
related: VLAN, Network Policies, Service Discovery, NAT, Subnet & CIDR
tags:
  - networking
  - overlay
  - vxlan
  - geneve
  - kubernetes-cni
  - flannel
  - calico
  - encapsulation
---

# 200 — Overlay Networks

⚡ TL;DR — An overlay network is a virtual network built on top of (over) an existing physical network (underlay). Enables pods/containers across different hosts to communicate as if on the same L2 network, even when hosts are on different subnets. Implemented via encapsulation (VXLAN, Geneve): original packet wrapped in a new packet with underlay IPs, tunnelled across the physical network, decapsulated at destination. Kubernetes CNI plugins (Flannel, Calico VXLAN mode, Cilium) use overlay networks.

---

### 🔥 The Problem This Solves

Container networking challenge: two containers on different physical hosts need to communicate. Host A has pod with IP 10.244.1.5; Host B has pod with IP 10.244.2.10. The physical network routes between hosts by HOST IP (10.0.0.1, 10.0.0.2) — it doesn't know about pod IPs (10.244.x.x). The overlay network creates a virtual L2 layer where pod IPs are directly routable, by encapsulating pod-to-pod traffic inside host-to-host traffic.

---

### 📘 Textbook Definition

**Overlay Network:** A logical network built on top of another network (the underlay/physical network). Traffic in the overlay appears to be point-to-point between virtual nodes, but is actually encapsulated and tunnelled through the physical network. Key encapsulation protocols: **VXLAN** (Virtual Extensible LAN) — wraps L2 frames in UDP packets; **Geneve** (Generic Network Virtualisation Encapsulation) — more flexible, used by newer CNI plugins and OVN. **GRE** (Generic Routing Encapsulation) — older, point-to-point tunnels.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Overlay = virtual network over physical network. Pod on Host A talks to pod on Host B by wrapping the pod-to-pod packet inside a Host-A-to-Host-B packet (encapsulation). The physical network sees only host traffic; the pods see a flat virtual network.

**One analogy:**

> Overlay networks are like sending international parcels. The parcel (pod packet) has a destination address in a virtual address space (192.168.1.5). You put it in a shipping box (VXLAN encapsulation) with real-world addresses (host IPs). The shipping company (physical network) only sees the outer box. At the destination country (target host), customs removes the outer box (decapsulation), revealing the inner parcel with its local address.

---

### 🔩 First Principles Explanation

**UNDERLAY VS OVERLAY:**

```
Underlay (physical network):
  Real switches, routers, cables
  Routes based on physical/cloud host IPs: 10.0.0.1, 10.0.0.2, 10.0.0.3
  Knows nothing about containers/pods

Overlay (virtual network):
  Virtual network built on top
  Pods have IPs in pod CIDR: 10.244.0.0/16 (Kubernetes default)
  Pod IPs not routable on physical network
  Overlay makes them appear directly routable

Problem without overlay:
  Pod A (10.244.1.5) on Host 1 (10.0.0.1)
  Pod B (10.244.2.10) on Host 2 (10.0.0.2)
  Physical switch: "where is 10.244.2.10?" → no route → drops packet
```

**VXLAN ENCAPSULATION:**

```
Original Pod-to-Pod packet:
┌──────────────────────────────────────────────────────────┐
│ Ethernet Header: src=podA-mac, dst=podB-mac              │
│ IP Header: src=10.244.1.5, dst=10.244.2.10               │
│ TCP Header: src=54321, dst=8080                          │
│ Payload: HTTP GET /api/users                             │
└──────────────────────────────────────────────────────────┘

After VXLAN encapsulation (added by VTEP on Host 1):
┌──────────────────────────────────────────────────────────┐
│ Outer Ethernet: src=host1-mac, dst=host2-mac (gateway)   │
│ Outer IP: src=10.0.0.1 (Host1), dst=10.0.0.2 (Host2)    │
│ Outer UDP: dst=4789 (VXLAN standard port)                │
│ VXLAN Header: VNI=100 (Virtual Network Identifier)       │
│ Inner Ethernet: src=podA-mac, dst=podB-mac               │
│ Inner IP: src=10.244.1.5, dst=10.244.2.10                │
│ TCP + Payload (original packet preserved intact)         │
└──────────────────────────────────────────────────────────┘

Physical network routes: outer packet (10.0.0.1 → 10.0.0.2)
Host 2 VTEP decapsulates: extracts inner packet, delivers to Pod B

VTEP = VXLAN Tunnel Endpoint (kernel or software on each host)
VNI = Virtual Network Identifier (24-bit, 16M possible overlays)
```

**KUBERNETES CNI IMPLEMENTATIONS:**

```
Flannel (simplest VXLAN overlay):
  - VXLAN mode: encapsulates all pod traffic in VXLAN
  - Easy to set up, limited features (no NetworkPolicy)
  - Good for simple clusters; not for production security

Calico:
  - Native routing mode: BGP to advertise pod CIDRs to physical router
    → No encapsulation overhead! Pods directly routable if BGP supported
  - VXLAN mode: when BGP not available (most cloud environments)
  - Supports NetworkPolicy enforcement (via iptables or eBPF)

Cilium:
  - eBPF-based (no iptables)
  - Geneve or VXLAN encapsulation, or native routing
  - L7-aware (HTTP, Kafka, DNS policies)
  - Hubble: real-time network flow observability

AWS VPC CNI (aws-node):
  - NO overlay! Uses AWS VPC routing directly
  - Each pod gets a VPC ENI (Elastic Network Interface) IP
  - Pod IPs are directly routable within the VPC
  - AWS manages routing table updates via EC2 API
  - Trade-off: limited pod density (IPs per ENI per instance type)
```

**NATIVE ROUTING VS OVERLAY:**

```
Overlay (VXLAN):
  + Works on any network (even if router doesn't know pod CIDRs)
  + Easy to set up (no BGP required)
  - Encapsulation overhead: ~50 bytes per packet
  - CPU overhead: encapsulation/decapsulation on every packet
  - Slightly higher latency (20-50μs extra per hop)
  - MTU: physical MTU - 50 = pod effective MTU (1450 vs 1500)
    → Fragmentation if not configured correctly

Native Routing (BGP or VPC-native):
  + No encapsulation overhead (full MTU, lower CPU, lower latency)
  + Packets go directly pod-to-pod
  - Requires network to know pod routes (BGP or cloud API)
  - More complex to set up in bare-metal environments
  - AWS VPC CNI: tied to ENI limits (IP exhaustion at scale)

Rule of thumb:
  Cloud: prefer VPC-native CNI (AWS VPC CNI, GKE native routing)
  On-premise: VXLAN overlay OR Calico BGP with BGP-capable switches
```

---

### 🧪 Thought Experiment

**MTU MISMATCH — THE INVISIBLE KILLER:**
A team sets up a Kubernetes cluster with VXLAN overlay. Pods run fine for small requests. But large file uploads (>1450 bytes) fail silently or with cryptic errors. The issue: physical network MTU = 1500 bytes. VXLAN header = 50 bytes overhead. Pod effective MTU = 1450 bytes. Large packets from pods are fragmented (or dropped if DF-bit set) because they exceed 1450 bytes BEFORE the VXLAN overhead is added, making the total 1500+ bytes. Fix: set MTU in CNI config to 1450 (or configure physical network for jumbo frames: MTU=9000, so overlay can use 8950).

---

### 🧠 Mental Model / Analogy

> VXLAN overlay is like Russian dolls (matryoshka). The innermost doll is the actual pod packet (with pod IPs). It gets placed inside a larger doll (UDP/IP packet with host IPs). The postal system (physical network) only sees and routes the outer doll based on the outer address labels. When the outer doll arrives at the destination host, it's opened to reveal the inner doll — the original pod packet — which is then delivered to the correct container. The pod never knows it was wrapped.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Overlay networks let containers on different physical hosts talk to each other as if they were on the same network. The CNI plugin wraps container packets in host packets (VXLAN), sends them across the physical network, then unwraps them at the destination. Kubernetes uses this for pod-to-pod communication.

**Level 2:** VXLAN encapsulates L2 frames in UDP, adding ~50 bytes overhead. The 24-bit VNI allows 16M separate virtual networks. Kubernetes uses one VNI per cluster (or per namespace in some implementations). MTU must be reduced by 50 bytes for VXLAN (1450 instead of 1500). Cloud CNIs (AWS VPC CNI) avoid overlay entirely by using native VPC routing — better performance but limited pod density per node.

**Level 3:** VTEP (VXLAN Tunnel Endpoint) — the component on each host that performs encapsulation/decapsulation. In Flannel: flanneld daemon + kernel VXLAN module. In Cilium: eBPF programs in the kernel. When a packet from Pod A to Pod B hits the host network stack: (a) iptables/eBPF intercepts; (b) looks up VTEP for destination pod's host (via ARP/NDP or control plane); (c) encapsulates and sends to destination VTEP; (d) destination VTEP decapsulates and delivers to pod. For ARP across VTENs: either broadcast (inefficient) or proxy-ARP where control plane answers on behalf of remote pods.

**Level 4:** Geneve (Generic Network Virtualisation Encapsulation) — the successor to VXLAN, used by OVN (Open Virtual Network), Cilium 1.11+. Like VXLAN but with extensible TLV-encoded options (can carry metadata in header). OpenStack, OVN-Kubernetes, and Cilium with Geneve use this for richer tunnel metadata. eBPF-XDP (eXpress Data Path): XDP processes packets at the NIC driver level, before the kernel network stack — even lower overhead for VXLAN encapsulation/decapsulation. Cilium can use XDP for packet processing at ~10Mpps (million packets per second) versus ~1-2Mpps with standard kernel networking.

---

### ⚙️ How It Works (Mechanism)

```bash
# View overlay network interfaces on a Kubernetes node
ip link show type vxlan
# Output: flannel.1 or cilium_vxlan etc.
ip -d link show flannel.1
# shows: vxlan id 1 dstport 8472 nolearning proxy l2miss l3miss

# Check VTEP entries (which host has which pods)
bridge fdb show dev flannel.1
# 66:5b:02:xx:xx:xx dst 10.0.0.3 self permanent
# → MAC address maps to host IP (10.0.0.3) — tunnel destination

# Check route for overlay (how pod CIDRs are routed)
ip route show
# 10.244.1.0/24 via 10.244.1.0 dev flannel.1 onlink
# → Pod CIDR 10.244.1.0/24 is on flannel.1 (VXLAN interface)

# Capture VXLAN traffic on physical interface
tcpdump -i eth0 -n port 8472  # Flannel VXLAN port
# or port 4789 for standard VXLAN
# See: outer IP (host-to-host) + inner IP (pod-to-pod) in dump

# View Calico BGP peers (native routing mode)
calicoctl node status
# Peer IP: 10.0.0.2, Type: node-to-node, State: up/Established
# BGP advertisng pod CIDRs to other nodes (no encapsulation)

# AWS VPC CNI: check ENI assignments
kubectl describe node worker-1 | grep -A 20 "vpc.amazonaws.com/eniconfig"
# Shows pod IP assignments from VPC subnet
aws ec2 describe-network-interfaces \
  --filters "Name=attachment.instance-id,Values=i-xxx" \
  --query 'NetworkInterfaces[*].[NetworkInterfaceId,PrivateIpAddresses[*].PrivateIpAddress]'
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Pod A (10.244.1.5) on Node 1 (10.0.0.1)
→ sends HTTP request to
Pod B (10.244.2.10) on Node 2 (10.0.0.2)

1. Pod A sends packet: src=10.244.1.5, dst=10.244.2.10
2. Pod A's default route: → eth0 (pod's veth) → Host 1 bridge (cni0)
3. Host 1 routing: 10.244.2.0/24 via flannel.1 (VXLAN interface)
4. VTEP lookup: 10.244.2.10 → hosted on Node 2 (10.0.0.2)
5. VXLAN encapsulation:
   Outer: src=10.0.0.1, dst=10.0.0.2, UDP:8472
   Inner: src=10.244.1.5, dst=10.244.2.10 (original packet)
6. Physical network routes: 10.0.0.1 → 10.0.0.2 (normal routing)
7. Node 2 receives UDP:8472 packet
8. VTEP (flannel.1) decapsulates: extracts inner packet
9. Host 2 routing: 10.244.2.10 → local pod (via cni0 bridge)
10. Pod B receives: src=10.244.1.5, dst=10.244.2.10

From Pod A and Pod B's perspective: direct L3 connection
Physical network sees: Node1 → Node2 UDP traffic
```

---

### 💻 Code Example

```python
# Simulate VXLAN encapsulation concept (educational)
# Real VXLAN is implemented in Linux kernel, not Python

import struct
import socket

VXLAN_PORT = 4789
VXLAN_FLAGS = 0x08000000  # I bit set (valid VNI)

def create_vxlan_header(vni: int) -> bytes:
    """Create an 8-byte VXLAN header."""
    # VXLAN header: flags (4 bytes) + VNI (3 bytes) + reserved (1 byte)
    flags = VXLAN_FLAGS
    vni_bytes = vni.to_bytes(3, 'big')
    reserved = b'\x00'
    return struct.pack('>I', flags) + vni_bytes + reserved

def encapsulate_packet(inner_packet: bytes, src_host: str,
                        dst_host: str, vni: int = 100) -> dict:
    """
    Simulate VXLAN encapsulation.

    In reality: Linux kernel VXLAN module does this at wire speed.
    """
    vxlan_header = create_vxlan_header(vni)

    return {
        "outer_ip": {
            "src": src_host,   # physical host IP
            "dst": dst_host,   # physical host IP
            "proto": "UDP",
            "dst_port": VXLAN_PORT,
        },
        "vxlan_header": {
            "vni": vni,         # identifies the overlay network
            "flags": hex(VXLAN_FLAGS),
        },
        "inner_packet": inner_packet.hex(),  # original pod packet
        "total_overhead_bytes": 8 + 8 + 20,  # VXLAN + UDP + IP headers
    }

# Example
original_packet = b"\x45\x00\x00\x3c..."  # IP header + payload (example)
encapsulated = encapsulate_packet(
    original_packet,
    src_host="10.0.0.1",   # Node 1
    dst_host="10.0.0.2",   # Node 2
    vni=100
)
print(f"VXLAN overhead: {encapsulated['total_overhead_bytes']} bytes")
print(f"Effective pod MTU: {1500 - encapsulated['total_overhead_bytes']} bytes")
# VXLAN overhead: 36 bytes
# Effective pod MTU: 1464 bytes (plus inner Ethernet: 1450 bytes usable)
```

---

### ⚖️ Comparison Table

| Approach                        | Overhead      | Setup Complexity    | Pod Density             | Best For                  |
| ------------------------------- | ------------- | ------------------- | ----------------------- | ------------------------- |
| VXLAN overlay (Flannel, Calico) | ~50 bytes/pkt | Low                 | Unlimited (IP space)    | On-prem, simple K8s       |
| BGP native routing (Calico)     | None          | Medium (BGP config) | Unlimited               | On-prem with BGP switches |
| AWS VPC CNI                     | None          | Low (AWS managed)   | Limited (ENI IP limits) | EKS production            |
| GKE native VPC                  | None          | Low (GCP managed)   | High (alias IP ranges)  | GKE production            |
| Cilium (eBPF + Geneve)          | ~50 bytes/pkt | Medium              | Unlimited               | Advanced features needed  |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                                 |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Overlay networks are slow                   | VXLAN with kernel hardware offload (NIC offload for checksum and segmentation) adds minimal overhead (< 5% throughput, 10-50μs latency). Modern NICs support VXLAN offload — the CPU cost is near zero. Only measurable impact in extremely high-frequency, latency-sensitive workloads |
| All Kubernetes networking uses overlays     | AWS EKS with VPC CNI, GKE with native networking, AKS with Azure CNI — no overlay. Native VPC routing is common in cloud. Overlays are more common in on-premise or hybrid deployments                                                                                                  |
| VXLAN supports only 4096 networks like VLAN | VXLAN uses 24-bit VNI (16.7M virtual networks) vs VLAN's 12-bit (4096). This was a primary reason VXLAN was created — to address VLAN scalability limits in large datacenters                                                                                                           |

---

### 🚨 Failure Modes & Diagnosis

**Overlay Network MTU Mismatch — Large Packets Silently Dropped**

```bash
# Symptom: small HTTP requests work fine; large file uploads/downloads fail
# Root cause: pod MTU (1450) + VXLAN (50) = 1500; jumbo frames needed OR
# pod is sending 1500-byte packets which become 1550 after VXLAN = fragmented

# Step 1: check pod MTU
kubectl exec -n production deploy/my-app -- ip link show eth0
# Should show: mtu 1450 (for VXLAN) or 1500 (for native routing)

# Step 2: test with different packet sizes
kubectl exec -n production deploy/my-app -- \
  ping -M do -s 1400 10.244.2.10  # DF bit set, 1400-byte payload
kubectl exec -n production deploy/my-app -- \
  ping -M do -s 1450 10.244.2.10  # should fail if MTU=1450

# Step 3: check CNI MTU config
kubectl get configmap kube-flannel-cfg -n kube-flannel -o yaml | grep -i mtu
# Or: kubectl get configmap cilium-config -n kube-system | grep mtu

# Step 4: check physical NIC MTU
ip link show eth0  # on the host node
# If shows 1500 and overlay is VXLAN: pod MTU should be 1450

# Fix for Flannel: edit configmap, set "mtu": 1450
# Fix for Cilium: helm upgrade --set global.MTU=1450

# Jumbo frames solution (preferred for performance):
# Set physical NIC MTU to 9000 (jumbo frames)
# Then overlay pods can use 8950 MTU (minimal fragmentation)
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `Network Topologies`, `Kubernetes`

**Related:** `VLAN`, `Network Policies`, `NAT`, `Subnet & CIDR`, `Service Discovery`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ OVERLAY      │ Virtual network over physical network     │
│ VXLAN        │ L2 frames in UDP; VNI identifies network  │
├──────────────┼───────────────────────────────────────────┤
│ OVERHEAD     │ ~50 bytes/packet; set pod MTU to 1450     │
│ VTEP         │ Endpoint that encapsulates/decapsulates   │
├──────────────┼───────────────────────────────────────────┤
│ K8S CNIs     │ Flannel (VXLAN), Calico (VXLAN/BGP)       │
│              │ Cilium (eBPF+Geneve), AWS VPC CNI (native)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wrap pod packets in host packets so the  │
│              │ physical network routes them correctly"   │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing the CNI strategy for a large-scale Kubernetes cluster running 10,000 pods on 200 nodes in AWS EKS. (a) Compare AWS VPC CNI vs Calico VXLAN overlay: AWS VPC CNI gives native VPC routing (no overhead) but limits pods per node by ENI IP count (e.g., c5.xlarge = 4 ENIs × 15 IPs = 60 pod IPs max per node) — calculate the maximum pod density and whether it's sufficient for your workload. (b) When VPC CNI IP exhaustion occurs (subnet runs out of IPs), what AWS-specific solutions exist (VPC CNI custom networking, /100 IPv6 CIDR, ENI prefix delegation)? (c) Explain the VXLAN vs Geneve tradeoff in terms of extensibility: how does Geneve's TLV options enable carrying security group metadata in the packet, which is used by AWS Nitro for security group enforcement at hypervisor level? (d) For ML training workloads requiring high-bandwidth pod-to-pod communication (NCCL gradient sync), explain why RDMA (Remote Direct Memory Access) over InfiniBand or RoCE (RDMA over Converged Ethernet) bypasses the kernel overlay entirely: how EFA (Elastic Fabric Adapter) provides this in AWS, and why it's categorically different from VXLAN-based pod networking.
