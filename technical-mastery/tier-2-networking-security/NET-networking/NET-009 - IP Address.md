---
id: NET-009
title: "IP Address"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-008, NET-007
used_by: NET-024, NET-025, NET-027, NET-028, NET-043
related: NET-011, NET-024, NET-025, NET-026
tags:
  - networking
  - foundational
  - addressing
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/net/ip-address/
---

**⚡ TL;DR** - An IP address is the globally routable
32-bit (IPv4) or 128-bit (IPv6) identifier assigned to a
network interface. It tells every router in the world how
to forward packets to reach that interface.

| #009 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | TCP/IP Model (Four Layers), OSI Model (Seven Layers) | |
| **Used by:** | Subnet and CIDR, NAT, ARP, Routing Basics, DNS Resolution | |
| **Related:** | MAC Address, Subnet and CIDR, NAT, DHCP | |

---

### 🔥 The Problem This Solves

Before IP addressing, each network used its own proprietary
addressing scheme. Connecting two networks required custom
protocol translation. IP addressing provided a universal
addressing language: any device, anywhere in the world,
gets a number. Any router, worldwide, can use that number
to forward a packet toward its destination without knowing
the full path.

---

### 📘 Textbook Definition

An **IP address** (Internet Protocol address) is a numerical
label assigned to each interface on a computer network that
uses the Internet Protocol for communication. IPv4 addresses
are 32-bit integers written as four octets in dotted-decimal
notation (e.g., `192.168.1.100`). IPv6 addresses are 128-bit
integers written as eight groups of four hex digits separated
by colons (e.g., `2001:0db8:85a3::8a2e:0370:7334`). IP
addresses have two functions: host identification and
location addressing (routing).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An IP address is a 32-bit (IPv4) or 128-bit (IPv6) number
that uniquely identifies a network interface and tells
routers how to deliver packets to it.

**One analogy:**

> An IP address is like a postal address with a building
> (network ID) and apartment (host ID). The postal service
> (routers) looks at the building address (network prefix)
> to route the envelope to the right area, and the local
> mailman (last-hop router) uses the apartment number (host
> part) to deliver to the exact door.

**One insight:**
Every IP address has two parts: the **network prefix** (which
network is this?) and the **host ID** (which host within
that network?). A /24 prefix means 24 bits are network, 8
bits are host - so 256 possible addresses in that network.
The prefix length is why `192.168.1.0/24` means "all
addresses from `192.168.1.0` to `192.168.1.255`."

---

### 🔩 First Principles Explanation

**IPv4 Address Structure:**

```
┌──────────────────────────────────────────────────┐
│  IPv4 Address: 192.168.1.100/24                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  192    .168    .1      .100                     │
│  11000000.10101000.00000001.01100100             │
│  │                                │             │
│  └─── Network prefix (/24) ───────┘   Host ID   │
│       (first 24 bits)                (last 8)   │
│                                                  │
│  Network address:  192.168.1.0   (host = 0)     │
│  First host:       192.168.1.1                  │
│  Last host:        192.168.1.254                │
│  Broadcast:        192.168.1.255 (host = 255)   │
│  Total hosts:      254 (256 - 2 reserved)       │
└──────────────────────────────────────────────────┘
```

**Address Classes (historical but tested):**

```
┌──────────────────────────────────────────────────┐
│  IPv4 Address Classes                            │
├──────────┬──────────────┬───────────┬────────────┤
│  Class   │  Range       │  Default  │  Hosts     │
│          │  (first octet│  Prefix   │  Per Net   │
├──────────┼──────────────┼───────────┼────────────┤
│  A       │  1-126       │  /8       │  16M+      │
│  B       │  128-191     │  /16      │  65534     │
│  C       │  192-223     │  /24      │  254       │
│  D       │  224-239     │  (multicast, no hosts) │
│  E       │  240-255     │  (reserved, no hosts)  │
└──────────┴──────────────┴───────────┴────────────┘
```

**Reserved/Special IPv4 ranges:**

