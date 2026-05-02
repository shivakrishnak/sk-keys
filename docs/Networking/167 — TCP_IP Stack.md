---
layout: default
title: "TCP/IP Stack"
parent: "Networking"
nav_order: 167
permalink: /networking/tcpip-stack/
number: "0167"
category: Networking
difficulty: ★☆☆
depends_on: OSI Model
used_by: Networking, HTTP & APIs, Distributed Systems
related: OSI Model, TCP, UDP, IP Addressing
tags:
  - networking
  - fundamentals
  - protocols
  - tcp-ip
---

# 167 — TCP/IP Stack

⚡ TL;DR — The TCP/IP stack is the practical 4-layer protocol suite that powers the internet: Network Access (Ethernet, Wi-Fi), Internet (IP routing), Transport (TCP/UDP), and Application (HTTP, DNS) — simpler than OSI, actually implemented, and the foundation of all internet communication.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every network is an island. IBM mainframes, UNIX workstations, and DEC minicomputers all use proprietary networking protocols. You can't send data from a UNIX machine to an IBM mainframe. Universities can't share research across different campus networks. International collaboration is impossible without standardising on common protocols that all machines can implement.

**THE BREAKING POINT:**
ARPANET (the early internet) connected different types of computers across different network technologies. As more universities and research institutions joined, the original NCP (Network Control Protocol) couldn't scale. A new protocol was needed that could: route packets across multiple networks (not just point-to-point), recover from partial network failures, and run on radically different hardware (satellite links, phone lines, Ethernet).

**THE INVENTION MOMENT:**
Vint Cerf and Bob Kahn designed TCP/IP in 1974 as the answer. The key innovation was the concept of a "catenet" (concatenated network) — distinct networks, each with different characteristics, connected by gateways (routers). IP handles routing between networks; TCP handles reliable end-to-end communication. The DoD adopted TCP/IP in 1982. ARPANET switched to TCP/IP on January 1, 1983 ("flag day"). This is the internet.

---

### 📘 Textbook Definition

The **TCP/IP stack** (also called the **Internet protocol suite**) is the conceptual model and set of protocols used for the internet and most private networks. It defines four layers (in the DARPA model):

| Layer | Name | Protocols | Function |
|---|---|---|---|
| 4 | Application | HTTP, SMTP, DNS, SSH, FTP | Application-level protocols |
| 3 | Transport | TCP, UDP, SCTP | End-to-end communication, port addressing |
| 2 | Internet | IP (IPv4/IPv6), ICMP, ARP | Logical addressing, routing between networks |
| 1 | Network Access | Ethernet, Wi-Fi, PPP | Physical delivery on a single network segment |

This maps loosely to OSI layers: TCP/IP Application ≈ OSI layers 5-7; Transport = layer 4; Internet = layer 3; Network Access = layers 1-2.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
TCP/IP is the actual protocol stack the internet uses: four layers that together take your HTTP request from browser to server and back.

**One analogy:**
> The TCP/IP stack is like the international postal system. Network Access layer: your local post office handles physical delivery in your neighbourhood. Internet layer: the postal routing system determines which cities and countries your package passes through (with each city potentially using different transport — truck, train, plane). Transport layer: you choose registered (TCP, with tracking and delivery confirmation) or standard (UDP, no tracking). Application layer: the content of your letter (HTTP request, email, DNS query).

**One insight:**
The Internet layer (IP) is the "thin waist" of the hourglass design. Many application protocols above, many network technologies below, but everything must pass through IP. This is why the internet can run on satellite, 5G, fibre, and copper all simultaneously — they all speak IP.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **End-to-end principle**: intelligence is at the edges (applications), not in the network core. Routers just route; they don't manage connections or guarantee delivery.
2. **Best-effort delivery**: IP makes no guarantees — packets may be lost, reordered, or duplicated. Reliability is TCP's responsibility, not IP's.
3. **Everything over IP**: any network technology can be the underlying carrier as long as it can carry IP packets.
4. **Packet switching**: data is broken into packets; each packet may take a different route; packets are reassembled at the destination.

