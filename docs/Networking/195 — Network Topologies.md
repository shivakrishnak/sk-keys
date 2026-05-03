---
layout: default
title: "Network Topologies"
parent: "Networking"
nav_order: 195
permalink: /networking/network-topologies/
number: "0195"
category: Networking
difficulty: ★☆☆
depends_on: IP Addressing, Networking
used_by: System Design, Cloud — AWS, Distributed Systems, Kubernetes
related: BGP, Load Balancer L4_L7, CDN, Overlay Networks, VLAN
tags:
  - networking
  - topology
  - mesh
  - star
  - fat-tree
  - spine-leaf
---

# 195 — Network Topologies

⚡ TL;DR — Network topology describes how nodes are connected. Classical: star (hub-and-spoke), mesh (every node to every other), ring, bus. Modern datacenter: **spine-leaf** (every leaf connects to every spine — predictable latency, horizontal scalability). Cloud: **hub-and-spoke VPC** (shared services VPC + peered application VPCs) or **full mesh VPC peering**. Understanding topology affects fault tolerance, bandwidth, and latency design decisions.

---

### 🔥 The Problem This Solves

A poorly chosen network topology creates bottlenecks (hub becomes a single point of failure and bandwidth bottleneck), unpredictable latency (traffic takes varying hop counts), or wasted cost (full mesh is expensive at scale). Modern datacenter design (spine-leaf) and cloud architecture (Transit Gateway hub-and-spoke vs full mesh peering) are direct applications of topology principles to real engineering decisions.

---

### 📘 Textbook Definition

**Network Topology:** The arrangement of nodes (computers, routers, switches) and links (cables, wireless, tunnels) in a network. Physical topology: actual cable layout. Logical topology: how data flows (may differ from physical).

**Classical topologies:** Star (hub-and-spoke), Ring, Bus, Mesh, Tree/Hierarchical.

**Modern datacenter topologies:** Spine-Leaf (Clos network), Fat-Tree, Three-tier (access-aggregation-core). **Cloud topologies:** Hub-and-spoke VPC, Full-mesh VPC peering, Transit Gateway hub-and-spoke.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Topology = how nodes are connected. Star = central hub (single point of failure). Mesh = every node connected to many others (resilient, expensive). Spine-leaf = modern datacenter topology: predictable 2-hop latency between any two servers.

**One analogy:**
> Network topologies are like road systems. Star = one central roundabout, all roads lead to it (bottleneck if roundabout is closed). Mesh = every neighbourhood has roads to every other neighbourhood (resilient but expensive to build). Spine-leaf = a city grid: every block (leaf) connects to the same main avenues (spines) — any two blocks are always exactly 2 main avenues apart.

---

### 🔩 First Principles Explanation

**CLASSICAL TOPOLOGIES:**
```
Star (Hub-and-Spoke):
  All nodes connect to central switch/router
  Advantages: easy to manage, add nodes
  Disadvantages: central device = single point of failure
  Example: home WiFi router, corporate LAN

Ring:
  Each node connects to two neighbours, forming a ring
  Data travels around ring until reaching destination
  Disadvantage: one break disrupts entire network
  Example: SONET/SDH (telecom backbone, dual ring for resilience)

Mesh:
  Every node connects to every other (full mesh)
  Or partial mesh (some connections)
  Advantage: maximum resilience (many paths)
  Disadvantage: N(N-1)/2 connections for N nodes (expensive)
  Full mesh with 10 nodes = 45 links
  Example: internet backbone (BGP makes logical mesh from partial mesh)

Bus:
  All nodes share one cable
  Historical: early Ethernet (10BASE2)
  Advantage: simple; Disadvantage: collision domain, any break fails all
  Modern: irrelevant (replaced by switched Ethernet)
```

