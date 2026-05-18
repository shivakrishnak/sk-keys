---
id: NET-011
title: "MAC Address"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-007
used_by: NET-027, NET-024
related: NET-009, NET-027, NET-016
tags:
  - networking
  - foundational
  - data-link
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/net/mac-address/
---

**⚡ TL;DR** - A MAC address is a 48-bit hardware identifier
burned into a network interface card (NIC). It enables
local delivery on a single network segment - routers use
IP addresses for global routing, but switches use MAC
addresses for local frame delivery.

| #011 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, OSI Model (Seven Layers) | |
| **Used by:** | ARP (Address Resolution Protocol), Subnet and CIDR | |
| **Related:** | IP Address, ARP, Network Topology | |

---

### 🔥 The Problem This Solves

Routing a packet globally to the right machine (IP) does
not tell a switch which physical port on the local segment
to send it out. IP addresses are hierarchical and globally
significant. MAC addresses are flat, locally significant
hardware IDs. The two-layer addressing system (IP for global
routing, MAC for local delivery) allows any physical network
technology (Ethernet, WiFi) to be used as the link layer
while IP routing remains unchanged.

---

### 📘 Textbook Definition

A **MAC address** (Media Access Control address) is a 48-bit
hardware identifier assigned to a network interface card
(NIC) by the manufacturer, globally unique by convention,
written as six octets in colon-separated hex (e.g.,
`aa:bb:cc:dd:ee:ff`). It operates at OSI layer 2 (Data
Link). On a local network, Ethernet switches use MAC
addresses in the destination field of Ethernet frames to
decide which port to forward each frame to. IP addresses
are resolved to MAC addresses by the ARP protocol before
the first packet is sent to a local host.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MAC addresses are the "apartment number within a building"
for the local network segment - where IP is the building's
street address.

**One analogy:**

> A MAC address is like an employee badge number. Every
> badge has a unique number that identifies exactly one
> person in the building. But to reach a specific employee,
> you first need to know they're in this building (IP), then
> use the badge directory (ARP) to find their desk location
> (MAC) and deliver the message directly.

**One insight:**
MAC addresses change at every router hop. When a packet
is forwarded through a router, the router strips the old
Ethernet frame (with its source/dest MAC) and creates a
new Ethernet frame for the next hop, with new MAC addresses.
IP addresses stay constant end-to-end. This is the key
distinction between OSI layer 2 (frame/MAC) and layer 3
(packet/IP) operation.

---

### 🔩 First Principles Explanation

**MAC address structure:**

```
┌────────────────────────────────────────────────────┐
│  MAC Address Format: aa:bb:cc:dd:ee:ff             │
├────────────────────────────────────────────────────┤
│  First 3 bytes: OUI (Organizationally Unique ID)  │
│  Assigned by IEEE to NIC manufacturers             │
│                                                    │
│  Last 3 bytes: NIC-specific ID                    │
│  Assigned by manufacturer (unique per device)     │
│                                                    │
│  Examples:                                         │
│  00:1a:2b → Apple Inc.                            │
│  00:50:56 → VMware (virtual NICs)                 │
│  02:42:ac → Docker (container virtual NICs)       │
│  52:54:00 → QEMU/KVM (virtual machines)           │
│                                                    │
│  Bit 0 of first byte:                             │
│  0 = Unicast (specific device)                    │
│  1 = Multicast (group of devices)                 │
│                                                    │
│  Bit 1 of first byte:                             │
│  0 = Globally unique (OUI-assigned)               │
│  1 = Locally administered (override by software)  │
└────────────────────────────────────────────────────┘
```

**MAC address vs IP address comparison:**

