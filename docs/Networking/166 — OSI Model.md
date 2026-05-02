---
layout: default
title: "OSI Model"
parent: "Networking"
nav_order: 166
permalink: /networking/osi-model/
number: "0166"
category: Networking
difficulty: ★☆☆
depends_on: []
used_by: Networking, TCP/IP Stack, HTTP & APIs
related: TCP/IP Stack, TCP, UDP, DNS
tags:
  - networking
  - fundamentals
  - protocols
---

# 166 — OSI Model

⚡ TL;DR — The OSI model is a 7-layer conceptual framework that divides network communication into discrete responsibilities — from physical bit transmission (Layer 1) to application protocols (Layer 7) — enabling interoperability by standardising what each layer does and how layers communicate.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Different hardware vendors, OS vendors, and protocol designers each implement networking in completely proprietary ways. IBM's SNA protocol stack is incompatible with DEC's DECnet. A cable modem from Vendor A doesn't work with routing software from Vendor B. Every networking product requires full vertical integration — one vendor's hardware, cables, switches, protocols, and applications. Innovation in one part requires replacing the entire stack.

**THE BREAKING POINT:**
The internet of the 1970s-80s consisted of incompatible islands. ARPANET, X.25, and IBM SNA networks couldn't interconnect. Each network was a custom solution. Connecting them required gateways that understood every proprietary detail of both networks.

**THE INVENTION MOMENT:**
ISO developed the OSI model (1984) as a universal reference architecture. By defining 7 layers with clear responsibilities and standardised interfaces between layers, any vendor can implement one layer independently. An Ethernet NIC (Layer 2) works with any IP stack (Layer 3). TCP (Layer 4) runs on top of any IP implementation. HTTP (Layer 7) runs over any TCP implementation. This is interoperability through layering.

---

### 📘 Textbook Definition

The **OSI (Open Systems Interconnection) model** is a conceptual framework developed by ISO (International Organization for Standardization) that divides the functions of a network communication system into seven distinct layers. Each layer provides services to the layer above and consumes services from the layer below. The model defines responsibilities at each layer, enabling vendors to build compatible products at each layer independently.

| Layer | Name         | Protocol Data Unit | Examples                         |
| ----- | ------------ | ------------------ | -------------------------------- |
| 7     | Application  | Data               | HTTP, SMTP, DNS, FTP             |
| 6     | Presentation | Data               | TLS/SSL, JSON encoding, JPEG     |
| 5     | Session      | Data               | RPC, NetBIOS, session management |
| 4     | Transport    | Segment            | TCP, UDP, SCTP                   |
| 3     | Network      | Packet             | IP, ICMP, BGP, OSPF              |
| 2     | Data Link    | Frame              | Ethernet, Wi-Fi (802.11), ARP    |
| 1     | Physical     | Bit                | Cable, NIC, repeater, hub        |

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The OSI model cuts network communication into 7 layers, each with a specific job — so each can be built, replaced, or debugged independently.

**One analogy:**

> Sending data over a network is like sending a parcel internationally. Layer 7: you write the letter. Layer 6: you translate it to the recipient's language. Layer 5: you mark it as part of a conversation. Layer 4: you split it across envelopes with sequence numbers. Layer 3: you address the outer envelope with city/country. Layer 2: you hand it to the local post office with a local route. Layer 1: the physical vehicle (truck, plane, conveyor belt) carries the envelope. Each step is handled by a different service. Replacing air freight with trucks doesn't require reprinting the letter.

**One insight:**
The OSI model is a reference model — real-world protocols don't map cleanly to it. TCP/IP collapses layers 5-7 into one "application layer." But the mental model of "isolate each layer's responsibility" is invaluable for debugging: "Is this a Layer 2 problem (MAC address)? Layer 3 (routing)? Layer 4 (port blocked)?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Encapsulation**: each layer adds its own header (and sometimes trailer) to the data from the layer above; this is called a PDU (Protocol Data Unit).
2. **Decapsulation**: on the receiving end, each layer strips its header and passes the remaining data up.
3. **Transparency**: a layer only knows about the layers immediately above and below it; it doesn't care about the implementation of other layers.
4. **Peer communication**: logically, Layer N on the sender communicates with Layer N on the receiver using the protocol defined for that layer.

