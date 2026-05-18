---
id: NET-014
title: "Packet Structure"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-010, NET-007
used_by: NET-020, NET-021, NET-059
related: NET-009, NET-010, NET-020, NET-007
tags:
  - networking
  - foundational
  - protocol
  - packet-analysis
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/net/packet-structure/
---

**⚡ TL;DR** - A packet is a nested set of headers: Ethernet
frame wrapping an IP packet wrapping a TCP segment wrapping
the application data. Each header belongs to one OSI layer
and adds addressing and control information for that layer's
protocol.

| #014 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, Port Number, OSI Model (Seven Layers) | |
| **Used by:** | TCP, UDP, MTU Fragmentation and PMTUD | |
| **Related:** | IP Address, Port Number, TCP, OSI Model (Seven Layers) | |

---

### 🔥 The Problem This Solves

Without understanding packet structure, engineers cannot
read Wireshark/tcpdump output, cannot understand MTU limits,
cannot diagnose fragmentation, and cannot understand why
protocols have overhead. Packet structure is the concrete
reality behind the abstract OSI layer model.

---

### 📘 Textbook Definition

A **network packet** is a formatted unit of data carried
by a packet-switched network. In practice, a packet is a
nested structure of protocol headers (one per OSI layer)
plus a payload. The typical structure for an HTTPS request
on Ethernet is: Ethernet frame header (14 bytes) containing
an IPv4 header (20 bytes minimum) containing a TCP header
(20 bytes minimum) containing a TLS record header (5 bytes)
containing HTTP data. This nesting is called
**encapsulation**: each layer's PDU is the payload of the
layer below it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A packet is like a nested set of envelopes: application
data inside TCP inside IP inside Ethernet, each envelope
adding its own addressing label.

**One analogy:**

> Sending a certified letter internationally:
> - Outer envelope (Ethernet): has local delivery addresses
>   (MAC). Gets replaced at each hop (like a relay carrier).
> - Inner envelope (IP): has the global destination address.
>   Never replaced. Travels intact.
> - Inner inner envelope (TCP): has the department number
>   (port). Delivery tracking/signature required.
> - Letter contents (Application): what you actually wrote.

**One insight:**
Protocol overhead is unavoidable. An HTTP/1.1 response of
1 byte still requires 14 (Ethernet) + 20 (IP) + 20 (TCP)
+ ~20 (TLS) + ~200 (HTTP headers) = ~274 bytes of overhead.
This is why HTTP/2 header compression, binary framing, and
multiplexing exist - they reduce overhead per request.

---

### 🔩 First Principles Explanation

**Complete packet structure (HTTPS over Ethernet):**

```
┌──────────────────────────────────────────────────────────┐
│  Ethernet Frame (1518 bytes maximum, 64 bytes minimum)   │
├──────────────────────────────────────────────────────────┤
│  Ethernet Header (14 bytes)                              │
│  ├─ Destination MAC: 6 bytes (next hop's NIC)            │
│  ├─ Source MAC: 6 bytes (sender's NIC)                   │
│  └─ EtherType: 2 bytes (0x0800=IPv4, 0x86DD=IPv6)       │
│                                                          │
│  ┌── IPv4 Header (20 bytes minimum) ──────────────────┐ │
│  │  Version: 4 bits (value: 4 for IPv4)               │ │
│  │  IHL: 4 bits (header length in 32-bit words)       │ │
│  │  DSCP/ECN: 8 bits (QoS marking)                   │ │
│  │  Total Length: 16 bits (header + payload)          │ │
│  │  Identification: 16 bits (fragmentation ID)        │ │
│  │  Flags/Offset: 16 bits (DF, MF, fragment offset)  │ │
│  │  TTL: 8 bits (decremented each hop, drop at 0)    │ │
│  │  Protocol: 8 bits (6=TCP, 17=UDP, 1=ICMP)         │ │
│  │  Header Checksum: 16 bits                         │ │
│  │  Source IP: 32 bits                               │ │
│  │  Destination IP: 32 bits                          │ │
│  │                                                   │ │
│  │  ┌── TCP Header (20 bytes minimum) ─────────────┐ │ │
│  │  │  Source Port: 16 bits                        │ │ │
│  │  │  Destination Port: 16 bits                   │ │ │
│  │  │  Sequence Number: 32 bits                    │ │ │
│  │  │  Acknowledgment Number: 32 bits              │ │ │
│  │  │  Data Offset: 4 bits (header length)         │ │ │
│  │  │  Flags: 6 bits (SYN ACK FIN RST PSH URG)    │ │ │
│  │  │  Window Size: 16 bits (receive window)       │ │ │
│  │  │  Checksum: 16 bits                           │ │ │
│  │  │  Urgent Pointer: 16 bits                     │ │ │
│  │  │                                              │ │ │
│  │  │  ┌── Application Data ──────────────────┐   │ │ │
│  │  │  │  TLS Record Header: 5 bytes          │   │ │ │
│  │  │  │  HTTP/2 Frame Header: 9 bytes        │   │ │ │
│  │  │  │  HTTP Headers + Body: variable       │   │ │ │
│  │  │  └──────────────────────────────────────┘   │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────┘ │
│  Ethernet FCS (Frame Check Sequence): 4 bytes           │
└──────────────────────────────────────────────────────────┘
```

