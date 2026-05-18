---
id: NET-028
title: "Routing Basics (Static vs Dynamic)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-009, NET-024
used_by: NET-045, NET-052
related: NET-009, NET-024, NET-025
tags:
  - networking
  - routing
  - static-routing
  - dynamic-routing
  - bgp
  - ospf
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/net/routing-basics-static-vs-dynamic/
---

**⚡ TL;DR** - Routing is how packets find their path
from source to destination across multiple networks.
Each router makes a local forwarding decision: "for this
destination IP, which interface/next-hop?" The routing
table is a sorted list of network prefixes with next-hop
addresses. Static routing uses manually configured entries
(predictable, simple); dynamic routing protocols (OSPF,
BGP) automatically discover and update paths (essential
at scale). The default route `0.0.0.0/0` catches all
unmatched traffic.

| #028 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, Subnet and CIDR Notation | |
| **Used by:** | VPN Fundamentals, Network Segmentation and Firewall Rules | |
| **Related:** | IP Address, Subnet and CIDR Notation, NAT | |

---

### 🔥 The Problem This Solves

The internet is not a single network - it's millions of
networks interconnected by routers. Each router knows
its local topology but not the full internet map (that
would be millions of routes). Routing solves the problem
of forwarding packets toward their destination hop-by-hop
without any single router needing global knowledge. The
internet works because each router knows the best next
hop for every destination prefix, and the chain of hops
eventually reaches the destination.

---

### 📘 Textbook Definition

**Routing** is the process of selecting paths for packet
forwarding between networks. Each **router** maintains
a **routing table** - a list of destination network
prefixes (CIDR) with associated next-hop IP addresses
and output interfaces. When a packet arrives, the router
performs **longest prefix match (LPM)**: find the most
specific matching route (highest prefix length wins) and
forward accordingly. **Static routes** are manually
configured. **Dynamic routing protocols** (OSPF, EIGRP,
BGP) automatically learn and share routes between routers.
**BGP (Border Gateway Protocol)** is the routing protocol
that holds the internet together.

---

### ⏱️ Understand It in 30 Seconds

**Routing table - what a router does:**

```
Router's routing table:
  Destination          Next-Hop         Interface
  10.0.0.0/8       →  192.168.1.1       eth0 (internal)
  192.168.2.0/24   →  10.0.0.2          eth1 (branch)
  192.168.2.50/32  →  10.0.0.3          eth1 (host)
  0.0.0.0/0        →  203.0.113.1       eth2 (internet)

Packet arrives for 192.168.2.50:
  Check /32 match: YES → 10.0.0.3 wins (most specific)

Packet arrives for 192.168.2.100:
  No /32 match
  Check /24 match: YES → 10.0.0.2 wins

Packet arrives for 8.8.8.8:
  No specific match
  Default route /0 → 203.0.113.1 (internet gateway)
```

**Longest Prefix Match:**
More specific = higher prefix number = wins.
`/32 > /28 > /24 > /16 > /8 > /0`

---

### 🔩 First Principles Explanation

**Static vs Dynamic routing comparison:**

```
┌──────────────────────────────────────────────────────────┐
│  Static vs Dynamic Routing                               │
├────────────────┬────────────────┬────────────────────────┤
│  Feature       │  Static        │  Dynamic               │
├────────────────┼────────────────┼────────────────────────┤
│  Configuration │  Manual per    │  Protocol auto-discovers│
│                │  router        │  and distributes routes │
├────────────────┼────────────────┼────────────────────────┤
│  Failure       │  No automatic  │  Reroutes around failed │
│  handling      │  failover      │  links automatically    │
├────────────────┼────────────────┼────────────────────────┤
│  Scale         │  10-100 routes │  Millions of routes     │
│                │  maximum       │  (BGP: internet)        │
├────────────────┼────────────────┼────────────────────────┤
│  Security      │  Predictable   │  Route injection risk   │
│                │  no protocol   │  (BGP hijacking)        │
├────────────────┼────────────────┼────────────────────────┤
│  CPU overhead  │  None          │  Protocol computation   │
├────────────────┼────────────────┼────────────────────────┤
│  Use case      │  Small network,│  ISP, large enterprise, │
│                │  stub network  │  internet exchange      │
│                │  edge routes   │                         │
└────────────────┴────────────────┴────────────────────────┘
```