**LAYER RESPONSIBILITIES:**

**Layer 1 — Physical:**
Converts bits to signals (electrical, light, radio). Defines cable types, pin layouts, voltages, frequencies. No addressing. Examples: Ethernet cable (Cat5e), fibre optic, Wi-Fi radio, hubs (repeat everything).

**Layer 2 — Data Link:**
Frames (packaging bits for a specific network segment). MAC addressing. Error detection (CRC). Access to shared media (CSMA/CD for Ethernet). Examples: Ethernet switches, Wi-Fi access points (for the local segment). ARP resolves IP to MAC at this layer.

**Layer 3 — Network:**
Logical addressing (IP addresses). Routing between networks. Fragmentation. Examples: routers, IP protocol, ICMP, BGP, OSPF.

**Layer 4 — Transport:**
End-to-end communication. Port numbers (identify applications). Segmentation/reassembly. Connection management. Examples: TCP (reliable, ordered), UDP (unreliable, fast).

**Layer 5 — Session:**
Managing sessions between applications. Synchronisation checkpoints. Examples: rarely implemented explicitly in modern protocols; TLS handshake, RPC session management.

**Layer 6 — Presentation:**
Data format translation. Encoding/decoding, encryption/decryption, compression. Examples: TLS encryption, character encoding (UTF-8), data serialisation (JSON, protobuf).

**Layer 7 — Application:**
User-facing protocols. Examples: HTTP, HTTPS, SMTP, DNS, FTP, SSH, DHCP.

**THE TRADE-OFFS:**
**Gain:** Interoperability; independent innovation at each layer; modular debugging ("which layer is the problem?").
**Cost:** Added overhead per layer (headers); strict layering can be inefficient (TCP/IP combines layers 5-7 for this reason); the model is theoretical — real implementations cross layer boundaries (ARP bridges layer 2 and 3).

---

### 🧪 Thought Experiment

**SETUP:**
You type `curl https://api.example.com/data` on your laptop. What happens at each OSI layer?

**Layer 7 (Application):**
curl constructs an HTTP GET request: `GET /data HTTP/1.1\nHost: api.example.com\n...`

**Layer 6 (Presentation):**
TLS negotiates encryption, wraps the HTTP request in an encrypted record.

**Layer 5 (Session):**
TLS session is established; manages the session lifecycle.

**Layer 4 (Transport):**
TCP wraps in segments: source port 54321, dest port 443. TCP handles ordering, retransmission. Adds TCP header.

**Layer 3 (Network):**
IP adds source IP (your laptop) and destination IP (resolved from api.example.com via DNS). Fragmented if needed. Routing decisions made here.

**Layer 2 (Data Link):**
Ethernet wraps in a frame: source MAC (your laptop's NIC), destination MAC (your router's interface). CRC added.

**Layer 1 (Physical):**
Bits transmitted as electrical signals over Cat5e cable or as radio waves over Wi-Fi.

**THE INSIGHT:**
Each layer is independent. You can upgrade from HTTP/1.1 to HTTP/2 (Layer 7) without changing TCP, IP, or Ethernet. You can switch from Ethernet to Wi-Fi (Layer 2) without changing HTTP, TLS, or IP. This is the power of layered design.

---

### 🧠 Mental Model / Analogy

