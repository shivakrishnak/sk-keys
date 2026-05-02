---
layout: default
title: "tcpdump / Wireshark"
parent: "Linux"
nav_order: 149
permalink: /linux/tcpdump-wireshark/
number: "0149"
category: Linux
difficulty: ★★★
depends_on: Networking, Linux Networking (ip, ss, netstat)
used_by: Observability & SRE, iptables / nftables, Linux Security Hardening
related: iptables / nftables, strace / ltrace, Linux Networking (ip, ss, netstat)
tags:
  - linux
  - networking
  - observability
  - deep-dive
---

# 149 — tcpdump / Wireshark

⚡ TL;DR — `tcpdump` and Wireshark capture raw network packets and decode them into human-readable protocol data — they are the ultimate "ground truth" tools when higher-level tools (ss, curl, logs) disagree about what is actually happening on the network.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A service claims it sent a request but the server says it never arrived. Both sides are "correct" from their perspective — the application logs say "sent", the server logs say "nothing received". Is it the network? A firewall? The wrong IP? A packet being silently dropped? Without packet capture, you're playing he-said-she-said between application logs and kernel counters. You cannot prove what actually traversed the wire.

**THE BREAKING POINT:**
A TLS handshake fails intermittently. The application logs "connection reset". The server logs nothing. Firewall logs show ACCEPT. DNS resolves correctly. Every diagnostic layer says "fine" — but the connection fails. The only way to find the truth is to capture the actual bytes that flow between client and server.

**THE INVENTION MOMENT:**
This is exactly what tcpdump/Wireshark solves. A capture shows: the client sends ClientHello, the server responds with a TCP RST immediately — meaning the server is actively refusing the connection at the TCP level before TLS begins. Now you know: it's not TLS, it's a firewall rule running after iptables ACCEPT, or the application process crashed. Packet capture eliminates hypothesis; it shows fact.

---

### 📘 Textbook Definition

**tcpdump** is a command-line packet analyser that uses the `libpcap` library (Packet CAPture) to capture packets from network interfaces. It uses BPF (Berkeley Packet Filter) — a kernel-level byte-code virtual machine — to filter packets in the kernel before they reach user space, making capture efficient even on high-traffic interfaces.

**Wireshark** is the graphical front-end for the same libpcap/npcap capture mechanism, with a deep dissector library that decodes hundreds of protocols and presents them as structured trees. It can read packet capture files (`.pcap`, `.pcapng`) produced by tcpdump. Both tools produce the same raw captures; the difference is analysis power and interface.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
tcpdump captures raw packets from the wire and decodes them; Wireshark adds a GUI and protocol dissection library on top.

**One analogy:**

> tcpdump is a court stenographer at the network. Everything said (every byte sent) is recorded verbatim. After the trial, you can read the transcript and see exactly who said what, in what order, and at what time. `ss` only tells you who is connected to whom; tcpdump tells you what they said.

**One insight:**
tcpdump captures packets after the NIC but before most software processing. This means you see packets that were sent but never reached the application (blocked by iptables), malformed packets the kernel silently discarded, and retransmissions the TCP stack sent automatically — none of which appear in application logs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Packet capture happens at a defined point in the kernel networking stack (usually after the NIC driver, before iptables).
2. BPF filters run in the kernel, filtering packets before they are copied to user space.
3. tcpdump captures frames, not application data — it sees TCP segments, not HTTP requests (unless you capture and reassemble).
4. The NIC must be in promiscuous mode to capture traffic not addressed to the host.

**DERIVED DESIGN:**
`libpcap` opens a raw socket and registers a BPF program with the kernel. When a packet arrives at the NIC, the kernel runs the BPF filter against it. If the filter matches, the packet is copied into a ring buffer in kernel memory. `tcpdump` maps this buffer into user space and reads from it. The copy overhead (kernel → user space) is the main performance cost; BPF filtering minimises this by discarding non-matching packets in the kernel before the copy.

Modern `tcpdump` uses AF_PACKET or AF_XDP sockets. Wireshark can use the same libpcap mechanism for live capture, or read `.pcap` files for offline analysis. Protocol dissectors in Wireshark are written in C or Lua and decode the raw bytes into structured fields (TCP checksum, HTTP method, TLS version).