```
┌────────────────────────────────────────────────────┐
│  Special IPv4 Address Ranges                       │
├─────────────────┬──────────────────────────────────┤
│  Range          │  Purpose                         │
├─────────────────┼──────────────────────────────────┤
│  10.0.0.0/8     │  Private (RFC 1918) - not routed │
│  172.16.0.0/12  │  Private (RFC 1918) - not routed │
│  192.168.0.0/16 │  Private (RFC 1918) - not routed │
│  127.0.0.0/8    │  Loopback (localhost)             │
│  169.254.0.0/16 │  Link-local (APIPA, no DHCP)     │
│  0.0.0.0        │  Unspecified (bind to all)        │
│  255.255.255.255│  Limited broadcast               │
│  100.64.0.0/10  │  Shared (carrier-grade NAT)      │
└─────────────────┴──────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
You see an IP address in a log: `172.31.4.23`. Is this
reachable from the internet?

- `172.31.4.23` - this is in the `172.16.0.0/12` private
  range. The range is `172.16.0.0` to `172.31.255.255`.
  `172.31.4.23` falls within this range. It is a private
  address. It cannot be reached directly from the internet.
  It exists behind NAT.

**FOLLOW-UP:**
The log also shows a connection from `52.1.200.3`. Is this
private or public? `52.x.x.x` is not in 10/8, 172.16/12,
or 192.168/16. Not loopback (127). Not link-local (169.254).
Not special. Therefore it is a public, globally routable
IP address.

**THE INSIGHT:**
Recognizing private vs public IP ranges is a daily skill.
Private addresses appear in: local machine `ip addr` output,
VPC/cloud internal addresses, container network addresses
(Docker uses `172.17.0.0/16`), Kubernetes pod CIDRs (often
`10.244.0.0/16` or `192.168.0.0/16`). Any time you see
`10.`, `172.16-31.`, or `192.168.`, you are looking at a
private address requiring NAT to reach the internet.

---

### 🧠 Mental Model / Analogy

> IPv4 addresses are like employee ID badges in a large
> company with subsidiaries. The first three digits (company
> ID) tell security which subsidiary the employee belongs
> to - useful for routing to the right building. The last
> digit (individual ID) identifies the specific person
> within that subsidiary. Security (router) only needs to
> know the company ID to send the package to the right
> building. The building's receptionist uses the individual
> ID to find the right person.
>
> Private addresses (10.x.x.x) are like internal extension
> numbers - they work within the building but cannot be used
> for external calls without going through the switchboard
> (NAT).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An IP address is a unique number that identifies a device
on a network. Like a phone number, every device needs one
to receive data.

**Level 2 - How to use it (junior developer):**
Use `ip addr show` (Linux) or `ipconfig` (Windows) to see
your IP addresses. `127.0.0.1` or `::1` is always "this
machine" (loopback). `0.0.0.0` means "all interfaces" when
binding a server socket. IPs starting with 10, 172.16-31,
or 192.168 are private and not internet-accessible.

**Level 3 - How it works (mid-level engineer):**
An IP address has two roles: identification (which host?)
and routing (how to get there?). Routers maintain routing
tables that map network prefixes to next-hop addresses. A
packet's destination IP is compared against routing table
entries with longest-prefix match: the most specific match
wins. `ip route get <target>` shows which route and
interface Linux would use for a specific destination.

**Level 4 - Why it was designed this way (senior/staff):**
IPv4's 32-bit address space (4.3 billion addresses) seemed
sufficient in 1981. CIDR (Classless Inter-Domain Routing)
in 1993 extended the lifetime by replacing fixed class
boundaries with flexible prefixes. NAT in the mid-1990s
extended it further by allowing entire networks to share
one public IP. IPv6's 128-bit space (340 undecillion
addresses) was designed to never run out - but full IPv6
transition is still incomplete 30 years later because NAT
"solved" the shortage well enough to delay migration.

**Level 5 - Mastery (distinguished engineer):**
IP address assignment is a distributed resource allocation
problem. IANA allocates blocks to Regional Internet
Registries (RIRs like ARIN, RIPE). RIRs allocate to ISPs.
ISPs allocate to customers. ARIN ran out of unallocated
IPv4 in 2015. RIPE ran out in 2019. IPv4 addresses are now
traded on a secondary market for $20-50 per address.
This scarcity fundamentally changed cloud networking:
AWS charges per public IPv4 per hour. Large internet
companies (Google, Facebook) obtained /8 blocks (16 million
addresses each) in the 1990s and those are now extremely
valuable assets.

---

### ⚙️ How It Works (Mechanism)

**IPv4 packet header (IP address location):**

```
┌──────────────────────────────────────────────────┐
│  IPv4 Header (20 bytes minimum)                  │
├──────────┬───────────────────────────────────────┤
│  Byte 0  │  Version(4) | IHL | DSCP | ECN        │
│  Byte 1  │  Total Length (16 bits)               │
│  Byte 2  │  Identification (16 bits)             │
│  Byte 3  │  Flags | Fragment Offset              │
│  Byte 4  │  TTL | Protocol | Header Checksum     │
│  Byte 5  │  Source IP Address (32 bits)          │
│  Byte 6  │  Destination IP Address (32 bits)     │
│  Byte 7+ │  Options (if IHL > 5) | Payload       │
└──────────┴───────────────────────────────────────┘
```

**Linux IP address commands:**
```bash
# Show all IP addresses on all interfaces
ip addr show

