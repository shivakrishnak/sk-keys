---
id: NET-016
title: "Network Topology (LAN, WAN, MAN)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-011
used_by: NET-024, NET-025, NET-028
related: NET-009, NET-024, NET-025
tags:
  - networking
  - foundational
  - topology
  - infrastructure
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/net/network-topology/
---

**⚡ TL;DR** - LAN (Local Area Network) = one building
or campus. MAN (Metropolitan) = a city. WAN (Wide Area
Network) = multiple cities or global. Each scope has
different latency characteristics, ownership models, and
technology choices.

| #016 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, MAC Address | |
| **Used by:** | Subnet and CIDR Notation, NAT, Routing Basics | |
| **Related:** | IP Address, Subnet and CIDR, NAT, Routing Basics | |

---

### 🔥 The Problem This Solves

Without topology vocabulary, engineers cannot communicate
about which part of the network is experiencing problems,
which team owns it, or what performance to expect. "The
network is slow" is meaningless. "The LAN switch in AZ-B
has high utilization" or "the WAN link to our DR site is
saturated" is actionable.

---

### 📘 Textbook Definition

**LAN (Local Area Network):** A network covering a small
geographic area (building, campus, floor) under single
ownership. Typically uses Ethernet (IEEE 802.3) or WiFi
(IEEE 802.11). Low latency (< 1ms), high bandwidth
(1-100 Gbps), privately owned and managed.

**MAN (Metropolitan Area Network):** Covers a city or
large campus. Often connects multiple LANs across a metro
area. Typically leased from a carrier (fiber rings, cable).
Latency: 1-10ms. Bandwidth: Gbps range.

**WAN (Wide Area Network):** Covers multiple cities,
countries, or globally. The internet is the ultimate WAN.
Corporate WANs connect offices across geographies. Typically
uses leased carrier lines (MPLS, SD-WAN) or VPN over
internet. Latency: 10-300ms depending on distance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
LAN = building (< 1ms). MAN = city (1-10ms). WAN = globe
(10-300ms). The scope determines latency, ownership, and cost.

**One analogy:**

> Network topologies are like road systems:
> - LAN = the roads inside a private campus or neighborhood.
>   You own them, maintain them, and can drive fast.
> - MAN = city streets. Shared with others. Still fast.
>   City government owns them.
> - WAN = interstate highways and international routes.
>   Carrier-owned. Different traffic rules. Slower per mile
>   due to tolls (cost) and distance (latency).

**One insight:**
The LAN/WAN boundary is also the public/private boundary.
Inside a LAN, you typically use private IP addresses (RFC
1918) and communicate directly without encryption (though
you should encrypt anyway). Across a WAN (especially the
internet), you need NAT or public IPs, and encryption
(VPN/TLS) is essential.

---

### 🔩 First Principles Explanation

**Topology comparison table:**

```
┌──────────────────────────────────────────────────────────┐
│  LAN vs MAN vs WAN                                       │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Property    │  LAN         │  MAN         │  WAN       │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Geographic  │  Building /  │  City /      │  Country / │
│  scope       │  campus      │  campus ring │  global    │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Latency     │  < 1ms       │  1-10ms      │  10-300ms  │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Bandwidth   │  1-400 Gbps  │  1-100 Gbps  │  Mbps-Gbps │
│              │  (Ethernet)  │  (fiber ring)│  (varies)  │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Ownership   │  Private     │  Carrier/    │  Carrier / │
│              │              │  private     │  internet  │
├──────────────┼──────────────┼──────────────┼────────────┤
│  IP range    │  RFC 1918    │  RFC 1918 or │  Public or │
│              │  (private)   │  public      │  VPN       │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Technology  │  Ethernet,   │  SONET/SDH,  │  MPLS,     │
│              │  WiFi,VLAN   │  Metro-E,    │  SD-WAN,   │
│              │              │  fiber ring  │  VPN, BGP  │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Encrypted?  │  Optional    │  Optional    │  Required  │
│              │  (but should)│  (but should)│  (always)  │
└──────────────┴──────────────┴──────────────┴────────────┘
```

**Physical topology shapes:**

