---
layout: default
title: "Subnet & CIDR"
parent: "Networking"
nav_order: 177
permalink: /networking/subnet-cidr/
number: "0177"
category: Networking
difficulty: ★★☆
depends_on: IP Addressing
used_by: Cloud — AWS, Cloud — Azure, Kubernetes, Networking
related: IP Addressing, NAT, Firewall, VPN
tags:
  - networking
  - subnet
  - cidr
  - ip
  - routing
---

# 177 — Subnet & CIDR

⚡ TL;DR — Subnetting divides an IP address space into smaller networks; CIDR (Classless Inter-Domain Routing) notation expresses this as prefix/length (e.g., 192.168.1.0/24), where /24 means 24 bits are the network portion, leaving 8 bits for 254 usable host addresses — essential for VPC design, firewall rules, and route summarisation.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before CIDR (pre-1993), IP addresses were allocated in three fixed classes: Class A (/8, 16M hosts), Class B (/16, 65K hosts), Class C (/24, 254 hosts). A company needing 1,000 addresses would get a Class B (/16, 65K addresses) — wasting 98% of the allocation. With only 128 Class A blocks available, address space was exhausted rapidly. Routing tables also bloated because every network was a separate entry.

**THE BREAKING POINT:**
By 1991, the internet routing table had 45,000 entries and was growing exponentially. Class-based allocation meant that MIT, HP, and Ford each held a full /8 (16M addresses) while most companies held fragmented Class C blocks requiring hundreds of routing table entries. The internet routing infrastructure was approaching collapse from routing table size.

**THE INVENTION MOMENT:**
CIDR (RFC 1519, 1993) replaced fixed classes with variable-length subnet masks (VLSM). Any IP address can now be associated with any prefix length /0 to /32. This enables: (1) efficient allocation — give a company a /22 (1022 hosts) instead of a wasted /16; (2) route aggregation (supernetting) — ISP can announce 198.0.0.0/8 instead of 256 separate /24s; (3) hierarchical routing — ISPs announce aggregated blocks, reducing global routing table size. Modern routing tables have ~900K entries (IPv4) instead of the projected billions that class-based routing would have required.

---

### 📘 Textbook Definition

**CIDR** (Classless Inter-Domain Routing) is the addressing and routing architecture (RFC 4632) that replaced class-based IP addressing. An IP address with CIDR notation is written as `address/prefix_length` (e.g., 192.168.1.0/24). The **prefix length** (1-32 for IPv4) indicates how many leading bits are the network address; remaining bits identify hosts. A **subnet** is a subdivision of an IP network. The **subnet mask** is an alternative notation: /24 = 255.255.255.0. Key values for a subnet: **network address** (all host bits 0), **broadcast address** (all host bits 1), **usable hosts** = 2^(32-prefix) - 2.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CIDR notation (like /24) tells you how many bits are the "network" part of an IP address — the remaining bits identify specific hosts, and the more bits for the host, the more devices fit in the subnet.

**One analogy:**

> A /24 is like a street: all houses on "192.168.1.x Street" share the same prefix (192.168.1). The last number (0-255) identifies the specific house. A /16 is like a whole town: "192.168.x.x Town" with 65K houses. A /32 is a single doorbell — one specific address, no room for others. Subnetting is the town planner deciding how to divide the land into streets.

**One insight:**
Every cloud provider (AWS VPC, Azure VNet, GCP VPC) is built entirely on subnets and CIDR. Understanding /16, /24, /28 is not optional for cloud engineers — it determines how many IPs you have for instances, load balancers, and internal services.

---

### 🔩 First Principles Explanation

**CIDR ARITHMETIC:**

```
Network: 192.168.1.0/24

Subnet mask:     255.255.255.0
Binary:          11111111.11111111.11111111.00000000
                 ←──────── 24 bits ────────→←8 bits→

Network address: 192.168.1.0   (host bits = 0000 0000)
Broadcast:       192.168.1.255 (host bits = 1111 1111)
Usable hosts:    192.168.1.1 - 192.168.1.254 = 254 hosts
Formula: 2^(32-24) - 2 = 2^8 - 2 = 254

Network: 10.0.0.0/8
Usable hosts: 2^24 - 2 = 16,777,214

Network: 192.168.1.128/26
Subnet mask: 255.255.255.192 (11000000)
Network:     192.168.1.128
Broadcast:   192.168.1.191
Hosts:       192.168.1.129 - 192.168.1.190 = 62 hosts
```