```
┌────────────────────────────────────────────────────┐
│  MAC vs IP                                         │
├──────────────────┬─────────────┬───────────────────┤
│  Attribute       │  MAC        │  IP               │
├──────────────────┼─────────────┼───────────────────┤
│  Layer           │  L2 (Data   │  L3 (Network)     │
│                  │  Link)      │                   │
│  Length          │  48 bits    │  32 (v4), 128 (v6)│
│  Scope           │  Local      │  Global           │
│                  │  segment    │                   │
│  Persistence     │  Changes at │  Constant end-    │
│                  │  each hop   │  to-end           │
│  Assignment      │  Hardware   │  OS/DHCP config   │
│  Routing use     │  Switch     │  Router           │
│                  │  forwarding │  forwarding       │
│  Human-readable  │  No (hex)   │  Yes (decimal)    │
└──────────────────┴─────────────┴───────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
You run `tcpdump -en` and capture packets. Each line shows
the Ethernet frame with MAC addresses and the IP packet
inside it. You see:

```
aa:bb:cc:11:22:33 > 00:11:22:aa:bb:cc, IPv4
  src=192.168.1.100 dst=8.8.8.8
```

The source MAC `aa:bb:cc:11:22:33` is your machine's NIC.
The destination MAC `00:11:22:aa:bb:cc` is your router's NIC.
The source IP is your machine's IP. The destination IP is
Google's DNS server.

**THE INSIGHT:**
The destination MAC is your router, not Google's NIC.
Why? Google's NIC is 10 hops away - you don't know its MAC
and you can't reach it directly anyway. You send the frame
to your router (local MAC). The router will strip the
Ethernet frame, check the IP destination, and create a new
Ethernet frame with new MACs for the next hop. The IP
addresses (`192.168.1.100` → `8.8.8.8`) travel unchanged.
The MAC addresses change at every router.

---

### 🧠 Mental Model / Analogy

> Sending a package internationally:
> - IP address = the ultimate destination country/city/address
>   (never changes throughout the journey)
> - MAC address = the carrier's tracking labels, replaced
>   at each hub (UPS → DHL → local post → final mile)
> Every hub strips the old label and attaches a new one for
> the next leg. Only the final hub looks at the actual
> delivery address (IP) to deliver to the door.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Every network card has a hardware address (MAC) burned in
at the factory. Local switches use this hardware address to
deliver frames within the same building (network segment).

**Level 2 - How to use it (junior developer):**
Use `ip link show` to see MAC addresses on your machine.
In AWS or cloud environments, virtual NIC MACs look like
`02:xx:xx:xx:xx:xx` (locally administered). Docker
containers get MACs starting with `02:42:ac` by default.
If `arping` returns "no response" for a local IP, the host
is down or ARP is blocked by a firewall.

**Level 3 - How it works (mid-level engineer):**
Switches maintain a MAC address table: port → MAC mappings.
When a frame arrives, the switch records the source MAC on
the input port. When forwarding, it looks up the destination
MAC in its table and sends out the corresponding port. If
the destination MAC is unknown, it floods the frame to all
ports (unknown unicast flood). This is why a new device
on a network triggers a brief flood until the switch learns
its MAC.

**Level 4 - Why it was designed this way (senior/staff):**
The MAC address design allows IP to be hardware-agnostic.
IPv4 over Ethernet, IPv4 over WiFi, IPv4 over fiber - all
use the same IP layer but different link-layer addressing.
ARP bridges L2 and L3 by dynamically discovering the MAC
address for a given IP. This allowed Ethernet, Token Ring,
FDDI, and WiFi to all work as IP link layers without
changing the IP protocol.

**Level 5 - Mastery (distinguished engineer):**
MAC address tables in switches have finite capacity. In
large networks, MAC table overflow (intentional or due to
VM migration) forces the switch to flood all frames, causing
network-wide broadcast storms. This is why enterprise
networks use VLANs: limiting MAC table scope to one VLAN
reduces the number of MACs each switch must learn.
Spanning Tree Protocol (STP) prevents loops that would
cause frames to circulate forever when the switch floods.

---

### ⚙️ How It Works (Mechanism)

```bash
# Show MAC addresses on Linux
ip link show
# Output:
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
#   link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff

# Show ARP table (IP → MAC mappings)
ip neigh show
# 192.168.1.1 dev eth0 lladdr 00:11:22:33:44:55 REACHABLE

# Detect MAC address of a specific IP on local network
arping -I eth0 192.168.1.1