> The OSI model is like the manufacturing supply chain for a finished product. Layer 7: product designer specifies what the product should be. Layer 6: translator converts the design to factory specifications. Layer 5: project manager coordinates production sessions. Layer 4: logistics manager plans how to ship sub-components. Layer 3: freight coordinator determines routes between countries. Layer 2: local delivery driver handles the last mile. Layer 1: the physical trucks, planes, and rails that move boxes. Each party only interfaces with the people directly above and below them in the chain. The product designer doesn't know which airline was used; the airline doesn't know what's being shipped.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The OSI model breaks network communication into 7 steps, each with a specific job. Think of it like an assembly line — each station does one thing, passes the result to the next. This way, you can change one station (switch from cable to Wi-Fi) without redesigning the whole line.

**Level 2 — How to use it (junior developer):**
Use OSI for debugging. "Layer 1 problem": cable unplugged, NIC not getting link light. "Layer 2 problem": switch not forwarding, MAC address conflict. "Layer 3 problem": wrong IP route, firewall blocking IP. "Layer 4 problem": port blocked, TCP connection refused. "Layer 7 problem": wrong HTTP response code. When debugging, always start at Layer 1 (is the cable plugged in?) and work up.

**Level 3 — How it works (mid-level engineer):**
Encapsulation in practice: an HTTP response body gets wrapped in TLS record (Layer 6), then TCP segment (Layer 4, adds source/dest ports, sequence number, checksum), then IP packet (Layer 3, adds source/dest IP, TTL, protocol type), then Ethernet frame (Layer 2, adds source/dest MAC, EtherType, CRC). The total overhead: TCP header (20-60 bytes) + IP header (20 bytes) + Ethernet header+trailer (18 bytes) = 58-98 bytes per packet of overhead, before any data. For a 1500-byte Ethernet MTU, 58+ bytes is headers — ~4-6% overhead.

**Level 4 — Why it was designed this way (senior/staff):**
The OSI model was developed as an open standard to counter vendor lock-in. IBM's SNA, DEC's DECnet, and Xerox's XNS were competing proprietary stacks in the 1970s. ISO's response was a neutral reference model that any vendor could implement. In practice, TCP/IP (developed in parallel by ARPANET) "won" because it was simpler, already deployed, and open source (academic). The OSI model survived not as an implementation but as a conceptual vocabulary. Today, the distinction between a Layer 4 load balancer (routes based on TCP ports) and a Layer 7 load balancer (routes based on HTTP headers/URL) is purely OSI model terminology — essential for system design discussions. The model enables engineers from different backgrounds to communicate precisely about "at which layer does this decision happen?"

---

### ⚙️ How It Works (Mechanism)

**Packet anatomy:**

```
Ethernet Frame (Layer 2 wrapper):
┌─────────────────────────────────────────────────────┐
│ Dst MAC (6B) │ Src MAC (6B) │ EtherType (2B) │     │
│──────────────────────────────────────────────────── │
│                   IP Packet (Layer 3)               │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Ver│IHL│ToS│Total Len│ID│Flags│Offset│TTL│Proto │ │
│ │ Src IP (4B)          │ Dst IP (4B)             │ │
│ │─────────────────────────────────────────────────│ │
│ │             TCP Segment (Layer 4)               │ │
│ │ ┌───────────────────────────────────────────┐   │ │
│ │ │ Src Port (2B) │ Dst Port (2B)             │   │ │
│ │ │ Seq Num (4B)  │ Ack Num (4B)              │   │ │
│ │ │ Flags │ Window │ Checksum │ Urgent        │   │ │
│ │ │───────────────────────────────────────────│   │ │
│ │ │          Application Data (Layer 7)       │   │ │
│ │ │  GET /index.html HTTP/1.1\r\n...          │   │ │
│ │ └───────────────────────────────────────────┘   │ │
│ └─────────────────────────────────────────────────┘ │
│ CRC (4B) │                                          │
└─────────────────────────────────────────────────────┘
```

**Debugging by OSI layer:**