**COMMON PREFIX LENGTHS:**

```
/32 → 1 address    (single host route)
/31 → 2 addresses  (point-to-point link; RFC 3021)
/30 → 4 addresses  (2 usable — old point-to-point)
/29 → 8 addresses  (6 usable)
/28 → 16 addresses (14 usable — AWS min VPC subnet)
/27 → 32 addresses (30 usable)
/26 → 64 addresses (62 usable)
/25 → 128 addresses (126 usable)
/24 → 256 addresses (254 usable) — "Class C"
/23 → 512 addresses (510 usable)
/22 → 1,024 (1,022 usable)
/20 → 4,096 (4,094 usable)
/16 → 65,536 (65,534 usable) — "Class B"
/8  → 16,777,216 — "Class A"
```

**SUBNETTING A BLOCK:**

```
Starting block: 10.0.0.0/16 (65,534 hosts)

Divide into 4 equal /18 subnets:
  10.0.0.0/18   → 10.0.0.0   - 10.0.63.255   (16,382 hosts)
  10.0.64.0/18  → 10.0.64.0  - 10.0.127.255
  10.0.128.0/18 → 10.0.128.0 - 10.0.191.255
  10.0.192.0/18 → 10.0.192.0 - 10.0.255.255

Each /18 subnet into 4 equal /20 subnets:
  10.0.0.0/20   → 10.0.0.0   - 10.0.15.255   (4,094 hosts)
  10.0.16.0/20  → ...
  ...
```

**ROUTE AGGREGATION (SUPERNETTING):**

```
Instead of advertising:
  192.168.0.0/24
  192.168.1.0/24
  192.168.2.0/24
  192.168.3.0/24

Aggregate to: 192.168.0.0/22 (covers all four /24s)
→ One routing table entry instead of four
```

---

### 🧪 Thought Experiment

**SETUP:**
Design a VPC for a 3-tier application (web, app, database) with room for 3 availability zones each.

**ALLOCATION:**

```
VPC: 10.0.0.0/16 (65,534 usable addresses)

AZ-a (10.0.0.0/20 - 10.0.31.0/20):
  Web tier:  10.0.0.0/24   (254 hosts)
  App tier:  10.0.1.0/24   (254 hosts)
  DB tier:   10.0.2.0/24   (254 hosts)
  Reserved:  10.0.3.0/24 - 10.0.31.255

AZ-b (10.0.32.0/20 - 10.0.63.0/20):
  Web tier:  10.0.32.0/24
  App tier:  10.0.33.0/24
  DB tier:   10.0.34.0/24

AZ-c (10.0.64.0/20 - 10.0.95.0/20):
  Web tier:  10.0.64.0/24
  App tier:  10.0.65.0/24
  DB tier:   10.0.66.0/24

Remaining: 10.0.96.0/12 - 10.0.255.0/24 for future use
```

**FIREWALL RULES using CIDR:**

```
Allow DB access only from app tier:
Source: 10.0.1.0/24 OR 10.0.33.0/24 OR 10.0.65.0/24
→ Summarise: Allow 10.0.1.0/24, 10.0.33.0/24, 10.0.65.0/24
```

---

### 🧠 Mental Model / Analogy

> CIDR is like a file system path. /24 is like specifying up to the folder name — everything inside the folder (254 IPs) is addressed from there. /32 is like specifying an exact file. The prefix length is how specific your address is: /8 is a rough location (country), /24 is a neighbourhood, /32 is a single house. Route aggregation is like saying "deliver anything addressed to 'C:\Users\' to this machine" instead of separate routes for every file path under Users\.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A subnet is a smaller network within a larger network. CIDR notation (the "/24" part) tells you how big the subnet is. A /24 can have 254 devices; a /16 can have 65,000. When setting up cloud resources, you pick subnet sizes to match how many servers you need in each segment.