**THE TRADE-OFFS:**
**Gain:** Ground truth — what actually traversed the wire; full packet content including headers and payload.
**Cost:** CPU and disk overhead at high packet rates; security risk (captures all data including credentials); requires root/CAP_NET_RAW; captures at one point only — you don't see both sides of a remote connection simultaneously.

---

### 🧪 Thought Experiment

**SETUP:**
A client sends `curl http://api.internal/health`. The response is sometimes 200, sometimes times out. Nothing in the application logs explains the intermittent failure.

**WITHOUT PACKET CAPTURE:**
You see an average response time increase in your APM tool. You suspect the database. You add logging. You restart services. The problem persists. You've been debugging for 4 hours.

**WITH PACKET CAPTURE:**

```bash
# Capture on the API server while the failure happens
tcpdump -i eth0 -w /tmp/api_capture.pcap \
  host client-ip and port 80

# After failure, analyse:
tcpdump -r /tmp/api_capture.pcap -nn
```

The capture reveals: every 7th connection, the client's SYN arrives but the server sends no SYN-ACK. The server has a half-open connection table that fills up (SYN flood from a misconfigured service). The TCP accept queue is full and new SYNs are silently dropped. This appears nowhere in application logs — only packet capture reveals it.

**THE INSIGHT:**
When application logs and server logs disagree, packet capture is the arbiter. The packet is the ground truth — it either arrived or it didn't, and capture proves which.

---

### 🧠 Mental Model / Analogy

> tcpdump is like wiretapping a phone line with a transcript machine. `ss` tells you "there's a call currently in progress between Alice and Bob". tcpdump gives you the complete transcript: "Alice said SYN at 10:00:00.001, Bob said SYN-ACK at 10:00:00.002, Alice said GET /api/v1/users at 10:00:00.003...". Every word, in order, timestamped to microsecond precision.

- "Phone call" → TCP connection
- "Wiretap position" → capture point in kernel stack
- "Transcript" → pcap file
- "BPF filter" → only record calls involving a specific number

Where this analogy breaks down: in encrypted communications (TLS), tcpdump sees only ciphertext — the "transcript" is scrambled. For TLS debugging you need the session key (from SSLKEYLOGFILE) or a man-in-the-middle proxy.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
tcpdump records every network packet sent or received by your computer, like a flight recorder for your network connection. You can play it back later to see exactly what was sent and received, when, and from where. Wireshark does the same thing but with a graphical interface that colour-codes different types of network conversations.

**Level 2 — How to use it (junior developer):**
`tcpdump -i eth0 host 8.8.8.8` captures traffic to/from Google DNS. `tcpdump -i eth0 port 80` captures HTTP. `-w file.pcap` saves to file; `-r file.pcap` reads back. `-nn` suppresses name resolution (faster output). `-A` prints packet content as ASCII. `tcpdump -i any` captures on all interfaces. Load `.pcap` files in Wireshark for GUI analysis. Common: `tcpdump -i eth0 -nn -w /tmp/out.pcap host <target>`.