# Show IPv4 only
ip -4 addr show

# Show IPv6 only
ip -6 addr show

# Which route and interface does traffic to
# a specific IP use?
ip route get 8.8.8.8
# Output: 8.8.8.8 via 10.0.0.1 dev eth0
#   src 10.0.0.100 uid 0

# All routes in the routing table
ip route show table main

# Add a static IP to an interface
ip addr add 192.168.1.50/24 dev eth0
```

**IPv6 address format:**
```bash
# Full IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
# Compressed: 2001:db8:85a3::8a2e:370:7334
# Rules: leading zeros in group can be omitted,
#        one run of consecutive all-zero groups
#        can be replaced with ::

# Loopback IPv6:
::1
# (equivalent to 127.0.0.1 in IPv4)

# Link-local (auto-assigned, not routable off-link):
fe80::1a2b:3c4d:5e6f:7890%eth0
# %eth0 = scope identifier (required for link-local)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Packet routing using IP addresses:**
1. Application sends data to `google.com` - DNS resolves
   to `142.250.80.78`.
2. OS checks routing table: `142.250.80.78` matches
   default route `0.0.0.0/0` via gateway `10.0.0.1`.
3. OS sends IP packet with `src=10.0.0.100`,
   `dst=142.250.80.78` to gateway `10.0.0.1`.
4. Gateway (router) receives packet, looks up
   `142.250.80.78` in its routing table, finds next hop
   is ISP's border router.
5. Each router repeats: check routing table, forward
   to next hop.
6. Google's router receives packet, IP matches its
   interface, delivers to local process.

**WHAT CHANGES AT SCALE:**
Cloud providers assign private IPs from large RFC 1918
pools (AWS uses `10.0.0.0/8` internally). Kubernetes
assigns pod IPs from cluster CIDR (`10.244.0.0/16` in
Flannel). Service mesh sidecars intercept all IP traffic
before it leaves the pod. At 10,000 pod scale, IP address
management (IPAM) is a critical service: pods are created
and destroyed hundreds of times per hour, requiring
automated IP assignment and revocation.

---

### ⚖️ Comparison Table

| Feature | IPv4 | IPv6 |
|---|---|---|
| **Address length** | 32 bits | 128 bits |
| **Notation** | Dotted decimal: `192.0.2.1` | Colon hex: `2001:db8::1` |
| **Address space** | ~4.3 billion | 340 undecillion |
| **NAT required?** | Yes (address scarcity) | No (but still used) |
| **Header size** | 20-60 bytes | 40 bytes fixed |
| **Checksum in header** | Yes | No (moved to transport) |
| **Auto-configuration** | DHCP or manual | SLAAC (auto from MAC) |
| **Broadcast** | Yes | No (multicast instead) |
| **Internet adoption** | ~100% | ~40% (Google) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A machine has one IP address | A machine has one IP per interface, and can have multiple interfaces and multiple IPs per interface. A Linux server commonly has: `127.0.0.1` (loopback), `10.0.0.5` (private), `172.17.0.1` (Docker bridge), `::1` (IPv6 loopback). |
| Private IPs are secure | Private IPs are not routable on the internet, but they provide ZERO security within the network. Any machine in the same VPC can reach any other machine's private IP unless firewall rules block it. |
| `0.0.0.0` means "no IP" | `0.0.0.0` means "all interfaces" when used as a bind address. `server.listen(0.0.0.0, 8080)` listens on all interfaces. It does NOT mean "no address." |
| IPv6 replaces IPv4 | After 30 years, most networks run dual-stack (both IPv4 and IPv6). IPv6-only networks exist but are rare. Full IPv4 replacement is not expected in the next decade. |