**Level 2 — How to use it (junior developer):**
In AWS VPC: choose a /16 for your VPC (65K IPs), then create /24 subnets per availability zone per tier. AWS reserves 5 IPs per subnet (network address, VPC router, DNS, future use, broadcast). So /28 gives 16 - 5 = 11 usable IPs. For Kubernetes: pod CIDR should be large enough for max pods per node × max nodes; with 110 pods/node and 50 nodes, need /21 (2046 addresses) minimum. Use `ipcalc` or Python `ipaddress` module to compute subnet ranges quickly.

**Level 3 — How it works (mid-level engineer):**
VLSM (Variable Length Subnet Masking): subnets within the same address space can have different prefix lengths. Enables efficient allocation: /30 for point-to-point links, /24 for server farms, /22 for large networks — all from the same /16 block. Route summarisation: advertise a supernet (less-specific route) to cover multiple subnets. The "longest prefix match" rule in routing: if a routing table has 0.0.0.0/0 (default) and 192.168.1.0/24, a packet destined for 192.168.1.5 matches the /24 (more specific). Longest prefix match is why you can create a more specific route to override a default route.

**Level 4 — Why it was designed this way (senior/staff):**
CIDR's variable-length prefix was a response to routing table explosion and address space exhaustion. The key algorithmic insight: IP forwarding can use longest prefix match with a trie data structure — routers lookup the destination IP and find the most specific matching route in O(log n) or O(1) with TCAM hardware. TCAM (Ternary Content-Addressable Memory) stores routing tables in hardware and does parallel lookup at line rate. Modern top-of-rack switches use TCAM for /32 host routes in data centre networks. IPv6 CIDR works identically but with 128-bit addresses and prefix lengths up to /128.

---

### ⚙️ How It Works (Mechanism)

```bash
# Calculate subnet details
ipcalc 192.168.1.0/24
# Shows: network, broadcast, first/last host, number of hosts

# Python ipaddress module
python3 -c "
import ipaddress
net = ipaddress.ip_network('10.0.0.0/22')
print(f'Network:    {net.network_address}')
print(f'Broadcast:  {net.broadcast_address}')
print(f'Hosts:      {net.num_addresses - 2}')
print(f'First host: {list(net.hosts())[0]}')
print(f'Last host:  {list(net.hosts())[-1]}')
# Subdivide into /24s
for subnet in net.subnets(new_prefix=24):
    print(f'  Subnet: {subnet}')
"

# Check if IP is in a subnet
python3 -c "
import ipaddress
ip = ipaddress.ip_address('10.0.1.50')
net = ipaddress.ip_network('10.0.0.0/22')
print(ip in net)  # True
"

# Show routing table with CIDR notation
ip route show
# 0.0.0.0/0 via 10.0.0.1 dev eth0 (default route)
# 10.0.0.0/8 dev eth0 proto kernel (directly connected)

# Find route for a specific destination
ip route get 8.8.8.8
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────┐
│  Route lookup: Longest Prefix Match              │
└──────────────────────────────────────────────────┘

 Routing table:
   0.0.0.0/0       → gateway (default)
   10.0.0.0/8      → local
   10.0.1.0/24     → eth1 (more specific)
   10.0.1.128/25   → eth2 (most specific)

 Destination 10.0.1.200:
   Matches 0.0.0.0/0  (/0 prefix length)
   Matches 10.0.0.0/8 (/8 prefix length)
   Matches 10.0.1.0/24 (/24 prefix length)
   Matches 10.0.1.128/25 (/25 prefix length) ← WINNER

   → Packet forwarded via eth2 (most specific match)
```

---

### 💻 Code Example