**Header size summary:**

| Header | Min Size | Key Fields |
|---|---|---|
| Ethernet | 14 bytes | Src MAC, Dst MAC, EtherType |
| IPv4 | 20 bytes | Src IP, Dst IP, TTL, Protocol |
| IPv6 | 40 bytes fixed | Src IP, Dst IP, Hop Limit |
| TCP | 20 bytes | Src port, Dst port, Seq, Ack, Flags, Window |
| UDP | 8 bytes | Src port, Dst port, Length |
| ICMP | 8 bytes | Type, Code, Checksum |
| TLS record | 5 bytes | Content type, Version, Length |

---

### 🧪 Thought Experiment

**SETUP:**
MTU (Maximum Transmission Unit) on Ethernet is 1500 bytes.
This means the IP packet payload can be at most 1500 bytes.
IP header = 20 bytes. TCP header = 20 bytes.
Maximum TCP payload (MSS) = 1500 - 20 - 20 = 1460 bytes.
This is why TCP's MSS (Maximum Segment Size) is typically
1460 bytes.

**FOLLOW-UP:**
Your VPN adds an outer IP header (20 bytes) + UDP header
(8 bytes) + VPN overhead (varies, ~50 bytes total).
Your effective MTU drops from 1500 to ~1500 - 50 = 1450.
TCP MSS over VPN = 1450 - 20 - 20 = 1410 bytes.
If the VPN doesn't perform MSS clamping, TCP segments of
1460 bytes will be fragmented by the VPN, adding overhead
and potentially causing path MTU discovery (PMTUD) issues.

**THE INSIGHT:**
Every tunneling or encapsulation protocol reduces the
effective payload size. Docker containers, VPNs, IPsec
tunnels, VXLAN overlays, GRE tunnels - each adds headers
that reduce the usable MTU.

---

### 🧠 Mental Model / Analogy

> A packet is like a Russian nesting doll (Matryoshka):
> - The outermost doll is the Ethernet frame - it has local
>   delivery information (MAC) and is replaced at each hop.
> - Inside is the IP doll - it has the global address and
>   travels intact.
> - Inside IP is the TCP doll - it has the port/sequence
>   number and is understood only by sender and receiver.
> - Inside TCP is the TLS doll - encrypted, only the
>   receiver can open it.
> - Innermost is the actual application data - the real
>   content. All outer dolls exist only to deliver this.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A packet is data (like a web page chunk) wrapped in
multiple layers of addressing information so routers know
where to send it and processes know what to do with it.

**Level 2 - How to use it (junior developer):**
Use Wireshark or `tcpdump -v` to see packets. Each column
maps to a field in a header. "Packet capture" shows you
the actual bytes on the wire. MTU limits mean large data
is split into multiple packets automatically - you don't
need to manage this, but you need to know it happens.