---

### 🚨 Failure Modes & Diagnosis

**IP Address Conflict (Duplicate IP)**

**Symptom:** Two machines assigned the same IP. Network
is intermittent for one or both. Traffic is randomly
delivered to the wrong machine. ARP cache poisoning can
cause the symptom even without a true duplicate.

**Root Cause:** DHCP lease database corruption. Manual
static IP assignment overlapping with DHCP pool. Container
networking misconfiguration assigning overlapping CIDRs.

**Diagnostic Command / Tool:**
```bash
# Detect IP conflict (look for duplicate ARP)
arping -D -I eth0 192.168.1.50
# -D = duplicate detection mode
# Exits 0 if no duplicate, 1 if duplicate found

# Show ARP table (look for duplicate MACs)
arp -n | awk '{print $1}' | sort | uniq -d

# tcpdump for ARP conflicts
sudo tcpdump -n -i eth0 arp and "arp[7] == 2" \
  and "arp[24:4] == 0xc0a80132"
# (Replace hex with target IP in hex)
```

**Fix:** Identify which machine has the "wrong" IP
(check DHCP leases). Remove the static assignment or
exclude the range from DHCP pool. Force ARP cache refresh
on affected hosts: `ip neigh flush dev eth0`.

**Prevention:** Separate DHCP range from static assignment
range. Use `/etc/hosts` records with a DHCP reservation
(fixed DHCP by MAC) instead of manual static IPs.

---

**Cloud EC2 Instance Not Reachable by Public IP**

**Symptom:** EC2 instance has a public IP assigned in the
console. Cannot connect via SSH. `telnet public_ip 22`
times out.

**Root Cause:** Security group (firewall) blocks inbound
port 22. Subnet route table has no Internet Gateway route.
Instance has public IP but it's not the elastic IP.

**Diagnostic Command / Tool:**
```bash
# From the instance itself
curl -s http://169.254.169.254/latest/meta-data/public-ipv4
# AWS metadata service - returns assigned public IP

# Check if port 22 is open (from outside)
nmap -p 22 public_ip
# PORT  STATE    SERVICE
# 22/tcp filtered ssh  ← security group blocking

# From inside instance: can it reach internet?
curl -s http://checkip.amazonaws.com
# Should return its own public IP if IGW is configured
```

**Fix:** Add inbound rule to security group: TCP port 22
from your IP. Add route to subnet route table: `0.0.0.0/0
→ igw-xxxxxxxx`. Confirm instance is in public subnet
(auto-assign public IP enabled OR Elastic IP attached).

**Prevention:** Use infrastructure-as-code (Terraform,
CloudFormation) to define security groups and route tables,
not manual console clicks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `TCP/IP Model (Four Layers)` - the framework that
  explains what role IP addresses play
- `OSI Model (Seven Layers)` - OSI L3 = Network layer
  where IP addresses live

**Builds On This (learn these next):**
- `Subnet and CIDR Notation` - how to carve up IP address
  space into networks
- `NAT (Network Address Translation)` - how private IPs
  reach the internet
- `ARP (Address Resolution Protocol)` - how IP addresses
  map to MAC addresses on local networks

**Alternatives / Comparisons:**
- `MAC Address` - the hardware address at layer 2 that
  complements the logical IP address at layer 3

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 32-bit (IPv4) or 128-bit (IPv6) network   │
│              │ interface identifier                      │
├──────────────┼───────────────────────────────────────────┤
│ PRIVATE RANGES│ 10.0.0.0/8, 172.16.0.0/12,              │
│              │ 192.168.0.0/16 (RFC 1918 - not routed)   │
├──────────────┼───────────────────────────────────────────┤
│ SPECIAL      │ 127.0.0.1=loopback, 0.0.0.0=all-ifaces,  │
│              │ 169.254/16=link-local (no DHCP)           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ IP = network prefix + host ID. Prefix     │
│              │ length (/24) determines network size.     │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ ip addr show, ip route get X.X.X.X,       │
│              │ arping -D for conflict detection           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ IPv4 (universal support) vs IPv6          │
│              │ (no NAT needed, 128-bit space)            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every packet carries src+dst IP.         │
│              │  Routers forward based on dst prefix."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Subnet/CIDR → NAT → DHCP → ARP           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Private ranges: 10/8, 172.16-31/12, 192.168/16. Behind
   NAT. Not reachable from internet without a VPN or tunnel.