```python
import ipaddress

def vpc_subnet_plan(vpc_cidr: str, az_count: int = 3,
                    tier_count: int = 3) -> list[dict]:
    """Generate a VPC subnet plan."""
    vpc = ipaddress.ip_network(vpc_cidr, strict=False)
    # Use /24 subnets for each tier × AZ
    subnets = list(vpc.subnets(new_prefix=24))

    plan = []
    tiers = ["web", "app", "db"]
    az_labels = ["a", "b", "c"][:az_count]

    idx = 0
    for az in az_labels:
        for tier in tiers[:tier_count]:
            if idx >= len(subnets):
                break
            subnet = subnets[idx]
            plan.append({
                "az": f"us-east-1{az}",
                "tier": tier,
                "cidr": str(subnet),
                "usable_hosts": subnet.num_addresses - 5,  # AWS reserves 5
            })
            idx += 1

    return plan

plan = vpc_subnet_plan("10.0.0.0/16")
for s in plan:
    print(f"{s['az']:15s} {s['tier']:5s} {s['cidr']:20s} "
          f"({s['usable_hosts']} usable)")
```

---

### ⚖️ Comparison Table

| Prefix | Addresses | Usable   | Use Case             |
| ------ | --------- | -------- | -------------------- |
| /32    | 1         | 1        | Single host route    |
| /30    | 4         | 2        | P2P link (old style) |
| /28    | 16        | 11\*     | Small AWS subnet     |
| /24    | 256       | 249\*    | Standard subnet      |
| /22    | 1,024     | 1,019\*  | Medium subnet        |
| /16    | 65,536    | 65,531\* | VPC                  |

\*AWS reserves 5 IPs per subnet

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                       |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| /24 always means 255 hosts               | 2 addresses are reserved (network and broadcast), leaving 254. AWS further reserves 5 per subnet → 249 usable |
| Smaller prefix = smaller subnet          | Smaller prefix (e.g., /8) is a LARGER network. Larger prefix (e.g., /28) is a SMALLER network                 |
| Subnets must be the same size            | VLSM allows different prefix lengths in the same address space; mix /24, /27, /30 as needed                   |
| You can't change a subnet after creation | In most cloud providers, subnets are immutable after creation; plan ahead with enough space for growth        |

---

### 🚨 Failure Modes & Diagnosis

**Overlapping Subnets / Routing Conflict**

**Symptom:**
Two systems can't communicate despite being on different subnets. Routing doesn't work as expected.

```bash
# Check for overlapping routes
ip route show
# Look for multiple routes that could match same destination

# Check if two CIDRs overlap
python3 -c "
import ipaddress
a = ipaddress.ip_network('10.0.1.0/24')
b = ipaddress.ip_network('10.0.0.0/22')
print(f'Overlap: {a.overlaps(b)}')  # True — a is inside b
"

# Verify route for a specific host
ip route get 10.0.1.50
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`

**Builds On This:** `NAT`, `Firewall`, `VPN`, `BGP`, `Cloud — AWS` (VPC subnetting)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMULA      │ Usable hosts = 2^(32-prefix) - 2         │
├──────────────┼───────────────────────────────────────────┤
│ /24 = 254    │ /23 = 510 │ /22 = 1022 │ /16 = 65534     │
├──────────────┼───────────────────────────────────────────┤
│ ROUTING      │ Longest prefix match wins                 │
├──────────────┼───────────────────────────────────────────┤
│ AGGREGATION  │ Combine /24s into /22 for route summary   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "/N = first N bits are network; rest = host│
│              │ Longer prefix = smaller, more specific net"│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An AWS VPC is allocated 10.0.0.0/16. Design a complete subnet layout for: 3 AZs × (public subnet for ALB, private subnet for EC2, isolated subnet for RDS) = 9 subnets. Requirements: public subnets need ~50 IPs, private subnets need ~200 IPs, DB subnets need ~20 IPs. Choose the most efficient prefix sizes, leaving at least 50% of the VPC CIDR for future expansion. Show your math.

**Q2.** Explain how "longest prefix match" works in hardware using TCAM (Ternary Content-Addressable Memory). What makes TCAM different from regular RAM for routing lookups? Why can a BGP router with 900K routes still perform line-rate forwarding on a 100 Gbps port? What happens when the TCAM capacity is exhausted and some routes must be moved to software forwarding?