**The three main dynamic routing protocols:**

```
┌──────────────────────────────────────────────────────────┐
│  Dynamic Routing Protocols Overview                      │
├──────────────┬───────────────────────────────────────────┤
│  OSPF        │  Interior Gateway Protocol (within one    │
│              │  autonomous system). Link-state: each     │
│              │  router knows full topology, runs         │
│              │  Dijkstra's SPF algorithm. Fast           │
│              │  convergence (<5s). Scales to 100+       │
│              │  routers. Used in: enterprise, ISP core  │
├──────────────┼───────────────────────────────────────────┤
│  BGP         │  Exterior Gateway Protocol (between       │
│  (Border     │  autonomous systems). Policy-based:      │
│  Gateway     │  "path vector" protocol, routes internet  │
│  Protocol)   │  traffic between ISPs/CDNs. Holds 900K+  │
│              │  routes on internet backbone. Used in:   │
│              │  internet exchanges, multi-homed orgs,   │
│              │  AWS/GCP/Azure peering, Direct Connect   │
├──────────────┼───────────────────────────────────────────┤
│  RIP         │  Legacy distance vector protocol.         │
│              │  Max 15 hops. Slow convergence (30s       │
│              │  updates). Avoid in modern networks.     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP: Two routes, longest prefix match**

Your server is at `10.0.1.50/24` with this routing table:

```
Destination      Next-Hop       Type
10.0.0.0/8    → 10.0.0.1       static (corporate HQ)
10.0.1.0/24   → local          connected (your subnet)
10.0.2.0/24   → 10.0.0.5       static (branch office)
172.16.0.0/12 → 10.0.0.1       static (corporate 172)
0.0.0.0/0     → 10.0.1.1       static (internet gateway)
```

**Q: Where does a packet to `10.0.1.100` go?**
- Match `10.0.0.0/8`? YES (10.0.x.x matches)
- Match `10.0.1.0/24`? YES (10.0.1.x matches)
- `10.0.1.0/24` is more specific (/24 > /8) → LOCAL
- Packet stays on local segment, ARP resolves MAC directly.

**Q: Where does a packet to `10.0.5.0` go?**
- Match `10.0.0.0/8`? YES
- Match `10.0.1.0/24`? NO
- Match `10.0.2.0/24`? NO
- Best match: `10.0.0.0/8` → next-hop 10.0.0.1

**THE INSIGHT:**
Routing is pure longest-prefix-match lookups. A router
doesn't know or care about the full path. It just finds
the most specific matching route and forwards. The next
router does the same. The packet follows a chain of local
decisions until it reaches the destination subnet.

---

### 🧠 Mental Model / Analogy

> Routing is GPS navigation with a chain of signposts:
>
> No single signpost shows the full route from A to Z.
> Each signpost shows: "For destinations in direction X,
> take THIS next road."
>
> Your packet reads each signpost (routing table lookup),
> takes the indicated road (next-hop), arrives at the next
> router/signpost, reads THAT signpost, continues.
>
> The most specific signpost wins:
> "New York, Exit 12" beats "East Coast, Exit 1-50"
>
> Dynamic routing updates the signposts automatically
> when roads close (link failures). Static routing
> requires a human to update every signpost manually.

---

### ⚙️ How It Works (Mechanism)

**Linux routing commands:**

```bash
# Show routing table
ip route show
# default via 192.168.1.1 dev eth0 proto dhcp src 192.168.1.50
# 192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.50
# 10.8.0.0/24 via 10.8.0.1 dev tun0  (VPN route)

