---
layout: default
title: "IP Addressing"
parent: "Networking"
nav_order: 176
permalink: /networking/ip-addressing/
number: "0176"
category: Networking
difficulty: ★☆☆
depends_on: OSI Model, TCP/IP Stack
used_by: Networking, Cloud — AWS, Cloud — Azure, Kubernetes
related: Subnet & CIDR, NAT, DNS, ARP
tags:
  - networking
  - ip
  - addressing
  - ipv4
  - ipv6
---

# 176 — IP Addressing

⚡ TL;DR — An IP address is a 32-bit (IPv4) or 128-bit (IPv6) number that uniquely identifies a network interface; IPv4 addresses are written as 4 octets (192.168.1.1), split into network and host portions by a subnet mask, and are nearly exhausted — driving IPv6 adoption and NAT as workarounds.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without addressing, every computer would need a direct physical connection to every other computer it communicates with — a complete mesh of cables. Networks would not be possible: you couldn't route a packet across multiple intermediate nodes because there would be no way to specify the destination.

**THE BREAKING POINT:**
Ethernet addresses (MAC addresses) identify hardware on the same local network. But a MAC address cannot be used for routing across networks — routers don't know the "location" of a MAC address in the network topology. You need a hierarchical addressing scheme where the address encodes location (which network you're on), enabling routers to make forwarding decisions without knowing every device on the internet.

**THE INVENTION MOMENT:**
IP addressing provides hierarchical, location-based addressing. An IPv4 address is divided into a network portion (identifies which network) and host portion (identifies which device on that network). Routers only need to know routes to networks — not to every individual host. This enables the internet to scale from 4 hosts in 1969 to billions today, with routers making forwarding decisions using routing tables of manageable size.

---

### 📘 Textbook Definition

An **IP address** is a numerical label assigned to each device on a network that uses the Internet Protocol. **IPv4** uses 32-bit addresses, written in dotted-decimal notation (e.g., 192.168.1.1), supporting ~4.3 billion addresses. **IPv6** uses 128-bit addresses, written in hexadecimal groups (e.g., 2001:0db8:85a3::8a2e:0370:7334), supporting ~3.4 × 10^38 addresses. IPv4 addresses are classified into: **public** (globally routable), **private** (RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 — non-routable on the public internet), **loopback** (127.0.0.1), and **link-local** (169.254.0.0/16 — APIPA, assigned when no DHCP). IPv6 equivalents: `::1` (loopback), `fe80::/10` (link-local), `fc00::/7` (unique local — private).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An IP address is your device's network identity — a hierarchical number that encodes both which network you're on (network portion) and which device you are (host portion), enabling routers to forward packets across the internet.

**One analogy:**

> An IP address is like a postal address: "10 Downing Street, London, SW1A 2AA." The "London, SW1A" part is the network prefix (narrows down to a neighbourhood), and "10 Downing Street" is the host part (specific building). Postal workers don't memorise every address — they route to the region, then the street, then the building. Routers work the same way with IP prefixes.

**One insight:**
IPv4 exhaustion was predicted in 1991. IANA allocated the last IPv4 /8 blocks to RIRs in 2011. The "solution" has been NAT (one public IP serving thousands of private devices) and slow IPv6 adoption (now ~40-45% of Google traffic is IPv6). Understanding private vs public IPs is essential for cloud networking, VPNs, and Kubernetes networking.

---

### 🔩 First Principles Explanation

**IPV4 ADDRESS STRUCTURE:**

```
192   .   168   .   1     .   100
11000000 10101000 00000001 01100100
│                              │
└── 32 bits total ─────────────┘

With /24 subnet mask (255.255.255.0):
Network:  192.168.1.0    (first 24 bits)
Host:     .100           (last 8 bits)
Range:    192.168.1.1 - 192.168.1.254
Broadcast: 192.168.1.255
```

**PRIVATE ADDRESS RANGES (RFC 1918):**

```
10.0.0.0/8      → 10.0.0.0   - 10.255.255.255   (16M hosts)
172.16.0.0/12   → 172.16.0.0 - 172.31.255.255   (1M hosts)
192.168.0.0/16  → 192.168.0.0 - 192.168.255.255  (65K hosts)
```

**SPECIAL ADDRESSES:**

```
127.0.0.1    → Loopback (localhost) — never leaves the host
0.0.0.0      → Unspecified / "any interface" (in bind calls)
255.255.255.255 → Limited broadcast (this subnet)
169.254.x.x  → APIPA (Automatic Private IP Addressing — no DHCP)
```

**IPV6 STRUCTURE:**

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
└────────┘ 128 bits, 8 groups of 16 bits each

Abbreviation rules:
- Leading zeros in group can be omitted: 0db8 → db8
- Consecutive all-zero groups: :: (once only)
2001:db8:85a3::8a2e:370:7334