# Capture MAC addresses with tcpdump
sudo tcpdump -en -i eth0 -c 5
# Shows: timestamp MAC>MAC ethertype IP
#   src_ip > dst_ip protocol
```

**Ethernet frame with MAC addresses:**

```
┌────────────────────────────────────────────────────┐
│  Ethernet II Frame (minimum 64 bytes)              │
├────────────────────┬───────────────────────────────┤
│  Dest MAC (6 bytes)│  Next hop device's MAC        │
│  Src  MAC (6 bytes)│  Sender's NIC MAC             │
│  EtherType (2 bytes│  0x0800=IPv4, 0x0806=ARP      │
│                    │  0x86DD=IPv6, 0x8100=VLAN     │
│  Payload           │  IP packet (46-1500 bytes)    │
│  FCS (4 bytes)     │  CRC error check              │
└────────────────────┴───────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**How MAC addresses change across hops:**
```
Client → Router1 → Router2 → Server

Hop 1 (Client → Router1):
  frame: src=client_mac, dst=router1_mac
  packet: src=client_ip, dst=server_ip

Hop 2 (Router1 → Router2):
  frame: src=router1_out_mac, dst=router2_mac
  packet: src=client_ip, dst=server_ip (UNCHANGED)

Hop 3 (Router2 → Server):
  frame: src=router2_out_mac, dst=server_mac
  packet: src=client_ip, dst=server_ip (UNCHANGED)
```

IP addresses persist. MAC addresses are replaced at each
router. This is the fundamental difference between L2 and
L3 forwarding.

---

### ⚖️ Comparison Table

| Feature | MAC | IP |
|---|---|---|
| **Uniqueness scope** | Globally unique (by convention) | Globally routable (public IPs) |
| **Assignment** | Hardware (manufacturer) | Software (DHCP or static) |
| **Can be changed** | Yes (MAC spoofing: `ip link set eth0 address xx:xx:xx:xx:xx:xx`) | Yes (reconfigure) |
| **Used by** | Switches, ARP | Routers, DNS |
| **Broadcast address** | `ff:ff:ff:ff:ff:ff` | `255.255.255.255` (IPv4) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| MAC addresses are globally unique | By convention and manufacturer practice, yes. But MAC spoofing is trivial and common. Virtual machines and containers routinely use randomly generated MACs. Two identical MACs on the same network segment cause packet delivery failures. |
| You can track someone by their MAC address across the internet | MACs never traverse a router - they are stripped at every hop. They are only visible within the same local network segment. Internet-level tracking uses IP addresses, not MACs. |
| MAC addresses are fixed hardware | They can be changed in software. On Linux: `ip link set eth0 address 02:11:22:33:44:55`. iPhones use random MACs for WiFi scanning (since iOS 14) to prevent location tracking. |

---

### 🚨 Failure Modes & Diagnosis

**ARP Spoofing (MAC-based Attack)**

**Symptom:** Traffic is being intercepted. MITM attack.
Legitimate host stops receiving traffic even though it is
active. ARP table shows a MAC address that changed recently.

**Root Cause:** Attacker sends gratuitous ARP replies
claiming their MAC corresponds to a legitimate host's IP.
All hosts in the network update their ARP cache. Traffic
intended for the legitimate host is sent to attacker's MAC.

**Diagnostic Command / Tool:**
```bash
# Check ARP table for suspicious entries
# (same MAC for two different IPs = ARP spoofing)
ip neigh show | awk '{print $5}' | \
  sort | uniq -d

# Capture ARP traffic
sudo tcpdump -n -i eth0 arp

# Look for: ARP reply who-has X tell Y
# from unexpected MACs
```

**Fix:** Use static ARP entries for critical hosts.
Use 802.1X port authentication. Use Dynamic ARP
Inspection (DAI) on managed switches.

**Prevention:** Enable DAI on switches. Segment networks
with VLANs to limit ARP blast radius. Use encrypted
protocols (TLS) so interception reveals only metadata.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `IP Address` - the layer 3 complement to MAC's layer 2
- `OSI Model (Seven Layers)` - OSI L2 is where MAC lives

**Builds On This (learn these next):**
- `ARP (Address Resolution Protocol)` - how IP maps to MAC
- `Subnet and CIDR Notation` - defining which IPs share a
  local segment (and thus use ARP/MAC)

**Alternatives / Comparisons:**
- `IP Address` - global routing address vs local delivery
  address

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 48-bit hardware ID for NIC. OSI L2.       │
│              │ Local delivery only (one network segment) │
├──────────────┼───────────────────────────────────────────┤
│ FORMAT       │ aa:bb:cc:dd:ee:ff (hex octets)            │
│              │ First 3 bytes = OUI (manufacturer)        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ MAC changes at every router hop.          │
│              │ IP persists end-to-end.                   │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ ip link show, ip neigh show, arping       │
│              │ tcpdump -en to see MACs in frames         │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Relying on MACs for security (easily      │
│              │ spoofed). Use 802.1X + TLS instead.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Switches forward by MAC (local).         │
│              │  Routers route by IP (global)."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ARP → how IP resolves to MAC on           │
│              │ local network segment                     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. MAC is 48-bit hardware address, used within one network
   segment. IP is 32/128-bit logical address, used globally.
2. MAC changes at every router hop; IP stays constant.
   Switches use MAC. Routers use IP.
3. MAC spoofing is trivial. Virtual machines, containers,
   and modern phones all use randomized MACs.

**Interview one-liner:**
"A MAC address is a 48-bit hardware identifier (written as
`aa:bb:cc:dd:ee:ff`) assigned by the NIC manufacturer.
Ethernet switches use MAC addresses to deliver frames within
a local network segment. Unlike IP addresses, MAC addresses
change at every router hop - the router strips the incoming
Ethernet frame and creates a new one for the next hop.
ARP (Address Resolution Protocol) maps IP addresses to MAC
addresses on local networks."