**LAYER RESPONSIBILITIES:**

**Network Access (Layer 1 in TCP/IP):**
Physically delivers data on one network segment. Handles MAC addressing (local delivery), framing, and error detection. Ethernet, Wi-Fi, PPPoE, etc. This layer changes at each hop — a packet goes Ethernet → Wi-Fi → fibre, and each segment uses a different Network Access protocol.

**Internet (Layer 2 in TCP/IP):**
IP routing: forward packets hop-by-hop to the destination IP. Each router decrements TTL, consults routing table, forwards to next hop. IP addresses don't change end-to-end (unlike MAC addresses). ICMP: error and diagnostic messages. ARP: resolve IP to MAC for the Network Access layer.

**Transport (Layer 3 in TCP/IP):**
Multiplexing: port numbers identify applications (HTTP=80, SSH=22). TCP: adds reliability, ordering, flow control. UDP: adds only multiplexing (ports), no reliability. This is the highest layer the OS handles — everything above is user-space.

**Application (Layer 4 in TCP/IP):**
Protocols that applications directly use: HTTP, SMTP, DNS, SSH, FTP, DHCP. No OS involvement beyond providing the socket API. Each application implements its own application-layer protocol.

**THE TRADE-OFFS:**
Simplicity (4 layers vs OSI's 7) enables easier implementation. Best-effort IP enables building diverse networks but shifts reliability burden to endpoints. The end-to-end principle enables application innovation but makes some network optimisations harder (e.g., Quality of Service requires violating the pure IP model).

---

### 🧪 Thought Experiment

**SETUP:**
`curl http://93.184.216.34/` — trace the packet's journey.

**On the sender (your laptop):**
1. **Application layer**: curl creates HTTP GET request bytes.
2. **Transport layer (TCP)**: kernel wraps in TCP segment. Source port: 52341 (random). Dest port: 80. Seq: 1.
3. **Internet layer (IP)**: kernel wraps in IP packet. Source IP: 192.168.1.100 (your IP). Dest IP: 93.184.216.34.
4. **Network Access (Ethernet)**: kernel wraps in Ethernet frame. Source MAC: your NIC. Dest MAC: your router's MAC (not the server's!).

**At the first router (your home router):**
- Receives Ethernet frame, strips it (Network Access layer done).
- IP layer: checks routing table → forwards to ISP.
- New Ethernet frame: source MAC = router's WAN interface, dest MAC = next hop router's MAC.
- IP packet unchanged (same source/dest IP, TTL decremented by 1).

**This repeats at every router** until the packet arrives at 93.184.216.34's server.

**At the destination server:**
- Network Access stripped → IP stripped → TCP processed → HTTP parsed → response sent back.

**THE INSIGHT:**
IP source/destination addresses stay constant end-to-end. MAC addresses change at every hop. This is the fundamental mechanism of internet routing: IP for global routing, MAC for local delivery.

---

### 🧠 Mental Model / Analogy

> The TCP/IP stack is like logistics for shipping a package internationally. Network Access: your local courier picks up the package and takes it to the nearest hub (local Ethernet delivery). Internet layer: the routing hubs determine the route (IP routing) — London → Frankfurt → New York → LA — each hub reads the destination address and forwards to the next. Transport layer: you chose FedEx with tracking (TCP) or standard post with no tracking (UDP). Application layer: the actual contents of your package. The package address (IP) stays the same throughout; the delivery labels on each leg (MAC) change at every handoff.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The TCP/IP stack is the set of rules that lets computers talk to each other over the internet. Four layers work together: the application you use (email, browser), the transport (reliable or best-effort delivery), the routing (finding the path), and the physical network (cables, Wi-Fi). Every device on the internet speaks these same rules, which is why a phone in Japan can load a website hosted in Germany.