**SPINE-LEAF (MODERN DATACENTER):**
```
Spine Layer: high-capacity switches, fully interconnected
Leaf Layer:  access switches, each connected to ALL spine switches

                    [Spine 1] [Spine 2] [Spine 3] [Spine 4]
                      │  ╲ ╱ │   │ ╲ ╱ │   │ ╲ ╱ │
                   [Leaf1] [Leaf2] [Leaf3] [Leaf4] [Leaf5]
                   /    \   / \   /  \   / \   / \
               [Srv] [Srv] [Srv] [Srv] [Srv] [Srv] [Srv]

Properties:
  Any server to any server: exactly 2 hops (Leaf → Spine → Leaf)
  Predictable latency: all paths have same hop count
  Scale-out: add spine for more bandwidth, add leaf for more servers
  No spanning tree: ECMP (Equal Cost Multi-Path) for load distribution

vs Three-tier (access-aggregation-core):
  Old model: server → access switch → aggregation → core
  Problems: spanning tree convergence, oversubscription, limited east-west
  Spine-leaf: purpose-built for east-west (server-to-server) traffic
  (Microservices and Kubernetes are primarily east-west)
```

**CLOUD VPC TOPOLOGY:**
```
Hub-and-Spoke (Transit Gateway):
  Shared services VPC (hub): DNS, Active Directory, NAT, monitoring
  Application VPCs (spokes): prod-vpc, staging-vpc, dev-vpc
  All connected via Transit Gateway
  Advantages: shared services in one place, simple routing
  Disadvantages: hub can be bandwidth bottleneck; TGW costs

Full Mesh VPC Peering:
  Every VPC peers with every other VPC
  Advantages: direct paths, no central bottleneck
  Disadvantages: N(N-1)/2 peering connections (impractical at >10 VPCs)
  No transitive peering (A↔B, B↔C does NOT allow A↔C)

AWS VPC Connectivity:
  2-5 VPCs: full mesh peering (simple, no TGW cost)
  5+ VPCs: Transit Gateway (hub-and-spoke, managed routing)
  Multi-account: AWS RAM (Resource Access Manager) to share TGW
```

---

### 🧪 Thought Experiment

**CHOOSING BETWEEN TOPOLOGIES:**
A company runs 20 AWS VPCs (production, staging, dev, per-team VPCs). Should they use full-mesh peering or Transit Gateway?

Full mesh: 20×19/2 = 190 peering connections to manage. Each pair needs manually maintained route tables. Adding a VPC = 19 new peerings. Management overhead is prohibitive.

Transit Gateway: 20 VPC attachments to one TGW. Adding a VPC = 1 TGW attachment. Central route table. Cost: $0.05/GB transferred + $0.07/attachment-hour. At scale, the management simplicity far outweighs the cost.

---

### 🧠 Mental Model / Analogy

> Think of datacenter spine-leaf like an airport hub system, but optimised. Traditional hierarchy (core-aggregation-access) is like flying always through one major hub (slow, single point of failure). Spine-leaf is like a grid of regional airports where every small airport has direct connections to all 4 major hubs — you always fly directly to a hub then directly to your destination. Exactly 2 hops, always. Compare that to star topology where everyone connects through the same terminal — if it's busy or down, everything stops.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Network topology = how devices are connected. Star = central switch (most home/office networks). Mesh = everything connects to everything (internet-style). Modern datacenters use spine-leaf for fast, predictable server-to-server communication.

**Level 2:** Cloud topology: use VPC peering for 2-5 VPCs; use Transit Gateway for 5+ VPCs. Understand transitive peering doesn't work (you need direct connections or TGW). Subnet-level topology: public subnets (load balancer, NAT gateway) → private subnets (app servers) → isolated subnets (databases) = defence in depth.

**Level 3:** Spine-leaf with ECMP: every server can reach any other server via multiple equal-cost paths (all spine paths have equal bandwidth and latency). ECMP (Equal Cost Multi-Path) hashes flows across paths using 5-tuple. Fat-oversubscription: leaf switch might have 48 × 10G downlinks and 4 × 100G uplinks = 48:4 = 1.2:1 oversubscription ratio (much better than traditional 20:1). For HPC/ML training: non-blocking fat-tree topology — mathematically proven to never oversubscribe any path, requires exactly 3× the number of switches.

**Level 4:** Clos networks (Bell Labs, 1953) are the mathematical basis for spine-leaf. Charles Clos proved that you can build non-blocking multi-stage networks from smaller switches. k-ary fat-tree: k pods, each pod has k/2 edge switches and k/2 aggregation switches, k core switches = (5k³)/4 ports total for (k/2)² × k hosts. A modern 128-radix fat-tree can connect 524,288 servers with non-blocking bandwidth. This is the architecture underlying AWS, Google Cloud, and Facebook datacenters — tens of thousands of commodity switches in a highly structured topology replacing one expensive custom "big iron" switch.