```
┌──────────────────────────────────────────────────────────┐
│  Physical Topology Designs                               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  STAR (most common, modern Ethernet)                    │
│     All devices connect to central switch               │
│     ┌──────┐   ┌──────┐   ┌──────┐                    │
│     │ Host │   │ Host │   │ Host │                    │
│     └──┬───┘   └──┬───┘   └──┬───┘                    │
│        └──────────┼──────────┘                          │
│               [Switch]                                  │
│                                                          │
│  RING (old Token Ring, modern fiber metro rings)        │
│     Each node connected to two neighbors                 │
│     Redundant path: traffic can go either direction     │
│                                                          │
│  MESH (datacenters, internet backbone, BGP)             │
│     Multiple paths between nodes                        │
│     Highly resilient: any link failure has alternate     │
│     path. Cost: N*(N-1)/2 links for full mesh           │
│                                                          │
│  BUS (obsolete 10BASE-2 coax Ethernet)                  │
│     All devices on shared medium. Any collision          │
│     disrupts all. Why CSMA/CD was needed.               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
A company has offices in New York and London. They have
three connectivity options for their WAN:

**Option A:** Internet VPN (TLS/IPsec over internet)
- Cost: minimal (just ISP bandwidth)
- Latency: 70-90ms RTT (trans-Atlantic internet)
- Reliability: internet-grade (99.9% typical)

**Option B:** MPLS private line
- Cost: $10,000-50,000/month
- Latency: 70-90ms RTT (same physics, but SLA-guaranteed)
- Reliability: carrier SLA (99.99% typical)
- Benefit: predictable jitter, QoS for voice

**Option C:** Multicloud private connectivity (AWS
Direct Connect + Azure ExpressRoute)
- Cost: medium, per GB data transfer
- Latency: similar to MPLS (carrier-grade)
- Benefit: also connects to cloud resources

**THE INSIGHT:**
Physics determines latency (the Atlantic is the Atlantic).
What you buy is reliability, jitter predictability, and
QoS guarantees. For most workloads, a reliable internet
VPN with TLS is sufficient and dramatically cheaper.
MPLS makes sense for voice/video conferencing where
consistent jitter matters more than average latency.

---

### 🧠 Mental Model / Analogy

> Think of network topology in terms of property rights:
> - **LAN**: you own the cable, the switch, the router.
>   You control everything. If it breaks, you fix it.
> - **MAN**: you lease the city fiber ring from the carrier.
>   You control the equipment at each end but not the middle.
> - **WAN**: you use the internet (no one owns it) or lease
>   MPLS from a carrier. You control nothing in the middle
>   except what you've paid to have prioritized.
>
> The further from your LAN, the less control you have
> over the path.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
LAN is your home or office network. WAN is the internet or
a corporate network spanning multiple cities. MAN is
somewhere in between - city-scale network.

**Level 2 - How to use it (junior developer):**
When an app is "slow," identify which topology segment is
the issue. `ping` your default gateway (LAN test). `ping`
a known internet IP (WAN test). Latency in LAN should be
< 1ms. LAN latency > 5ms indicates congestion or faulty
hardware. WAN latency varies by geography.

**Level 3 - How it works (mid-level engineer):**
In cloud environments (AWS, GCP), "VPC" is a virtual LAN.
Each VPC is a private address space. "Internet Gateway" is
the LAN-to-WAN boundary. "VPC Peering" or "Transit Gateway"
connects multiple VPCs (like connecting two LANs over a
private WAN). "Direct Connect" is like a leased line MAN/WAN
bypassing the internet.

**Level 4 - Why it was designed this way (senior/staff):**
The LAN/WAN architectural boundary emerged from economics:
high-bandwidth links within a building are cheap (fiber
runs). High-bandwidth links between cities are expensive
(carrier fiber, rights-of-way). This cost difference drives
architecture: compute near data (avoid WAN), cache at the
edge (reduce WAN round trips), CDN for static content
(serve from LAN rather than WAN relative to user).

**Level 5 - Mastery (distinguished engineer):**
SD-WAN (Software-Defined WAN) disrupted traditional MPLS
by using commodity internet links with intelligent traffic
management (quality measurement, dynamic path selection,
application-aware routing). The result: MPLS pricing
collapsed as enterprises proved internet-based SD-WAN
could deliver enterprise-grade WAN at 60-80% cost
reduction. The trade-off: SD-WAN requires more sophisticated
management tooling and has different failure modes than
MPLS (more paths but each path less reliable).

---

### ⚙️ How It Works (Mechanism)

```bash
# Test LAN latency (gateway)
ping -c 10 192.168.1.1
# Should be < 1ms avg, < 0.1ms mdev

# Test WAN latency (internet)
ping -c 10 8.8.8.8
# Depends on distance: 5-200ms typical

# Traceroute to see LAN→WAN transition
traceroute 8.8.8.8
# First hop: LAN default gateway
# Second hop: ISP first hop (entering WAN)
# Subsequent hops: internet backbone

# Check local network interface details
ip addr show      # IP addresses per interface
ip link show      # MAC, MTU, state
ip route show     # Routing table (LAN vs WAN routes)