2. IP address has 2 parts: network prefix + host ID.
   The `/N` notation tells you how many bits are prefix.
   A `/24` means 256 addresses, 254 usable.
3. `0.0.0.0` = bind to all interfaces. `127.0.0.1` =
   loopback (same machine). `169.254.x.x` = no DHCP server
   found (APIPA auto-assigned - investigate your DHCP).

**Interview one-liner:**
"IPv4 addresses are 32-bit numbers written as four octets.
They have two parts: network prefix and host ID, separated
by the subnet mask. RFC 1918 reserves 10/8, 172.16/12, and
192.168/16 as private (non-routable). NAT allows private
addresses to reach the internet by translating to a public
IP at the gateway. IPv4 has 4.3B addresses and ran out -
IPv4 is now traded on a secondary market. IPv6 (128 bits)
solves scarcity but coexists with IPv4 in dual-stack."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Addressing schemes need two properties: enough unique
identifiers for all entities (space), and enough structure
to enable efficient routing (hierarchy). The failure of
IPv4 demonstrates that address space is a finite resource
that must be designed with growth in mind. The success of
CIDR demonstrates that adding flexible hierarchy to an
existing addressing scheme can extend its lifetime decades
beyond the original design.

**Where else this pattern appears:**
- **Phone numbers** - country code + area code + number =
  3-level hierarchy. Adding 1-800 and mobile ranges extended
  the system without renumbering all existing numbers.
- **Database keys** - UUID vs sequential integer debate:
  UUID has large address space but poor index locality;
  sequential integers have small space but excellent B-tree
  performance.

---

### 💡 The Surprising Truth

AWS charges $0.005 per hour per public IPv4 address as of
February 2024 - a new policy that costs companies with
large fleets millions of dollars annually. A company with
10,000 EC2 instances each having a public IP pays $438,000
per year just for IPv4 addresses. This change was explicitly
to accelerate IPv6 adoption. AWS itself uses private IPv4
internally (via NAT64 gateways for outbound IPv4) and
routes internally over IPv6, then translates at the edge.
The "global shortage" of IPv4 is making headlines in cloud
billing departments.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the difference between public, private, and
   loopback IP addresses and give two examples of each.
2. **DEBUG** a "connection refused" error by checking
   whether the destination IP is reachable (ping), whether
   the route exists (`ip route get`), and whether the source
   IP is what you expect (NAT or not).
3. **DECIDE** whether an IP in a log is private or public,
   in what private range, and what that implies about NAT.
4. **BUILD** a mental model of how a packet's IP addresses
   are used at each router hop from client to server.
5. **EXTEND** the addressing concepts to explain why Docker
   assigns `172.17.0.0/16` to containers and how that
   affects connectivity to the host and to the internet.

---

### 🧠 Think About This Before We Continue

**Q1.** A Docker container has IP `172.17.0.3`. Your host
machine has IP `10.0.0.50`. Can the container reach
`google.com`? If yes, what mechanism allows a `172.17.x.x`
private address to reach the internet through your host's
`10.0.0.50` interface? Can a process outside Docker connect
to the container at `172.17.0.3` from the internet directly?

*Hint: Trace the layers of NAT: host→internet NAT, and
then container→host NAT. These are nested NAT levels.*

**Q2.** Two AWS EC2 instances in different VPCs need to
communicate. VPC A uses `10.0.0.0/16` and VPC B uses
`10.1.0.0/16`. If you set up VPC peering, can they
communicate? What if both used `10.0.0.0/16`? Why does
IP range overlap break VPC peering?

*Hint: Routing tables can only have one entry for a prefix.
If two networks have identical prefixes, a router cannot
distinguish between them.*

**Q3.** [Hands-On] Run `ip addr show` and list all IP
addresses on your machine with their interface names.
Identify: which is loopback, which is your LAN IP, which
are Docker/VM bridge IPs (if any). Then run
`curl -s https://api.ipify.org` to see your public IP.
Why is the public IP different from all IPs in `ip addr`?
What device in your network performs the translation?