**Level 3 - How it works (mid-level engineer):**
The IP TTL field prevents packets from circling forever:
each router decrements TTL by 1. When TTL reaches 0,
the router drops the packet and sends ICMP "Time Exceeded"
back to the sender. This is exactly how `traceroute`
works: send packets with TTL=1 (first router responds),
TTL=2 (second router responds), etc., building a map
of the path.

**Level 4 - Why it was designed this way (senior/staff):**
Variable-length packets (rather than fixed-size cells like
ATM) allow the system to adapt payload size to data needs.
A 1-byte TCP ACK doesn't need a 1500-byte packet. A 1400-byte
download chunk fills the MTU. ATM (fixed 53-byte cells) was
the alternative: predictable, low jitter, but 10-byte
overhead per 48-byte payload (17% overhead!) killed its
efficiency for data. IP's variable-length packets won because
they waste less bandwidth on overhead for typical internet
traffic.

**Level 5 - Mastery (distinguished engineer):**
The IPv4 header checksum is recomputed at every router (since
TTL changes). This adds measurable CPU overhead at high
packet rates. IPv6 removed the header checksum entirely,
delegating error detection to L2 (Ethernet FCS) and L4
(TCP/UDP checksum). This was a deliberate trade-off: IPv6
headers are more efficient for router processing, trusting
that the link layer and transport layer provide sufficient
error detection. IPv6 routers process packets faster than
IPv4 routers per packet.

---

### ⚙️ How It Works (Mechanism)

**Reading packets with tcpdump:**

```bash
# Capture packets on eth0, show headers verbosely
sudo tcpdump -i eth0 -v -n -c 10

# Show full hex dump of each packet
sudo tcpdump -i eth0 -XX -n -c 5

# Filter by destination port 443 (HTTPS)
sudo tcpdump -i eth0 -v port 443 -c 10

# Capture to file for Wireshark analysis
sudo tcpdump -i eth0 -w /tmp/capture.pcap
# Open capture.pcap in Wireshark for GUI analysis

# Example output (-v):
# 10:23:45.123456 IP (tos 0x0, ttl 64, id 12345,
#   offset 0, flags [DF], proto TCP (6),
#   length 80)
#   192.168.1.100.52341 > 142.250.80.78.443:
#   Flags [S], seq 12345678, win 65535
#   options [mss 1460,sackOK,TS val 12345]
```

**Key packet fields to recognize:**

```
IP packet:
  TTL: starts at 64 (Linux) or 128 (Windows)
       after 4 hops → TTL=60
  DF flag: "Don't Fragment" - if set, router must
           drop and send ICMP error if packet too large
  Protocol: 6=TCP, 17=UDP, 1=ICMP

TCP segment:
  Flags: [S]=SYN, [SA]=SYN+ACK, [A]=ACK,
         [F]=FIN, [R]=RST, [P]=PSH
  seq: sequence number for ordering
  ack: next byte expected from other side
  win: receive window (flow control)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Packet processing at each hop:**

```
┌──────────────────────────────────────────────────┐
│  What each network device processes              │
├───────────────────┬──────────────────────────────┤
│  Device           │  Headers read/modified       │
├───────────────────┼──────────────────────────────┤
│  NIC              │  Ethernet FCS (checksum)     │
│  Switch (L2)      │  Ethernet src/dst MAC        │
│  Router (L3)      │  IP src/dst + TTL decrement  │
│                   │  New Ethernet header added   │
│  Firewall (L4)    │  IP + TCP/UDP port + flags   │
│  Load Balancer    │  IP + TCP + HTTP (L7 LB)     │
│  Application      │  TCP + TLS + HTTP headers    │
└───────────────────┴──────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
At 100Gbps line rate, every packet must be processed in
~10 nanoseconds (100Gbps = 14.8 million 1500-byte packets/sec
= 67ns per packet). Hardware ASICs handle L2-L3 at line
rate. Software (Linux kernel netfilter) processes ~1-10
million packets/sec on modern CPUs. High-performance
systems use DPDK (Data Plane Development Kit) to bypass
the kernel entirely, processing packets directly from NIC
memory in user space.

---

### ⚖️ Comparison Table