```bash
# Layer 1: Physical
# Check NIC link status
ip link show eth0
# state UP = link detected

# Layer 2: Data Link
# Check MAC address table on switch (from the switch CLI)
# From host: ARP table
arp -n
ip neigh show

# Layer 3: Network
# Check routing table
ip route show
# Reachability
ping 8.8.8.8  # ICMP (Layer 3)
traceroute 8.8.8.8  # Layer 3 path

# Layer 4: Transport
# Check port connectivity
nc -zv 8.8.8.8 443  # TCP connection test
ss -tlnp  # listening ports

# Layer 7: Application
curl -v https://api.example.com  # full HTTP trace
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
SENDER (your browser):                   RECEIVER (web server):

Layer 7: HTTP GET /page                  Layer 7: Process HTTP
     ↓ encapsulate                            ↑ decapsulate
Layer 6: TLS encrypt                     Layer 6: TLS decrypt
     ↓                                        ↑
Layer 5: Session mgmt                    Layer 5: Session mgmt
     ↓                                        ↑
Layer 4: TCP segment                     Layer 4: TCP reassemble
     ↓ add port headers                       ↑ strip port headers
Layer 3: IP packet                       Layer 3: IP routing
     ↓ add IP headers                         ↑ strip IP headers
Layer 2: Ethernet frame                  Layer 2: Ethernet
     ↓ add MAC headers                        ↑ strip MAC headers
Layer 1: Electrical/optical              Layer 1: Electrical/optical
     ─────────────── physical medium ─────────────────
                (cable, fibre, radio)
```

---

### 💻 Code Example

**Example — Inspect OSI layers with Python:**

```python
from scapy.all import *

# Build a packet from scratch using OSI layers
# Layer 3 (IP) + Layer 4 (TCP) + Layer 7 (HTTP)
packet = (
    IP(dst="93.184.216.34") /    # Layer 3: IP
    TCP(dport=80, sport=12345,   # Layer 4: TCP
        flags="S") /
    Raw(b"GET / HTTP/1.1\r\n"    # Layer 7: Application
        b"Host: example.com\r\n\r\n")
)

# Show all layers
packet.show()
# ###[ IP ]###
#   dst= 93.184.216.34
# ###[ TCP ]###
#   dport= http (80)
#   flags= S
# ###[ Raw ]###
#   load= 'GET / HTTP/1.1...'

# Capture and dissect packets
def analyse_packet(pkt):
    if pkt.haslayer(IP):
        print(f"L3 IP: {pkt[IP].src} → {pkt[IP].dst}")
    if pkt.haslayer(TCP):
        print(f"L4 TCP: port {pkt[TCP].sport} → {pkt[TCP].dport}")
    if pkt.haslayer(Raw):
        data = pkt[Raw].load[:80]
        print(f"L7 Data: {data}")

# sniff(prn=analyse_packet, count=10)
```

---

### ⚖️ Comparison Table

| OSI Layer      | TCP/IP Layer   | Protocols       | L4 LB? | L7 LB? |
| -------------- | -------------- | --------------- | ------ | ------ |
| 7 Application  | Application    | HTTP, SMTP, DNS | No     | Yes    |
| 6 Presentation | Application    | TLS, encoding   | No     | Yes    |
| 5 Session      | Application    | RPC sessions    | No     | Yes    |
| 4 Transport    | Transport      | TCP, UDP        | Yes    | Yes    |
| 3 Network      | Internet       | IP, ICMP        | No     | No     |
| 2 Data Link    | Network Access | Ethernet        | No     | No     |
| 1 Physical     | Network Access | Cable, NIC      | No     | No     |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                 |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OSI model is how the internet actually works | TCP/IP is how the internet works; OSI is a reference model. TCP/IP has 4 layers vs OSI's 7                                                              |
| Layer 4 load balancers understand HTTP       | L4 LBs see TCP ports, not HTTP content. Only L7 LBs can route by URL, headers, or cookies                                                               |
| ARP is Layer 3                               | ARP (Address Resolution Protocol) operates between Layers 2 and 3 — it maps Layer 3 addresses (IP) to Layer 2 addresses (MAC); strictly it's Layer 2    |
| TLS is Layer 7                               | TLS operates at Layer 6 (Presentation) in OSI, or between Layer 4 and 7 in practice — it encrypts above TCP but below HTTP                              |
| "Firewalls work at Layer 3"                  | Modern firewalls work at multiple layers: stateless packet filters at Layer 3/4; stateful firewalls at Layer 4; application firewalls (WAFs) at Layer 7 |