Global unicast: 2000::/3 (publicly routable)
Link-local:    fe80::/10 (not routable beyond segment)
Loopback:      ::1
Unique local:  fc00::/7 (private, like RFC1918)
```

---

### 🧪 Thought Experiment

**SETUP:**
Why does 192.168.1.100 on your home router not conflict with 192.168.1.100 on your neighbour's router, even though they're the same address?

**ANSWER:**
RFC 1918 private addresses are not globally routable. Your home router uses NAT to translate private IPs to your one public IP before packets leave your network. Packets from 192.168.1.100 never appear on the public internet — they're always translated to your ISP-assigned public IP (e.g., 81.105.42.7) before leaving your router. Routers on the public internet never see 192.168.1.100 as a source address — so the same private range can be reused by millions of homes simultaneously without conflict.

---

### 🧠 Mental Model / Analogy

> An IPv4 address is like a 32-digit binary social security number divided into a "country code" (network prefix) and "citizen ID" (host). Routers are like post offices that only need to know how to forward to countries and regions — not to every individual citizen. NAT is like a large company with one external phone number (+44 20 7946 0000) routing calls to thousands of internal extensions. From outside, all calls appear to come from the one public number.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every device on the internet has an IP address — a number that identifies it uniquely, like a postal address for computers. IPv4 addresses look like "192.168.1.1" (four numbers separated by dots). There aren't enough IPv4 addresses for every device, so most home devices use private addresses (192.168.x.x) that are invisible outside your network.

**Level 2 — How to use it (junior developer):**
In code: bind a server to `0.0.0.0` to listen on all interfaces, `127.0.0.1` for localhost only, or a specific IP. Use `socket.gethostbyname()` for DNS resolution. Docker containers get private IPs from Docker's network bridge (172.17.0.x by default). Kubernetes pods get IPs from the pod CIDR (configurable, often 10.244.0.0/16 with Flannel). Check IPs: `ip addr show` (Linux) or `ipconfig` (Windows).

**Level 3 — How it works (mid-level engineer):**
IPv4 address allocation: originally class-based (A/B/C), replaced by CIDR (Classless Inter-Domain Routing) in 1993. IANA → RIRs (ARIN, RIPE, APNIC) → ISPs → customers. Private IP blocks are never assigned to public internet-facing hosts. Anycast: the same IP announced by multiple routers (BGP); packets routed to nearest instance — used by CDNs (Cloudflare: 1.1.1.1 is anycast), DNS root servers, and Google's 8.8.8.8. IPv6 adoption: dual-stack (host has both IPv4 and IPv6), Happy Eyeballs (RFC 6555 — browser tries IPv6 and IPv4 simultaneously, uses whichever connects first).

**Level 4 — Why it was designed this way (senior/staff):**
IPv4's 32-bit design (1981) assumed the internet would never grow beyond a research network. The class-based A/B/C system wastefully allocated /8s (16M addresses) to individual universities and companies. CIDR reclaimed some space by subdividing blocks. The NAT "solution" violates the internet's original end-to-end principle: every host should be directly addressable. NAT creates asymmetry (inbound connections require port forwarding), breaks protocols that assume end-to-end connectivity (IPsec, SIP), and shifts state to the network layer. IPv6 restores end-to-end addressing but requires dual-stack or translation during the 20+ year transition period. This transition has enormous engineering cost, explaining why IPv6 adoption is still only ~45% after 25+ years.

---

### ⚙️ How It Works (Mechanism)

```bash
# View IP addresses on all interfaces
ip addr show
# OR: ip a

# Check public IP
curl -s ifconfig.me
# OR: curl -s api.ipify.org

# Check routing table
ip route show
# Default route: default via 192.168.1.1 dev eth0

# Check IPv6 address
ip -6 addr show

# Test IPv4 vs IPv6 connectivity
ping 8.8.8.8         # IPv4
ping6 2001:4860:4860::8888  # Google DNS IPv6

# Check if interface is up with an IP
ip addr show dev eth0

# Assign IP manually (temporary)
ip addr add 192.168.1.200/24 dev eth0

# Check ARP (IP → MAC resolution on local network)
arp -n
# OR: ip neigh show
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  Packet journey: private IP → public internet  │
└────────────────────────────────────────────────┘

 Your laptop (192.168.1.100):
   GET https://google.com
   → IP packet: src=192.168.1.100, dst=142.250.x.x

 Home router (192.168.1.1 private, 81.105.42.7 public):
   NAT: src=192.168.1.100 → 81.105.42.7 (rewrite src)
   → IP packet: src=81.105.42.7, dst=142.250.x.x

 ISP router:
   Route to 142.250.0.0/16 (Google AS)

 Google (142.250.x.x):
   Receives: src=81.105.42.7 (your public IP)
   Response: src=142.250.x.x, dst=81.105.42.7

 Home router:
   NAT reverse: dst=81.105.42.7 → 192.168.1.100 (restore dst)
   → Your laptop receives response
```

---

### 💻 Code Example

```python
import socket
import ipaddress