| Protocol | Header Size | Key Fields | When Used |
|---|---|---|---|
| IPv4 | 20-60 bytes | TTL, src/dst IP, protocol, flags | Most internet traffic |
| IPv6 | 40 bytes fixed | Hop limit, src/dst IP (128-bit) | Increasingly common |
| TCP | 20-60 bytes | Ports, seq/ack, flags, window | Reliable streams |
| UDP | 8 bytes | Ports, length, checksum | Low-overhead datagrams |
| ICMP | 8 bytes | Type, code | Ping, traceroute, errors |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Packet == frame | A frame is the L2 PDU (Ethernet frame). A packet is the L3 PDU (IP packet). The IP packet is carried in the Ethernet frame's payload. They are different things at different layers. |
| MTU is 1500 bytes | 1500 bytes is Ethernet's standard MTU. Jumbo frames (up to 9000 bytes) are used in datacenters. VXLAN, IPIP tunnels reduce effective MTU. Docker default MTU is 1500 but VPN + Docker can lead to sub-1400 effective MTU for applications. |
| TTL protects against infinite loops | TTL only prevents loop-induced infinite circulation. It does NOT prevent routing loops from forming. BGP route loops can cause packets to drop immediately (TTL hits 0 at the loop), which is actually harder to diagnose than an obvious forwarding problem. |

---

### 🚨 Failure Modes & Diagnosis

**ICMP Fragmentation Required (PMTUD Black Hole)**

**Symptom:** SSH connections work for login but hang after
running any command that produces output. Large HTTP
responses fail. Small packets work; large packets fail.

**Root Cause:** A firewall on the path blocks ICMP "Fragmentation
Needed" messages. When a packet is too large for an
intermediate link, the router sends ICMP back to the sender
saying "reduce to X bytes." If ICMP is blocked, the sender
never learns and keeps sending large packets that get dropped.

**Diagnostic Command / Tool:**
```bash
# Test if PMTUD works
ping -M do -s 1400 target_ip
# -M do = don't fragment, -s 1400 = 1400 byte payload
# If this works: MTU >= 1428 bytes (1400 + 28 overhead)
# If this fails: PMTUD may be broken

# Try progressively smaller sizes
ping -M do -s 1200 target_ip
ping -M do -s 1000 target_ip
# Find the maximum working size = effective MTU - 28

# Check if ICMP is being blocked by a firewall
# (indirectly: if large packets fail, ICMP unreachable
# may be blocked)
```

**Fix:** Allow ICMP type 3 (Destination Unreachable) and
type 4 (Fragmentation Needed) through all firewalls on
the path. Or configure TCP MSS clamping on routers:
`ip tcp adjust-mss 1452` (Cisco syntax).

**Prevention:** Never block ICMP type 3/4. Only block
ICMP echo (ping) if security policy requires it.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `IP Address` - the L3 addressing in IP headers
- `Port Number` - the L4 addressing in TCP/UDP headers
- `OSI Model (Seven Layers)` - the conceptual framework
  that packet headers implement

**Builds On This (learn these next):**
- `TCP (Transmission Control Protocol)` - deep dive into
  TCP header fields (seq/ack/window/flags)
- `UDP (User Datagram Protocol)` - simpler 8-byte header
- `MTU Fragmentation and PMTUD` - what happens when packets
  exceed link MTU

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRUCTURE    │ ETH(14) + IP(20) + TCP(20) + data         │
│              │ = 54 bytes overhead minimum (TCP/IPv4)    │
├──────────────┼───────────────────────────────────────────┤
│ MTU          │ Ethernet: 1500 bytes total IP packet size │
│              │ Max TCP payload (MSS): 1460 bytes         │
├──────────────┼───────────────────────────────────────────┤
│ KEY FIELDS   │ IP: TTL, src/dst IP, Protocol, DF flag    │
│              │ TCP: ports, seq, ack, flags, window       │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ tcpdump -v (headers), -XX (hex dump)     │
│              │ Wireshark: GUI packet dissector            │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Blocking all ICMP: breaks PMTUD          │
│              │ (large packet failures, SSH hangs)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A packet is nested envelopes.            │
│              │  ETH for local, IP for global,            │
│              │  TCP for ports."                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TCP → TCP Three-Way Handshake →           │
│              │ MTU Fragmentation and PMTUD               │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Packet structure: Ethernet(14) + IP(20) + TCP(20) + data.
   Ethernet MTU=1500, so max TCP payload = 1500-40=1460 bytes.