**Level 2 — How to use it (junior developer):**
As a developer, you mostly live in the Application layer (HTTP, WebSockets). You use the Transport layer via sockets: `socket(AF_INET, SOCK_STREAM, 0)` for TCP, `SOCK_DGRAM` for UDP. The OS handles Internet and Network Access layers automatically. Useful mental model for debugging: if `ping IP` works but `curl URL` doesn't, the problem is Layer 3 or Layer 4 (routing is fine, but maybe port 80 is blocked). If `curl http://IP` works but `curl http://hostname` doesn't, the problem is DNS (application layer).

**Level 3 — How it works (mid-level engineer):**
The OS kernel implements Transport and Internet layers. The socket API is the boundary between user space (Application) and kernel space (Transport + Internet). `send()` on a TCP socket passes data to the kernel's TCP stack which segments it, wraps in IP packets, passes to the NIC driver (Network Access). Incoming packets: NIC DMA's packets into ring buffer → kernel interrupt → IP processing (routing decision) → TCP processing (sequence/ack) → copy to socket receive buffer → `recv()` returns data. The IP packet's TTL is decremented by each router; when TTL=0, ICMP "time exceeded" is returned. This is how `traceroute` works — it sends packets with TTL=1,2,3... and maps the ICMP responses.

**Level 4 — Why it was designed this way (senior/staff):**
The end-to-end principle (articulated by Saltzer, Reed, and Clark in 1984) is the philosophical foundation of TCP/IP. The core argument: reliability functions should be implemented at the endpoints, not the network. A network that guarantees reliability (like X.25) is more complex, harder to evolve, and its guarantees are only as strong as the weakest link. A best-effort network with reliability at endpoints (TCP) can use any underlying medium, can evolve independently, and puts no requirements on the network core. This is why the internet survived the transition from copper to fibre to satellite to 5G — none of these changes required modifying TCP/IP itself. The "thin waist" design (many applications and networks, but a single IP layer between them) is the reason for the internet's extraordinary longevity and adaptability.

---

### ⚙️ How It Works (Mechanism)

**Socket API — the application/kernel boundary:**
```python
import socket

# TCP socket (Transport layer: reliable, connection-oriented)
tcp_sock = socket.socket(socket.AF_INET,    # IPv4 (Internet layer)
                         socket.SOCK_STREAM)  # TCP (Transport layer)

# Connect: TCP 3-way handshake happens here
tcp_sock.connect(('93.184.216.34', 80))

# Send HTTP request (Application layer)
request = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
tcp_sock.sendall(request)   # OS TCP stack handles segmentation

# Receive response
response = tcp_sock.recv(4096)  # OS TCP stack handles reassembly
print(response[:200])

tcp_sock.close()  # TCP FIN → kernel sends FIN packet

# UDP socket (Transport layer: unreliable, connectionless)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.sendto(b"\x00\x01", ('8.8.8.8', 53))  # DNS query
```

**Inspect the stack in action:**
```bash
# Layer 2 (Network Access) — ARP table
ip neigh show  # IP → MAC mapping
arp -n

# Layer 3 (Internet) — routing and ICMP
ip route show               # routing table
ping 8.8.8.8                # ICMP echo (Layer 3 test)
traceroute 8.8.8.8          # map Layer 3 path (TTL trick)

# Layer 4 (Transport) — TCP/UDP sockets
ss -tlnp        # TCP listening sockets
ss -ulnp        # UDP listening sockets
ss -tnp         # active TCP connections
netstat -an     # (older) all connections

# Layer 7 (Application)
curl -v http://example.com  # full HTTP trace
dig example.com             # DNS query
```