# Which route handles this destination?
ip route get 8.8.8.8
# 8.8.8.8 via 192.168.1.1 dev eth0 src 192.168.1.50

ip route get 192.168.1.10
# 192.168.1.10 dev eth0 src 192.168.1.50  (no via = local)

# Add a static route
sudo ip route add 10.0.2.0/24 via 192.168.1.100

# Add default route
sudo ip route add default via 192.168.1.1

# Delete a route
sudo ip route del 10.0.2.0/24

# Policy routing (different table for specific source IPs)
sudo ip rule add from 192.168.2.0/24 table 200
sudo ip route add default via 10.0.0.1 table 200
```

**Wrong vs Right - missing specific route causes incorrect forwarding:**

```bash
# BAD: only default route configured on VPN server
# All traffic (including LAN) exits via internet GW
ip route show
# default via 203.0.113.1 dev eth0
# (No route for 10.0.0.0/8 corporate network)

# When VPN client connects:
# 10.0.1.50 → no specific match → default → internet
# Packet goes to internet, not corporate network!

# GOOD: specific routes for internal networks via VPN
sudo ip route add 10.0.0.0/8 via 10.8.0.1 dev tun0
sudo ip route add 192.168.100.0/24 via 10.8.0.1 dev tun0
# default via 203.0.113.1 dev eth0 (internet stays)

# Now:
# 10.0.1.50 → matches 10.0.0.0/8 → via VPN (correct)
# 8.8.8.8  → no match → default → internet (correct)
# "Split tunneling": only corporate traffic through VPN
```

---

### 🔄 The Complete Picture - End-to-End Flow

**How the internet routes a packet:**

```
┌──────────────────────────────────────────────────────────┐
│  Internet Routing (simplified)                           │
├──────────────────────────────────────────────────────────┤
│  Your computer → Your ISP's router                      │
│  Your ISP's router → Internet Exchange Point (IXP)     │
│  IXP → Google's BGP router (AS15169)                   │
│  Google's router → 8.8.8.8 server                      │
│                                                          │
│  Each hop: longest prefix match in routing table        │
│  Each ISP maintains BGP sessions with peers             │
│  BGP routes: 900,000+ prefixes for the internet         │
│                                                          │
│  BGP hijacking risk:                                    │
│  Any ASN can (accidentally or maliciously) announce     │
│  a route for someone else's IP prefix. For example:    │
│  - In 2010, China Telecom accidentally announced ~50K  │
│    prefixes it didn't own → traffic routed through     │
│    China for 18 minutes                                 │
│  - Protection: RPKI (Resource Public Key Infrastructure)│
│    cryptographically validates prefix ownership         │
└──────────────────────────────────────────────────────────┘
```

**AWS VPC routing:**

```bash
# AWS VPC Route Table (viewed in Console or CLI):
aws ec2 describe-route-tables --query \
  'RouteTables[*].Routes[*].[DestinationCidrBlock,GatewayId]' \
  --output table