---

### 💡 The Surprising Truth

Modern operating systems and smartphones no longer use
permanent MAC addresses for WiFi scanning. Since iOS 14
(2020) and Android 10 (2019), phones use randomized MAC
addresses when scanning for and connecting to WiFi networks
(unless you specifically opt in to use the permanent MAC
with a trusted network). This was implemented to prevent
location tracking: retailers and tracking companies had
been building systems to track individuals' movements by
following their permanent WiFi MAC across retail locations.
The "permanent, unique" MAC address property - foundational
to network design - is now deliberately broken at the device
level as a privacy measure.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why MAC addresses change at every router
   hop while IP addresses remain constant, with a specific
   protocol mechanism (ARP, Ethernet frame replacement).
2. **DEBUG** ARP table issues using `ip neigh show` and
   identify duplicate MACs indicating ARP spoofing.
3. **DECIDE** whether a connectivity issue is L2 (MAC/ARP)
   or L3 (IP/routing) based on diagnostic output.
4. **BUILD** the mental model of how a switch builds its
   MAC address table by observing source MACs on each port.
5. **EXTEND** MAC concepts to explain how VLANs partition
   MAC address spaces and why this is needed in large networks.

---

### 🧠 Think About This Before We Continue

**Q1.** When a switch receives a frame with a destination
MAC it has never seen before, what does it do? What is the
network impact of this behavior at scale? How do broadcast
storms form from this behavior, and what protocol was
invented to prevent them?

*Hint: Unknown unicast flooding is the mechanism. At scale
with thousands of hosts it creates significant overhead.
Spanning Tree Protocol prevents the loops that cause storms.*

**Q2.** When you clone a virtual machine in VMware or
VirtualBox, what happens to the network adapter's MAC
address? Why can this cause connectivity problems if two
VMs run simultaneously with the same MAC? What does the
hypervisor do to prevent this?

*Hint: Think about what a switch's MAC table would do if
it saw the same MAC on two different ports simultaneously.*

**Q3.** [Hands-On] Run `ip neigh show` to see your ARP
table. Identify your default gateway's MAC address. Now
run `ip link show` and find your machine's own MAC. Run
`sudo arping -I eth0 -c 3 <gateway_ip>` to send ARP
requests to your gateway. What MAC address responds?
Compare it to the ARP table entry. Do they match?