def classify_ip(ip_str: str) -> dict:
    """Classify an IP address."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return {"error": "Invalid IP address"}

    return {
        "address": str(ip),
        "version": ip.version,
        "is_private": ip.is_private,
        "is_loopback": ip.is_loopback,
        "is_global": ip.is_global,
        "is_link_local": ip.is_link_local,
        "is_multicast": ip.is_multicast,
    }

# Examples
for addr in ["192.168.1.1", "8.8.8.8", "10.0.0.1",
             "127.0.0.1", "::1", "2001:db8::1",
             "fe80::1", "169.254.1.1"]:
    result = classify_ip(addr)
    print(f"{addr:20s}: {result}")

# Check if two IPs are on the same subnet
def same_subnet(ip1: str, ip2: str, prefix: int) -> bool:
    net = ipaddress.ip_network(f"{ip1}/{prefix}", strict=False)
    return ipaddress.ip_address(ip2) in net

print(same_subnet("192.168.1.5", "192.168.1.200", 24))  # True
print(same_subnet("192.168.1.5", "192.168.2.200", 24))  # False
```

---

### ⚖️ Comparison Table

| Feature        | IPv4           | IPv6                  |
| -------------- | -------------- | --------------------- |
| Address size   | 32-bit         | 128-bit               |
| Address space  | ~4.3 billion   | ~3.4 × 10^38          |
| Notation       | 192.168.1.1    | 2001:db8::1           |
| Private ranges | RFC 1918       | fc00::/7 (ULA)        |
| NAT required   | Often          | No (enough addresses) |
| Header size    | 20 bytes (min) | 40 bytes (fixed)      |
| Configuration  | Manual / DHCP  | SLAAC / DHCPv6        |

---

### ⚠️ Common Misconceptions

| Misconception                     | Reality                                                                                                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 192.168.1.1 is always the gateway | 192.168.1.1 is a common convention, not a standard. Any IP on the subnet can be the gateway.                                                            |
| 0.0.0.0 means "no address"        | In socket `bind()`, 0.0.0.0 means "all interfaces." In routing, it means the default route.                                                             |
| IPv6 automatically replaces IPv4  | IPv4 and IPv6 coexist via dual-stack. IPv6-only hosts need NAT64 to reach IPv4-only servers.                                                            |
| Private IPs are "secure"          | Private IPs are not routable on the public internet, but that's not the same as security — traffic on private networks is still unencrypted by default. |

---

### 🚨 Failure Modes & Diagnosis

**169.254.x.x Address — No DHCP Response**

**Symptom:**
Device gets a 169.254.x.x address. Cannot reach internet or other hosts.

**Root Cause:**
DHCP server unreachable — device used APIPA (Automatic Private IP Addressing) as fallback. Network cable unplugged, DHCP server down, or VLAN misconfiguration.

```bash
# Check for APIPA address
ip addr show | grep 169.254

# Manually request DHCP lease
dhclient eth0

# Check DHCP server reachability
journalctl -u NetworkManager | grep DHCP
```

---

### 🔗 Related Keywords

**Builds On This:**

- `Subnet & CIDR` — dividing IP address space into networks
- `NAT` — how private IPs access the public internet
- `DNS` — mapping hostnames to IP addresses
- `ARP` — resolving IP addresses to MAC addresses on local networks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ IPv4 PRIVATE  │ 10.0.0.0/8, 172.16.0.0/12,              │
│               │ 192.168.0.0/16                           │
├───────────────┼──────────────────────────────────────────┤
│ LOOPBACK      │ 127.0.0.1 (IPv4), ::1 (IPv6)             │
├───────────────┼──────────────────────────────────────────┤
│ ANY INTERFACE │ 0.0.0.0 (IPv4), :: (IPv6)                │
├───────────────┼──────────────────────────────────────────┤
│ CHECK         │ ip addr show / ip -6 addr show           │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Hierarchical label: network prefix +    │
│               │ host ID; enables global routing"         │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Subnet/CIDR → NAT → BGP routing          │
└───────────────┴──────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes cluster uses pod CIDR 10.244.0.0/16, service CIDR 10.96.0.0/12, and node IPs from 192.168.100.0/24. A pod at 10.244.1.5 makes a request to a Service at 10.96.0.10. Trace the complete path: (a) how kube-proxy or eBPF translates the service IP to a pod IP, (b) how the CNI plugin routes between pod CIDRs across nodes, (c) when a pod's traffic leaves the cluster to reach the public internet, what NAT translation occurs and at which component, and (d) why pod-to-pod communication doesn't need NAT but pod-to-internet does.

**Q2.** Explain IPv4 exhaustion and the engineering trade-offs of each "solution": (a) CIDR (eliminated class-based allocation waste), (b) RFC 1918 private addressing + NAT (enables millions of devices per public IP, but breaks end-to-end principle), (c) IPv6 (solves exhaustion but requires full protocol transition), (d) Carrier-Grade NAT / NAT444 (ISP-level NAT stacking — two NAT layers between device and internet; what protocols break?), and (e) why the transition to IPv6 after 25 years of effort is still only ~45% complete.