**Level 3 — How it works (mid-level engineer):**
tcpdump opens a raw socket (SOCK_RAW) and uses `setsockopt(SO_ATTACH_FILTER)` to attach a compiled BPF bytecode program. The filter runs in the kernel for every packet — packets not matching the filter are discarded before the copy to user space. High-rate captures must carefully balance buffer size (`-B` flag, default 2MB) against drop rate (visible in tcpdump's final summary: "X packets dropped by kernel"). The capture point is after the NIC driver, meaning you see packets that will be later dropped by iptables — useful for debugging firewall rules. Use `-s 0` (snaplen) to capture full packets; default snaplen of 262144 bytes captures most packets fully.

**Level 4 — Why it was designed this way (senior/staff):**
The BPF architecture (Van Jacobson, 1992) was specifically designed to solve the performance problem of packet capture. Earlier mechanisms copied every packet to user space and filtered there — at high packet rates, this created a massive CPU and memory bus bottleneck. BPF moves the filter into the kernel as a safe bytecode program, eliminating the copy for non-matching packets. This design was so effective that BPF evolved into eBPF (extended BPF) — a general-purpose in-kernel execution environment now used for everything from tracing to networking to security enforcement. tcpdump's filter language is compiled to BPF bytecode at startup; you can see this bytecode with `tcpdump -d 'your filter expression'`.

---

### ⚙️ How It Works (Mechanism)

**Essential tcpdump commands:**

```bash
# List available interfaces
tcpdump -D

# Capture on specific interface, suppress DNS
tcpdump -i eth0 -nn

# Capture to file (rotate at 100MB)
tcpdump -i eth0 -w /tmp/cap.pcap \
  -C 100 -W 5  # 5 files max, 100MB each

# Read from file
tcpdump -r /tmp/cap.pcap -nn

# Capture HTTP traffic with content
tcpdump -i eth0 -A -s 0 port 80

# Capture between two hosts
tcpdump -i eth0 host 10.0.0.1 and host 10.0.0.2

# Capture SYN packets only (connection attempts)
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# Capture TCP RST (connection resets)
tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'

# Capture DNS queries
tcpdump -i eth0 -nn udp port 53

# Capture everything except SSH (avoid feedback loop)
tcpdump -i eth0 -nn not port 22

# Show packets in hex + ASCII
tcpdump -i eth0 -XX port 8080

# Filter by CIDR
tcpdump -i eth0 net 192.168.0.0/24
```

**BPF filter syntax:**

```bash
# Combine filters
tcpdump 'host 10.0.0.1 and (port 80 or port 443)'
tcpdump 'src host 10.0.0.1 and dst port 80'
tcpdump 'not port 22 and not port 53'

# TCP flags
# tcp-syn=0x02, tcp-ack=0x10, tcp-rst=0x04, tcp-fin=0x01
tcpdump 'tcp[13] & 2 != 0'  # SYN packets
tcpdump 'tcp[13] = 4'       # RST only (no other flags)
tcpdump 'tcp[13] & 18 = 18' # SYN+ACK (0x02|0x10)

# Packet size
tcpdump 'greater 1000'      # packets > 1000 bytes
tcpdump 'less 64'           # tiny packets (possibly malformed)
```

**Wireshark display filters (different from BPF):**

```
ip.addr == 10.0.0.1
tcp.port == 443
tcp.flags.syn == 1 && tcp.flags.ack == 0
http.request.method == "POST"
tls.handshake.type == 1        (ClientHello)
dns.qry.name contains "google"
frame.time_delta > 0.5         (slow responses)
tcp.analysis.retransmission    (show only retransmissions)
tcp.analysis.zero_window       (TCP zero window — backpressure)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  DEBUGGING: Intermittent TLS Handshake Failure │
└────────────────────────────────────────────────┘

 tcpdump -i eth0 -nn -w /tmp/debug.pcap \
   host api.internal and port 443
       │
       ▼ (capture runs while failure occurs)
 Wireshark opens /tmp/debug.pcap
       │
       ▼
 Filter: tls.handshake.type == 1 (ClientHellos)
       │  Find a failed attempt
       ▼
 Follow TCP stream for that attempt:
       │  Client → Server: SYN
       │  Server → Client: SYN-ACK
       │  Client → Server: ACK (connection up)
       │  Client → Server: ClientHello (TLS)
       │  Server → Client: Alert: handshake_failure
       │                   ← Server rejected TLS
       ▼
 Inspect ClientHello: supported cipher suites
       │  Only TLS 1.2 ciphers offered by client
       ▼
 Server requires TLS 1.3 minimum
       │
       ▼
 Root cause: client TLS library version mismatch
 Fix: update client or relax server TLS policy
```

**FAILURE PATH:**
If tcpdump shows no packets at all for a connection that the client says it sent, the packet was dropped before the capture point — check iptables PREROUTING, routing decisions, or NIC hardware filtering.

---

### 💻 Code Example

**Example 1 — Capture and quick analysis:**

```bash
#!/bin/bash
# Capture 60s of traffic to a target host, then analyse
TARGET=${1:-10.0.0.1}
PORT=${2:-443}
OUTFILE="/tmp/capture_$(date +%Y%m%d_%H%M%S).pcap"

echo "Capturing 60s of traffic to $TARGET:$PORT..."
timeout 60 tcpdump -i any -nn -s 0 \
  -w "$OUTFILE" \
  "host $TARGET and port $PORT"

echo ""
echo "=== Packet Summary ==="
tcpdump -r "$OUTFILE" -nn -q

echo ""
echo "=== TCP Flag Analysis ==="
echo -n "SYN: "
tcpdump -r "$OUTFILE" -nn \
  'tcp[tcpflags] & tcp-syn != 0 and
   tcp[tcpflags] & tcp-ack = 0' 2>/dev/null \
  | wc -l

echo -n "RST: "
tcpdump -r "$OUTFILE" -nn \
  'tcp[tcpflags] & tcp-rst != 0' 2>/dev/null \
  | wc -l

echo "Saved to: $OUTFILE"
echo "Open in Wireshark: wireshark $OUTFILE"
```

**Example 2 — Monitor for suspicious connections:**

```bash
#!/bin/bash
# Alert on connections to unexpected external IPs
# (useful for detecting exfiltration or beaconing)
ALLOWED_NETS="10.0.0.0/8 192.168.0.0/16 172.16.0.0/12"

tcpdump -i eth0 -nn -l \
  'tcp[tcpflags] & tcp-syn != 0 and
   tcp[tcpflags] & tcp-ack = 0' \
  | while read line; do
    dst=$(echo "$line" | grep -oP '> \K[\d.]+' \
      | head -1)
    # Check if in allowed networks
    allowed=false
    for net in $ALLOWED_NETS; do
      # (simplified check — use ipcalc in production)
      if [[ "$dst" =~ ^(10\.|192\.168\.|172\.) ]]; then
        allowed=true
      fi
    done
    if ! $allowed; then
      echo "EXTERNAL CONNECTION: $line" | \
        logger -p security.warning
    fi
  done
```

**Example 3 — Measure RTT from packet capture:**

```bash
# Capture a SYN/SYN-ACK pair to measure network RTT
# (avoids application processing overhead in ping)
tcpdump -i eth0 -ttt -nn \
  "host $TARGET and tcp[tcpflags] & 18 != 0" \
  -c 10
# -ttt: show time delta between packets
# Look for SYN followed by SYN-ACK: delta = RTT
```

---

### ⚖️ Comparison Table

| Tool          | What It Shows                   | Depth           | Real-time     | Ease          |
| ------------- | ------------------------------- | --------------- | ------------- | ------------- |
| **tcpdump**   | Raw packets, decoded headers    | Protocol-level  | Yes           | CLI, moderate |
| **Wireshark** | Full protocol decode, streams   | Deepest         | Yes + offline | GUI, easiest  |
| ss / netstat  | Socket state, connection table  | Socket-level    | Yes           | Easy          |
| ip -s link    | Interface error/byte counters   | Interface-level | Yes           | Easy          |
| strace        | Syscalls (including socket ops) | Syscall-level   | Yes           | Complex       |
| eBPF/bpftrace | Custom kernel tracing           | Any point       | Yes           | Expert        |

How to choose: start with `ss` for connection state; use `tcpdump` when you need to verify what's on the wire; use Wireshark for complex protocol debugging; use `strace` when you need to see how the application is calling sockets.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                 |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| tcpdump shows everything on the network             | It shows packets on the local interface only; to capture from multiple hosts you need a network tap or port mirroring                                                   |
| Capture on any interface captures all traffic       | `-i any` captures from all local interfaces but still only on the local machine; encrypted switch ports prevent seeing other hosts' traffic                             |
| tcpdump can decode TLS/HTTPS content                | tcpdump sees only encrypted ciphertext for TLS; decrypt with SSLKEYLOGFILE or a MITM proxy                                                                              |
| A "drop by kernel" means the packets were malicious | Kernel drops in tcpdump's summary mean the ring buffer was full (capture too slow/no buffer space) — increase `-B` buffer size or filter more aggressively              |
| tcpdump capture point is after iptables             | **FALSE** — default AF_PACKET capture is BEFORE iptables (i.e., you see packets that will later be dropped by iptables). This is valuable for debugging firewall rules. |

---

### 🚨 Failure Modes & Diagnosis

**High Packet Drop Rate in tcpdump**

**Symptom:**
tcpdump output ends with "N packets dropped by kernel" or drop percentage visible with `tcpdump -S`.

**Root Cause:**
The kernel's ring buffer for packet capture fills up faster than tcpdump can read it. Happens on high-traffic interfaces (>100k pps) with overly broad capture filters.

**Diagnostic Command:**

```bash
# See drop count in real time
tcpdump -i eth0 -nn --count your-filter 2>&1 | \
  tail -5  # shows final drop count
```

**Fix:**

```bash
# Increase kernel buffer (default 2MB, increase to 256MB)
tcpdump -i eth0 -B 262144 your-filter -w out.pcap

# Narrow the filter to reduce captured packet volume
tcpdump -i eth0 -nn host specific-ip and port specific-port

# Write to file (faster than stdout decoding)
tcpdump -i eth0 -w /tmp/cap.pcap  # much lower overhead
```

**Prevention:**
Always write to file (`-w`) rather than live-decode for high-traffic captures; always use precise BPF filters.

---

**tcpdump Shows No Packets for a Known-Failing Connection**

**Symptom:**
`curl` reports "connection refused" but tcpdump on the server shows no SYN packets arriving.

**Root Cause:**
The packet was dropped before reaching the capture point. Could be: wrong interface (capture on `eth0` but traffic arrives on `eth1`); routing sent traffic elsewhere; NIC hardware filtering.

**Diagnostic Command:**

```bash
# Capture on ALL interfaces
tcpdump -i any -nn host client-ip and port target-port

# Verify routing from client's perspective
ip route get server-ip   # run on client side
```

**Fix:**
Identify the correct interface with `ip route get`; capture on that interface. If still not visible, the packet is being dropped before the capture point (possible eBPF/XDP drop earlier in the stack).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Networking` — understanding TCP/IP headers, flags (SYN, ACK, RST), and the packet structure is essential for reading tcpdump output
- `Linux Networking (ip, ss, netstat)` — tcpdump provides deeper analysis of what ss/ip show at the socket level

**Builds On This (learn these next):**

- `iptables / nftables` — tcpdump is the debugging tool that reveals when iptables rules are or aren't firing
- `Observability & SRE` — in production, distributed tracing and APM tools are built on the same principles as packet capture but at higher layers
- `strace / ltrace` — complements tcpdump: strace shows system calls including socket operations; tcpdump shows what those calls put on the wire

**Alternatives / Comparisons:**

- `Wireshark` — GUI version with protocol dissectors; use for complex analysis of pcap files
- `tshark` — command-line Wireshark with the full dissector library; like `tcpdump` but with more protocol awareness
- `eBPF/bpftrace` — capture arbitrary kernel data at any point in the network stack, not just at the NIC level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel packet capture using BPF filters   │
│              │ — ground truth for network debugging      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Application logs can't see network layer  │
│ SOLVES       │ events (drops, resets, retransmissions)   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Capture point is BEFORE iptables — so you │
│              │ see packets that firewall rules will drop  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Application and server logs disagree;     │
│              │ TLS failures; intermittent timeouts       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Production at high traffic without narrow │
│              │ BPF filters — buffer overruns cause drops │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Ground truth visibility vs security risk  │
│              │ (credentials in plaintext traffic)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A court stenographer for your network —  │
│              │  verbatim record of every byte exchanged" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Wireshark dissectors → eBPF → tshark     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A security engineer notices that a production server is connecting to an external IP every 10 minutes. The application team says "we don't have any external calls in our code". Design a tcpdump-based investigation plan: specify the exact capture command, the BPF filter, the output format, and how you would use Wireshark to identify the process responsible, the protocol being used, and whether data is being exfiltrated.

**Q2.** tcpdump shows a server is sending TCP RST packets in response to every incoming connection attempt on port 8443, but the application log shows the service is running and healthy. You've verified the port is listening with `ss -tlnp`. List all the layers of the Linux networking stack that exist between a packet arriving at the NIC and reaching the application socket, and for each layer, explain how to determine whether that layer is the source of the RST.