**TCP/IP packet flow (simplified):**
```
Application: send(sock, data)
      │
Kernel Transport (TCP):
  - segment data (MSS ≈ 1460B for Ethernet)
  - add TCP header (ports, seq, ack, flags)
  - manage window, retransmits
      │
Kernel Internet (IP):
  - add IP header (src/dst IP, TTL=64, proto=TCP)
  - routing lookup (which interface to send from)
  - fragment if packet > MTU (rare with PMTUD)
      │
Kernel Network Access (Ethernet driver):
  - ARP lookup: dst IP → dst MAC
  - add Ethernet header + CRC
  - DMA to NIC ring buffer
      │
NIC Hardware:
  - transmit bits on wire
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────────┐
│  Browser → Web Server: TCP/IP layer interaction      │
└──────────────────────────────────────────────────────┘

 BROWSER (192.168.1.100)        SERVER (93.184.216.34)
 
 App: HTTP GET /                 App: Parse HTTP, send 200
   ↓ write to socket               ↑ read from socket
 Transport: TCP                  Transport: TCP
   Seq=1, Port 52341→80            Ack=1, Seq=2001
   ↓ kernel TCP stack              ↑ kernel TCP stack
 Internet: IP                    Internet: IP
   src=192.168.1.100               dst=93.184.216.34
   dst=93.184.216.34               src=93.184.216.34
   ↓                               ↑
 NetAccess: Ethernet              NetAccess: Ethernet
   src=AA:BB:CC (laptop)           src=EE:FF:00 (NIC)
   dst=11:22:33 (router)           dst=CC:DD:EE (switch)
        │                               ↑
        ├── Router 1: new Ethernet hdr ─┤
        ├── Router 2: new Ethernet hdr ─┤
        └── ... n routers              ─┘
           IP unchanged throughout
           MAC changes at every hop
```

---

### 💻 Code Example

**Example — Inspect packet headers at each layer:**
```python
#!/usr/bin/env python3
"""Inspect TCP/IP layers of an HTTP request."""
import socket
import struct

def parse_ip_header(data):
    """Parse IPv4 header fields."""
    ihl = (data[0] & 0x0F) * 4  # Header length in bytes
    ttl = data[8]
    protocol = data[9]  # 6=TCP, 17=UDP, 1=ICMP
    src_ip = socket.inet_ntoa(data[12:16])
    dst_ip = socket.inet_ntoa(data[16:20])
    proto_name = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}.get(protocol, str(protocol))
    print(f"  IP Layer: {src_ip} → {dst_ip} | TTL={ttl} | proto={proto_name}")
    return ihl, protocol

def parse_tcp_header(data):
    """Parse TCP header fields."""
    src_port, dst_port = struct.unpack('!HH', data[0:4])
    seq = struct.unpack('!I', data[4:8])[0]
    flags = data[13]
    flag_str = ''.join([
        'S' if flags & 0x02 else '',
        'A' if flags & 0x10 else '',
        'F' if flags & 0x01 else '',
        'R' if flags & 0x04 else '',
    ])
    print(f"  TCP Layer: port {src_port} → {dst_port} | seq={seq} | flags={flag_str}")

# Make a TCP connection and show the layers
host = 'example.com'
ip = socket.gethostbyname(host)
print(f"Connecting to {host} ({ip}:80)")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, 80))

# Application layer
request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
print(f"\nApplication Layer:")
print(f"  HTTP: GET / HTTP/1.1 (Host: {host})")

sock.sendall(request.encode())
response = sock.recv(4096)
print(f"\nResponse Application Layer:")
print(f"  {response[:response.index(b'\r\n')].decode()}")

sock.close()
```

---

### ⚖️ Comparison Table

| Aspect | TCP/IP Model | OSI Model |
|---|---|---|
| Layers | 4 | 7 |
| Origin | DARPA/DoD practice | ISO standard |
| Status | Actual internet | Reference model |
| Session layer | Not separate | Layer 5 |
| Presentation layer | Not separate | Layer 6 |
| Application layer | Layers 5+6+7 combined | Layer 7 only |
| Use | Implementation | Conceptual reference |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| TCP/IP and OSI are equivalent | TCP/IP has 4 layers and is what the internet uses; OSI has 7 layers and is a reference model; they're related but not equivalent |
| IP guarantees packet delivery | IP is best-effort; packets can be lost, duplicated, or reordered; TCP provides reliability on top of IP |
| MAC addresses are used for internet routing | MAC addresses are local to a single network segment; IP addresses are used for routing; MACs change at every router hop |
| TCP/IP is slow because of all the overhead | TCP/IP is designed for efficiency; modern NICs do TCP offloading in hardware; at 100Gbps+ speeds, the overhead is negligible |
| IPv6 is a different protocol stack | IPv6 replaces IPv4 at the Internet layer only; TCP, UDP, HTTP, and all application protocols work unchanged over IPv6 |