---

### ⚙️ How It Works (Mechanism)

```bash
# Check network topology (Linux host)
# See which switches you're connected through
traceroute -n 10.0.1.50   # internal datacenter host

# View routing table (shows topology)
ip route show

# AWS: view Transit Gateway route tables
aws ec2 describe-transit-gateway-route-tables
aws ec2 search-transit-gateway-routes \
  --transit-gateway-route-table-id tgw-rtb-xxx \
  --filters "Name=type,Values=static,propagated"

# View VPC peering connections
aws ec2 describe-vpc-peering-connections \
  --query 'VpcPeeringConnections[*].[VpcPeeringConnectionId,Status.Code,RequesterVpcInfo.VpcId,AccepterVpcInfo.VpcId]'

# Kubernetes: view pod network topology
kubectl get nodes -o wide  # see which nodes host which pods
kubectl get pods -o wide   # pod IP and node assignment

# Check ECMP paths (Linux with ECMP routing)
ip route show table main | grep -i ecmp
# If multiple routes with same metric: ECMP active
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Modern Datacenter Packet Flow (Spine-Leaf):

Server A (Rack 1) → Server B (Rack 2):

Server A → Leaf Switch 1 (ToR - Top of Rack)
  Leaf 1: destination IP not local, consult FIB
  ECMP: hash(src_ip, dst_ip, src_port, dst_port, proto) % 4_spines
  → Pick Spine 3 (hash result)
  
Leaf 1 → Spine 3
  Spine 3: destination is behind Leaf 5 (per FIB)
  → Forward to Leaf 5

Spine 3 → Leaf 5 (ToR of Rack containing Server B)
  Leaf 5: Server B is directly connected
  → Forward to Server B

Total: 3 hops (leaf→spine→leaf), deterministic
Latency: ~3 × 1-2μs hop delay = 3-6μs one-way
```

---

### 💻 Code Example

```python
from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class SpineLeafTopology:
    """Model a spine-leaf datacenter topology."""
    n_spines: int
    n_leaves: int
    servers_per_leaf: int
    
    def __post_init__(self):
        self.spines = [f"spine-{i}" for i in range(1, self.n_spines + 1)]
        self.leaves = [f"leaf-{i}" for i in range(1, self.n_leaves + 1)]
        self.servers: Dict[str, List[str]] = {
            leaf: [f"server-{leaf}-{j}" 
                   for j in range(1, self.servers_per_leaf + 1)]
            for leaf in self.leaves
        }
    
    def path(self, src_server: str, dst_server: str) -> List[str]:
        """Calculate path between two servers (always 3 hops)."""
        src_leaf = next(
            leaf for leaf, srvs in self.servers.items() 
            if src_server in srvs
        )
        dst_leaf = next(
            leaf for leaf, srvs in self.servers.items() 
            if dst_server in srvs
        )
        
        if src_leaf == dst_leaf:
            return [src_server, src_leaf, dst_server]  # 2 hops (same rack)
        
        # ECMP: choose spine based on hash
        spine_idx = hash(f"{src_server}:{dst_server}") % self.n_spines
        spine = self.spines[spine_idx]
        
        return [src_server, src_leaf, spine, dst_leaf, dst_server]
    
    def stats(self) -> dict:
        n_servers = self.n_leaves * self.servers_per_leaf
        return {
            "spines": self.n_spines,
            "leaves": self.n_leaves,
            "servers": n_servers,
            "spine_to_leaf_links": self.n_spines * self.n_leaves,
            "max_hops": 5,  # server→leaf→spine→leaf→server
            "same_rack_hops": 3,  # server→leaf→server
        }

# Example: 4-spine, 8-leaf, 40 servers per leaf
topo = SpineLeafTopology(n_spines=4, n_leaves=8, servers_per_leaf=40)
print(f"Topology: {topo.stats()}")

path = topo.path("server-leaf-1-1", "server-leaf-5-20")
print(f"Path: {' → '.join(path)} ({len(path)-1} hops)")
```