# On Linux, show all connected segments
arp -n | awk '{print $1}' | head -10
# Lists hosts in local ARP table = LAN neighbors
```

**Cloud VPC as virtual LAN:**

```
┌──────────────────────────────────────────────────────────┐
│  AWS VPC Architecture (Virtual LAN)                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  VPC: 10.0.0.0/16 (your virtual LAN)                   │
│  ├── Private Subnet: 10.0.1.0/24                        │
│  │   └── EC2, RDS (no direct internet access)           │
│  ├── Public Subnet: 10.0.0.0/24                         │
│  │   └── EC2 with public IP, load balancer              │
│  └── Internet Gateway (LAN → WAN boundary)              │
│      └── Traffic to 0.0.0.0/0 goes to IGW (WAN)        │
│                                                          │
│  Direct Connect = dedicated fiber bypassing internet     │
│    (leased line, like MPLS MAN to datacenter)           │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**WHAT CHANGES AT SCALE:**
At internet scale (content delivery network), "LAN" becomes
relative: a CDN PoP (Point of Presence) in a user's city
is functionally a "LAN" for that user (< 5ms). The origin
server is the "WAN" (100ms+). The entire CDN design is about
converting WAN latency to LAN latency by caching content
close to users. Anycast routing (used by Cloudflare,
Google's `8.8.8.8`) routes users to the nearest PoP
automatically by advertising the same IP from multiple
geographic locations.

---

### ⚖️ Comparison Table

| Technology | Topology | Use Case |
|---|---|---|
| Ethernet (802.3) | LAN | Wired local network |
| WiFi (802.11ax) | LAN | Wireless local network |
| VLAN (802.1Q) | LAN (logical) | Network segmentation within one switch |
| MPLS | WAN | Carrier-grade private WAN, QoS for voice |
| SD-WAN | WAN | Internet-based WAN with intelligence |
| VPN (IPsec/WireGuard) | WAN (logical) | Encrypted tunnel across WAN |
| AWS VPC | LAN (virtual) | Cloud private network |
| AWS Direct Connect | MAN/WAN | Dedicated private circuit to AWS |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Cloud is in the cloud" (no topology) | Cloud has topology: each availability zone is a datacenter (LAN), AZs within a region connect over metro fiber (MAN-like), regions connect over global backbone (WAN). Latency follows these physical topologies. |
| VPN = WAN | VPN is a technology (logical tunnel) that can be used within LAN or across WAN. Corporate VPN creates a logical LAN across a WAN backbone. The topology still exists; the VPN just encrypts the WAN portion. |
| WiFi is less reliable than Ethernet for LAN | WiFi introduces variable latency and lower throughput due to radio interference and half-duplex nature. In a properly designed office WiFi network with good AP placement and modern 802.11ax, the difference is small for most applications. For latency-sensitive applications (voice trading desks, HFT), Ethernet is still required. |

---

### 🚨 Failure Modes & Diagnosis

**WAN Link Saturation (Bottleneck Between Sites)**

**Symptom:** Connections between offices are slow. Video
calls drop. File transfers across the WAN take hours.
LAN-local operations are normal speed.

**Root Cause:** WAN bandwidth is saturated. A backup job,
large file transfer, or misconfigured replication is
consuming all WAN capacity.

**Diagnostic Command / Tool:**
```bash
# From a WAN-connected server, check link utilization
# (if you have monitoring access to the router)
snmpget -v2c -c public router_ip \
  ifInOctets.ifIndex ifOutOctets.ifIndex

# Without router access: measure from servers
# Site A to Site B throughput test (requires iperf3 server)
iperf3 -c site-b-server -t 30 -P 4
# -P 4 = 4 parallel streams

# Check if it's just one host saturating
# (requires NetFlow/sFlow on router)
# Or check top traffic senders from application logs

# Quick bandwidth test to a fixed external point
curl -o /dev/null \
  https://speed.cloudflare.com/__down?bytes=10000000
```

**Fix:** Identify the process consuming WAN bandwidth.
Reschedule backups to off-hours. Implement QoS to
prioritize interactive traffic (voice, SSH) over bulk
transfers. Consider SD-WAN with application-aware routing.

**Prevention:** Monitor WAN utilization with SNMP/NetFlow.
Set alerts at 70% utilization (before 100% saturation).
Separate backup network from production WAN.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `IP Address` - private (LAN) vs public (WAN) addressing
- `MAC Address` - L2 addressing used within LAN segments

**Builds On This (learn these next):**
- `Subnet and CIDR Notation` - how to partition a LAN into
  smaller segments
- `NAT (Network Address Translation)` - how private LAN
  addresses reach the WAN (internet)
- `Routing Basics` - how routers connect LANs to WANs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LAN          │ Building/campus. < 1ms. 1-100Gbps.        │
│              │ Private RFC1918. Ethernet/WiFi.           │
├──────────────┼───────────────────────────────────────────┤
│ MAN          │ City scale. 1-10ms. Gbps. Carrier-leased. │
├──────────────┼───────────────────────────────────────────┤
│ WAN          │ Multi-city/global. 10-300ms. Mbps-Gbps.   │
│              │ Internet or MPLS/SD-WAN.                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Physics limits WAN latency. You can buy   │
│              │ reliability (SLA) not speed-of-light.     │
├──────────────┼───────────────────────────────────────────┤
│ CLOUD MAP    │ VPC = virtual LAN. IGW = WAN boundary.    │
│              │ Direct Connect = MAN/WAN private circuit. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "LAN: you own it, fast. WAN: carrier-     │
│              │  owned, latency is physics."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Subnet and CIDR → NAT → Routing Basics    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. LAN < 1ms, WAN 10-300ms. Physics sets the minimum.
   Data center within same region: low latency. Cross-
   country: 40-60ms. Trans-ocean: 70-140ms.
2. Cloud VPC = virtual LAN. Internet Gateway = LAN/WAN
   boundary. Same architecture as physical network,
   virtualized.
3. WAN link saturation shows as slow cross-office traffic
   while local LAN operations are normal. Monitor WAN
   utilization proactively.

**Interview one-liner:**
"LAN covers a building or campus with sub-millisecond latency
and Gbps bandwidth, using Ethernet and WiFi. MAN is city-
scale, WAN is global (the internet or corporate MPLS).
Latency is fundamentally bounded by physics: trans-Atlantic
minimum is ~56ms RTT. Cloud VPCs are virtual LANs with an
Internet Gateway as the WAN boundary. SD-WAN is disrupting
traditional MPLS by using commodity internet links with
intelligent traffic management."

---

### 💡 The Surprising Truth

Your AWS "region" is not actually a single location - it's
multiple physically separate datacenters (Availability
Zones) connected by private AWS fiber. The distance between
AZs in a region is typically 60-100km - enough to survive
a natural disaster affecting one AZ without affecting
others. The latency between AZs is 1-2ms (very fast MAN-
equivalent). But this means synchronous database replication
across AZs adds 1-2ms to every write. Systems that run
primary DB in us-east-1a and replica in us-east-1b pay
this "AZ tax" on every transaction. This is why some
high-performance databases keep primary and replica in
the same AZ, accepting disaster recovery risk for the
performance gain.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the three network topology scales with
   concrete latency and bandwidth numbers for each.
2. **DEBUG** whether a performance issue is LAN or WAN
   by using `ping` to the local gateway vs a WAN target.
3. **DECIDE** whether to use MPLS vs internet VPN for a
   new office WAN connection, articulating the trade-offs.
4. **BUILD** the mental model mapping AWS VPC constructs
   (VPC, subnet, IGW, NAT GW, Direct Connect) to LAN/WAN
   topology concepts.
5. **EXTEND** to explain how CDN converts WAN latency to
   LAN latency for content delivery.

---

### 🧠 Think About This Before We Continue

**Q1.** Your company runs a database cluster in AWS us-east-1.
Primary in AZ-a, read replica in AZ-b. An application in
AZ-b reads from the replica but writes go to the primary
in AZ-a. Draw the network path for a write operation
and calculate the additional latency compared to a
same-AZ setup. Is the additional latency significant for
a 95th-percentile latency SLA of 10ms?

*Hint: AZ-to-AZ latency within a region is ~1-2ms. How
does this compare to typical DB write latency?*

**Q2.** A company is choosing between internet-based SD-WAN
and dedicated MPLS for connecting 50 global offices. They
run real-time video conferencing and VoIP. The MPLS quote
is $500K/year; the SD-WAN solution is $80K/year. What
technical factors would favor MPLS despite the 6x cost?
What mitigation techniques in SD-WAN address these concerns?

*Hint: Voice quality cares about jitter (latency variation),
not just average latency. MPLS provides QoS guarantees.
SD-WAN provides QoS via traffic shaping on commodity links.*

**Q3.** [Hands-On] Run `traceroute 8.8.8.8` (Linux) or
`tracert 8.8.8.8` (Windows). Identify: Which hop is your
default gateway (LAN)? At which hop do you enter your ISP's
network (WAN)? What is the latency jump between LAN hops
and WAN hops? Can you identify any geographic hops by
reverse-DNS lookup on the hop IPs?