---

### 🚨 Failure Modes & Diagnosis

**"It works on my machine" — OSI-Layer Diagnosis**

**Symptom:**
Application works locally but fails when deployed. "Connection refused" errors.

**OSI-Layer Diagnostic Checklist:**

```bash
# L1: Is there physical connectivity?
ip link show  # Look for "state UP"

# L2: ARP resolution working?
ping <gateway_ip>  # If fails, check Layer 2

# L3: IP routing correct?
ip route show
ping <server_ip>  # Direct ping (ICMP = Layer 3)

# L4: Port open and listening?
nc -zv <server_ip> <port>   # TCP connect test
ss -tlnp | grep <port>       # Is port actually listening?

# L7: Application responding?
curl -v http://<server_ip>:<port>/healthz
# -v shows all HTTP headers (Layer 7 detail)
```

Most "network problems" are actually Layer 4 (firewall blocking the port) or Layer 7 (application not listening on `0.0.0.0`, only on `127.0.0.1`).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- None — OSI is a foundational model; this is the entry point for networking

**Builds On This (learn these next):**

- `TCP/IP Stack` — the actual protocol stack used by the internet, which maps roughly to OSI
- `TCP` — the transport layer protocol (Layer 4) at the heart of reliable internet communication
- `IP Addressing` — Layer 3 addressing scheme that OSI Network layer implements

**Alternatives / Comparisons:**

- `TCP/IP Model` — 4-layer practical model (Network Access, Internet, Transport, Application) actually used by the internet
- `DoD Model` — US Department of Defense network model; similar to TCP/IP model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ L7 Application  │ HTTP, SMTP, DNS — user protocols       │
│ L6 Presentation │ TLS, encoding — format/encrypt         │
│ L5 Session      │ RPC sessions — session management      │
│ L4 Transport    │ TCP, UDP — ports, reliability          │
│ L3 Network      │ IP, ICMP — routing, logical address    │
│ L2 Data Link    │ Ethernet, Wi-Fi — MAC, local delivery  │
│ L1 Physical     │ Cables, NIC — bits to signals          │
├──────────────────────────────────────────────────────────┤
│ MNEMONIC (top→bottom): "All People Seem To Need Data     │
│ Processing" (Application, Presentation, Session,         │
│ Transport, Network, Data Link, Physical)                 │
├──────────────────────────────────────────────────────────┤
│ KEY USE     │ Debug: "which layer is the problem?"       │
│             │ Design: "L4 LB vs L7 LB?"                 │
├──────────────────────────────────────────────────────────┤
│ ONE-LINER   │ "7-layer assembly line — each layer wraps  │
│             │ and passes to the next"                    │
├──────────────────────────────────────────────────────────┤
│ NEXT EXPLORE│ TCP/IP Stack → TCP → IP Addressing         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A load balancer vendor offers two products: an L4 load balancer (hardware, 100Gbps, $50,000) and an L7 load balancer (software, 10Gbps, $5,000). For each of these use cases — (a) distributing raw TCP connections for a financial trading system that requires sub-millisecond latency, (b) routing HTTP requests to different backend services based on URL path, (c) implementing SSL termination centrally — determine which product to use, explain what information each load balancer can and cannot see, and describe the trade-off between throughput and routing intelligence.

**Q2.** When a packet traverses a network from source to destination through three routers, describe precisely what changes and what stays the same in each layer's headers at each hop — specifically: does the source IP change? Does the destination IP change? Does the source MAC change? Does the destination MAC change? Does the TTL change? — and explain why this asymmetry in layer-2 vs layer-3 addressing is fundamental to how internet routing works.