2. IP TTL: starts at 64 (Linux), decremented at each hop.
   `traceroute` exploits TTL=1,2,3... to map the path.
3. NEVER block ICMP type 3/4 (Fragmentation Needed).
   Blocking it causes mysterious large-packet failures.

**Interview one-liner:**
"A packet for HTTPS is: 14-byte Ethernet header (src/dst
MAC), 20-byte IPv4 header (src/dst IP, TTL, protocol=6),
20-byte TCP header (src/dst port, seq/ack numbers, flags,
window size), then TLS record + HTTP data. Maximum TCP
payload on Ethernet is 1460 bytes (1500 MTU - 40 TCP+IP
headers). IP TTL starts at 64 and decrements at each router,
which is how traceroute works."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Structured headers with defined field boundaries enable
independent processing at each layer. Any network device
(switch, router, firewall, load balancer) can process only
the headers it understands and pass the rest through
unchanged. This layered processing principle appears in:
HTTP middleware (each middleware reads headers, passes body),
gRPC metadata (headers processed separately from body),
Kafka message envelope (headers vs payload).

---

### 💡 The Surprising Truth

TCP does NOT add a "message length" field. There is no
boundary between messages in the TCP stream. A TCP segment
says only "these bytes have sequence numbers X to Y." If
you send `"Hello"` and `"World"` as two write() calls, they
might arrive as `"Hel"` and `"loWor"` and `"ld"` in three
TCP segments. Application protocols (HTTP, Redis RESP,
gRPC, length-prefixed protocols) must implement their own
message framing. The TCP header's `PSH` flag is advisory
("push this to the application"), but it is not a message
boundary marker. Most developers assume TCP is message-
oriented. It is not - it is byte-stream-oriented.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the nested structure of a packet from
   application data to bits on wire, naming each header
   and its key fields.
2. **DEBUG** an MTU issue using `ping -M do -s SIZE` to
   find the effective MTU on a path.
3. **DECIDE** what `tcpdump` filter expression to use for
   a given debugging scenario (by port, by IP, by TCP flag).
4. **BUILD** a traceroute explanation from packet TTL
   mechanics: why TTL=1 gets a response from the first hop.
5. **EXTEND** the packet structure to explain how VPN
   encapsulation reduces effective MTU and what problems
   this causes.

---

### 🧠 Think About This Before We Continue

**Q1.** Wireshark shows a packet with IP TTL=1 being sent
from a host. What will happen to this packet? Why would an
application intentionally send packets with TTL=1? Name
two use cases where TTL=1 is correct and expected behavior.

*Hint: TTL=1 is dropped at the first router with an ICMP
response. When is that useful? Think about discovery
protocols and traceroute.*

**Q2.** A firewall rule says "allow TCP port 443 inbound."
The firewall processes packets at L4 (TCP). Does it need to
read the Ethernet header? The IP header? The TCP header?
Which headers does a stateful firewall track for each
connection, and why is this different from a stateless
packet filter?

*Hint: Stateful firewall tracks connection state (SYN seen,
established, FIN seen) - requires remembering previous
packets. Stateless filters each packet independently.*

**Q3.** [Hands-On] Run `sudo tcpdump -i eth0 -XX -n -c 1
"tcp and port 443"` while initiating an HTTPS connection.
Look at the raw hex output. Can you identify:
- Bytes 0-5: destination MAC
- Bytes 6-11: source MAC
- Bytes 12-13: EtherType (0x0800 = IPv4)
- Bytes 14+: start of IPv4 header (first nibble should be 4)
- Bytes 26-29: source IP (4 bytes)
- Bytes 30-33: destination IP (4 bytes)
Compare the IP addresses you see in hex to the `dig` output
for the site you connected to.