---

### ⚖️ Comparison Table

| Topology | Fault Tolerance | Scalability | Latency Predictability | Use Case |
|---|---|---|---|---|
| Star | Low (hub = SPOF) | Limited by hub | High | Home/small office |
| Full Mesh | Very high | Poor (N² links) | High | Internet backbone logic |
| Spine-Leaf | High (multi-path) | Excellent | Very high (2 hops) | Modern datacenters |
| Hub-Spoke VPC | Medium (hub can bottleneck) | Good | High | Cloud multi-VPC |
| Three-tier (traditional DC) | Medium | Limited | Lower (spanning tree) | Legacy datacenters |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More links = more complexity | Spine-leaf appears complex but simplifies operations: no spanning tree, deterministic hop count, simple ECMP. Traditional three-tier with spanning tree is operationally more complex |
| Full-mesh VPC peering is scalable | VPC peering is not transitive — A↔B, B↔C doesn't allow A↔C. Managing N(N-1)/2 connections and route tables becomes impossible past 10 VPCs. Use Transit Gateway |
| Star topology always means single point of failure | With redundant hub switches (active-active or HSRP/VRRP), star topologies can be made highly available. The design pattern matters more than the topology name |

---

### 🚨 Failure Modes & Diagnosis

**Spine Switch Failure in Spine-Leaf: Partial Bandwidth Degradation**

```bash
# Symptom: ~25% increase in inter-rack latency and packet loss
# (1 of 4 spines failed → 25% less bandwidth available)

# Diagnose: check ECMP paths
ip route show | grep ecmp
# If 4 paths previously, now 3 → one spine unreachable

# AWS: Transit Gateway attachment failure
aws ec2 describe-transit-gateway-attachments \
  --filters "Name=state,Values=failed,deleted"

# Check connectivity between racks (in datacenter)
# traceroute from server in leaf-1 to server in leaf-5
traceroute -n 10.0.5.10
# Number of intermediate hops should be stable (2 for same fabric)
# If seeing 3+ hops: possible rerouting through a different path

# Recovery: failing spine drains automatically (ECMP removes from hash)
# Verify traffic redistributed:
# netstat -s | grep retransmit  (elevated = packets lost during transition)
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `Networking`

**Related:** `BGP` (internet topology), `Load Balancer L4/L7` (distributes across topology), `Overlay Networks` (logical topology over physical), `VLAN` (segments within a topology), `CDN` (distributed network topology)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STAR         │ Hub-and-spoke; SPOF at centre; home/office│
│ MESH         │ All-to-all; resilient; N²/2 links         │
│ SPINE-LEAF   │ 2-hop datacenter; ECMP; scale-out         │
├──────────────┼───────────────────────────────────────────┤
│ CLOUD        │ < 5 VPCs: peer; ≥ 5 VPCs: Transit Gateway │
│              │ No transitive peering in VPC peering!     │
├──────────────┼───────────────────────────────────────────┤
│ SPINE-LEAF   │ Every leaf → every spine; ECMP across all │
│              │ Exactly 2 hops (any server → any server)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "How nodes connect determines bandwidth,  │
│              │ latency, and failure blast radius"        │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the network topology for a hyperscale ML training cluster running 10,000 GPU servers that must all communicate simultaneously during AllReduce operations (gradient synchronisation). (a) Explain why a standard spine-leaf topology creates bottlenecks during AllReduce (all GPUs need to communicate with all others — standard ECMP doesn't provide enough bisection bandwidth). (b) Describe a non-blocking fat-tree topology: how does it guarantee that any server can communicate with any other server at full line rate simultaneously. (c) Explain InfiniBand RDMA as an alternative: why is it preferred for ML training clusters (3-5μs latency vs 50μs for Ethernet, RDMA Zero-copy, direct memory access between GPU servers). (d) Compare NCCL (NVIDIA Collective Communications Library) ring AllReduce topology (servers arranged in a ring, each passes gradients to next) vs all-reduce tree topology — which is more bandwidth-efficient and why? (e) Describe how Google's TPU pods use a 3D torus network topology (each TPU connected to 6 neighbours in a cube) for minimising latency in tensor operations.