# Typical VPC route table:
# 10.0.0.0/16  → local (all VPC-local traffic)
# 0.0.0.0/0   → igw-xxxxx (internet via Internet Gateway)
# OR for private subnet:
# 0.0.0.0/0   → nat-xxxxx (internet via NAT Gateway)
# AND for VPN connected:
# 10.100.0.0/16 → vgw-xxxxx (on-prem via VPN GW)
```

---

### ⚖️ Comparison Table

| | Static | OSPF | BGP |
|---|---|---|---|
| **Scale** | Small | Medium (enterprise) | Internet (900K routes) |
| **Config** | Manual | Protocol auto-learns | Policy-based manual |
| **Failover** | None | Automatic (<5s) | Automatic (minutes) |
| **Use case** | Default GW, stub | Enterprise core | ISP, cloud peering |
| **Security** | Safe (no protocol) | Area authentication | BGP prefix validation |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Default route = internet | Default route `0.0.0.0/0` is just the catch-all. In a VPN scenario, default route points to the VPN gateway (all traffic through VPN). In a private network, it might point to a security appliance. |
| Routing protocols are always running | End hosts (servers, laptops) don't run routing protocols (except for policy routing scenarios). Routing protocols run on routers and L3 switches. End hosts just have a default gateway. |
| More routes = slower forwarding | Hardware routers use TCAM (Ternary Content Addressable Memory) for LPM lookup in constant time O(1) regardless of table size. Software routing is slower but still O(log N) with trie algorithms. |

---

### 🚨 Failure Modes & Diagnosis

**Routing Loop - Packets Circulating Forever**

**Symptom:** Traceroute shows the same 2-3 hops repeating.
TTL expires, ICMP TTL-exceeded returned. Packets never reach
destination. Bandwidth consumed by looping packets.

**Root Cause:** Two (or more) routers each think the best
route to destination X is via the other router. Router A
forwards to B, B forwards to A, repeat until TTL=0.

**Diagnosis:**
```bash
# Routing loop appears as repeating IPs in traceroute
traceroute -n 10.0.5.0
# 1  192.168.1.1   1ms
# 2  10.0.0.1      2ms
# 3  192.168.1.1   3ms   ← same as hop 1!
# 4  10.0.0.1      4ms   ← loop
# ...
# *  *  *          (TTL expired)

# Check routing table for conflicting routes
ip route show
# Look for two routes that might cause a loop

# Verify specific route decision
ip route get 10.0.5.0
```

**Fix:**
- Static routing: find misconfigured routes on both routers
- Dynamic routing: check OSPF/BGP configuration for route
  redistribution loops (redistributing OSPF into BGP and
  back is a common loop source)
- Horizon split in RIP: prevents advertising routes back
  to the router they were learned from

---

### 🔗 Related Keywords

**Prerequisites:**
- `IP Address` - routing operates on IP addresses
- `Subnet and CIDR Notation` - routing table entries are CIDR prefixes

**Builds On This:**
- `VPN Fundamentals` - VPN adds routes to routing table
- `Network Segmentation and Firewall Rules` - routes + ACLs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HOW IT WORKS │ Longest prefix match: most specific route │
│              │ wins. /32 > /28 > /24 > /16 > /8 > /0    │
├──────────────┼───────────────────────────────────────────┤
│ STATIC       │ Manual: predictable, no overhead, no      │
│              │ failover. Good for small/stub networks.   │
├──────────────┼───────────────────────────────────────────┤
│ DYNAMIC      │ Auto-learned: OSPF (enterprise interior), │
│              │ BGP (internet exterior, cloud peering)    │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT ROUTE│ 0.0.0.0/0 = catch-all. Points to internet │
│              │ GW, VPN GW, or security appliance         │
├──────────────┼───────────────────────────────────────────┤
│ COMMANDS     │ ip route show, ip route get X.X.X.X,     │
│              │ ip route add/del                          │
├──────────────┼───────────────────────────────────────────┤
│ TRACEROUTE   │ Repeating IPs = routing loop              │
│              │ * * * = ICMP filtered (NOT necessarily    │
│              │ packet loss)                              │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"Routing uses longest prefix match in a routing table:
the most specific matching CIDR prefix wins. Static routing
means manually configured entries - predictable but no
automatic failover. Dynamic protocols (OSPF within an AS,
BGP between ASes) auto-discover and update paths. BGP
holds the internet together with 900K+ routes across
autonomous systems. Default route `0.0.0.0/0` is the
catch-all for unmatched destinations. The critical
operational principle: add specific routes BEFORE broad
ones to avoid sending traffic to the wrong next-hop, and
use `ip route get TARGET_IP` to debug which route will
actually be used."