---

### 🚨 Failure Modes & Diagnosis

**"Connectivity works but application doesn't respond"**

**Symptom:**
`ping server.example.com` works. `curl http://server.example.com` times out.

**Diagnosis (OSI/TCP/IP layer by layer):**
```bash
# L3 OK: ping works → IP routing is fine
ping server.example.com

# L4: Can we establish TCP connection?
nc -zv server.example.com 80
# If "Connection refused": port 80 not listening / firewall
# If timeout: firewall dropping SYN silently

# Check if port is listening on server
ssh user@server "ss -tlnp | grep :80"
# If nothing → application not running / wrong port

# Check firewall
ssh user@server "iptables -L -n | grep 80"

# L7: Application response?
curl -v --connect-timeout 5 http://server.example.com/healthz
```

Most commonly: TCP port blocked (firewall), application not listening on `0.0.0.0` (only `127.0.0.1`), or application crashed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OSI Model` — the reference model that TCP/IP maps to; understanding OSI gives context for why TCP/IP has 4 layers

**Builds On This (learn these next):**
- `TCP` — the transport layer protocol that provides reliability
- `UDP` — the alternative transport layer protocol for low-latency applications
- `IP Addressing` — the Internet layer's addressing scheme

**Alternatives / Comparisons:**
- `OSI Model` — 7-layer reference model; conceptual framework that maps to TCP/IP
- `QUIC` — modern transport protocol that combines aspects of TCP and TLS, implemented over UDP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LAYER 4 (App) │ HTTP, DNS, SSH — what apps use          │
│ LAYER 3 (Tx)  │ TCP/UDP — reliable or fast delivery     │
│ LAYER 2 (IP)  │ IP routing — global addressing, routing  │
│ LAYER 1 (Net) │ Ethernet/Wi-Fi — local delivery, MAC    │
├──────────────────────────────────────────────────────────┤
│ KEY INSIGHT   │ IP is the "thin waist" — everything      │
│               │ above runs over IP; anything below       │
│               │ (cable, fibre, 5G) carries IP packets    │
├──────────────────────────────────────────────────────────┤
│ PACKET        │ Ethernet[IP[TCP[HTTP data]]]             │
│ STRUCTURE     │ Each layer wraps the layer above         │
├──────────────────────────────────────────────────────────┤
│ IP INVARIANT  │ Source/dest IP unchanged end-to-end      │
│               │ Source/dest MAC changes at every hop     │
├──────────────────────────────────────────────────────────┤
│ ONE-LINER     │ "4-layer stack that powers the internet: │
│               │ from cable bits to HTTP bytes"           │
├──────────────────────────────────────────────────────────┤
│ NEXT EXPLORE  │ TCP → UDP → IP Addressing → DNS          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The "end-to-end principle" says that reliability should be implemented at the endpoints, not the network. But modern networks violate this in several ways: NAT (network address translation), middleboxes (DPI, firewalls), and CDNs (which terminate TCP connections early). For each of these, describe: (a) exactly which TCP/IP layer they operate at, (b) how they technically violate the end-to-end principle, and (c) what problem they solve that makes the violation worthwhile — and whether QUIC (running over UDP, encrypting everything) was partly designed to prevent these violations.

**Q2.** A network packet travels from a home laptop (192.168.1.100) through a NAT router (public IP: 203.0.113.1) to a web server (93.184.216.34). Draw the complete state of the IP and TCP headers — source IP, destination IP, source port, destination port — at four points: (1) between laptop and router, (2) between router and internet, (3) between internet and server, (4) in the server's TCP stack. Explain why this works despite the private IP (192.168.1.100) being unreachable from the internet.
