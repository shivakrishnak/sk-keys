---
id: NET-034
title: "Networking Quick Recall Card"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-020, NET-021, NET-022, NET-023, NET-024, NET-025, NET-026, NET-027, NET-028, NET-029, NET-030, NET-031, NET-032
used_by: NET-053
related: NET-018, NET-053, NET-054
tags:
  - networking
  - reference
  - recall
  - interview
  - cheatsheet
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/net/networking-quick-recall-card/
---

**⚡ TL;DR** - A consolidated one-page reference for all
L2 Networking concepts: protocols, ports, commands,
failure modes, and the mental models that connect them.
Use this before interviews and during incident debugging
to quickly locate the right concept.

| #034 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | All L2 Networking entries (NET-020 through NET-032) | |
| **Used by:** | Networking System Design Interview Patterns | |
| **Related:** | Top 10 Networking Interview Questions, Networking System Design Interview Patterns | |

---

### 🔥 How to Use This Card

This is a structured recall reference, not a learning
document. Use it to:
1. **Before an interview:** review each concept until
   you can state the one-liner without looking
2. **During incident:** scan the diagnostic table to
   identify which tool answers your question
3. **After an incident:** verify you knew the right
   tool; review any card where you hesitated

---

### 📌 Transport Layer Quick Reference

**TCP - The Reliable Byte Stream:**

```
┌──────────────────────────────────────────────────────────┐
│  TCP CORE FACTS                                          │
├────────────────────────────────────────────────────────  │
│  Type:    Connection-oriented, reliable, byte stream    │
│  Setup:   3-way handshake (1 RTT) SYN→SYN-ACK→ACK      │
│  Teardown:4-way FIN + TIME_WAIT (60s)                   │
│  Header:  20+ bytes (seq, ack, flags, window, checksum) │
│  Guarantees: ordered delivery, reliability (retransmit) │
│             flow control (rwnd), congestion (cwnd)      │
│  Byte stream: NO message boundaries - add framing!      │
│  Key diagnosis: ss -tnp, netstat -s | grep retrans      │
├────────────────────────────────────────────────────────  │
│  TCP KEY STATES                                         │
│  LISTEN → accepting connections                         │
│  SYN_SENT → client waiting for SYN-ACK                 │
│  ESTABLISHED → data flowing                             │
│  TIME_WAIT → 60s after close, prevents stale packets   │
│  CLOSE_WAIT → waiting for app to close (app bug risk)  │
└──────────────────────────────────────────────────────────┘
```

**UDP - The Fast Datagram:**

```
┌──────────────────────────────────────────────────────────┐
│  UDP CORE FACTS                                          │
├────────────────────────────────────────────────────────  │
│  Type:    Connectionless, unreliable, datagram          │
│  Header:  8 bytes (src port, dst port, length, checksum)│
│  Setup:   0 RTT (fire and forget)                       │
│  Guarantees: NONE. Loss, reorder, duplication possible  │
│  Use when: old data is WORSE than no data               │
│  Use for: DNS, VoIP, video, gaming, NTP, QUIC base     │
│  Key trap: no timeout on recvfrom() → blocks forever!  │
│  Key diagnosis: ss -unp, netstat -su                    │
└──────────────────────────────────────────────────────────┘
```

---

### 📌 Network Layer Quick Reference

**IP Addressing:**

```
┌──────────────────────────────────────────────────────────┐
│  IP ADDRESS QUICK FACTS                                  │
├──────────────┬───────────────────────────────────────────┤
│  Private     │  10.0.0.0/8, 172.16.0.0/12,             │
│  Ranges      │  192.168.0.0/16                          │
├──────────────┼───────────────────────────────────────────┤
│  Special     │  127.0.0.1 = loopback                    │
│              │  0.0.0.0 = all interfaces (bind)         │
│              │  169.254.x.x = APIPA (DHCP failed)       │
│              │  255.255.255.255 = limited broadcast      │
├──────────────┼───────────────────────────────────────────┤
│  CIDR math   │  /24 = 254 hosts                         │
│              │  /28 = 14 hosts (NAT GW, bastion)        │
│              │  /32 = single host route                 │
│              │  Hosts = 2^(32-prefix) - 2               │
└──────────────┴───────────────────────────────────────────┘
```

**Subnetting rules to memorize:**

```
/8  = 16.7M hosts   | /24 = 254 hosts
/16 = 65,534 hosts  | /28 = 14 hosts
/20 = 4,094 hosts   | /30 = 2 hosts (point-to-point)
/22 = 1,022 hosts   | /32 = 1 host (single route)
```

---

### 📌 Key Protocols Reference

```
┌──────────────────────────────────────────────────────────┐
│  Protocol Quick Reference                                │
├────────┬───────────────────────────────────────────────  │
│ DNS    │ UDP/TCP 53. Hierarchy: Root→TLD→Auth→Resolver   │
│        │ TTL matters: lower BEFORE DNS changes.         │
│        │ Diagnose: dig +trace, dig @8.8.8.8             │
├────────┼───────────────────────────────────────────────  │
│ ARP    │ L2. Maps IP→MAC within subnet. Broadcast.      │
│        │ No auth → ARP spoofing attacks.                │
│        │ Diagnose: ip neigh show, arping -D             │
├────────┼───────────────────────────────────────────────  │
│ DHCP   │ UDP 67/68. DORA: Discover/Offer/Request/Ack.   │
│        │ T1=50%, T2=87.5% of lease for renewal.        │
│        │ APIPA (169.254.x.x) = DHCP failure.           │
│        │ Diagnose: tcpdump port 67 or 68               │
├────────┼───────────────────────────────────────────────  │
│ NAT    │ NAPT: many private IPs share one public IP.    │
│        │ Tracks (priv IP:port) ↔ (pub port) per conn.  │
│        │ Breaks P2P (needs STUN/TURN), FTP, SIP.       │
│        │ UDP timeout: 30s. TCP timeout: varies.         │
├────────┼───────────────────────────────────────────────  │
│ HTTP   │ GET=safe+idempotent, POST=neither.             │
│        │ 2xx=OK, 4xx=client, 5xx=server.               │
│        │ 502=bad upstream, 504=upstream timeout.       │
│        │ Diagnose: curl -v, curl -w timing             │
└────────┴───────────────────────────────────────────────  │
```

---

### 📌 Routing Quick Reference

```
Routing: Longest Prefix Match
  /32 beats /28 beats /24 beats /16 beats /0

Default route: 0.0.0.0/0 = catch-all
  → Internet GW (for internet access)
  → VPN GW (for full-tunnel VPN)
  → Security appliance (for policy enforcement)

Commands:
  ip route show           ← see routing table
  ip route get 8.8.8.8   ← which route wins?
  ip route add/del        ← add/remove static route

Static: predictable, no auto-failover, small scale
OSPF:  enterprise, auto-converge, Dijkstra algorithm
BGP:   internet-scale, policy-based, 900K+ routes
```

---

### 📌 Load Balancing Quick Reference

```
┌──────────────────────────────────────────────────────────┐
│  Load Balancer Decision                                  │
├──────────────────┬───────────────────────────────────────┤
│  L4 (TCP/UDP)    │  No content inspection. Fast.        │
│                  │  Use for: raw TCP, low latency        │
├──────────────────┼───────────────────────────────────────┤
│  L7 (HTTP)       │  TLS termination, path routing,      │
│                  │  header injection, health checks     │
├──────────────────┴───────────────────────────────────────┤
│  Algorithms:                                            │
│    Round-robin    = equal duration requests            │
│    Least-conn     = mixed duration requests            │
│    IP hash        = sticky (no cookie needed)          │
│    Weighted RR    = heterogeneous server capacity      │
├──────────────────────────────────────────────────────────┤
│  Mandatory: /health endpoint (200=up, 503=down)        │
│  Anti-pattern: read remote_addr (gets LB IP)           │
│  Fix: read X-Forwarded-For for real client IP          │
└──────────────────────────────────────────────────────────┘
```

---

### 📌 Diagnostic Decision Tree

```
┌──────────────────────────────────────────────────────────┐
│  "I can't connect to SERVICE"                            │
├──────────────────────────────────────────────────────────┤
│  1. DNS: dig SERVICE → gets IP?                         │
│     No → DNS problem. Check: cat /etc/resolv.conf       │
│                              dig @8.8.8.8 SERVICE       │
│  2. Ping: ping -c 5 IP → replies?                      │
│     No → L3 routing issue. Check: traceroute -n IP     │
│                                    ip route get IP      │
│  3. TCP port: nc -zv IP PORT → connected?              │
│     Refused → service DOWN on that port                │
│     Timeout  → FIREWALL DROP rule                      │
│  4. HTTP: curl -v https://IP → 200?                    │
│     TLS error → cert issue                             │
│     4xx       → application auth/routing error         │
│     5xx       → application server error               │
│  5. Timing: curl -w "..." https://SERVICE              │
│     DNS > 100ms   → DNS slow (use @8.8.8.8 to test)   │
│     TCP > 200ms   → network route issue                │
│     TLS > 500ms   → TLS handshake slow                 │
│     TTFB > 1s     → application slow                   │
└──────────────────────────────────────────────────────────┘
```

---

### 📌 Key Failure Modes at a Glance

```
┌──────────────────────────────────────────────────────────┐
│  Symptom → Likely Cause → Diagnose With                  │
├──────────────────────────────────────────────────────────┤
│  Conn refused (immediate)  │ Service down   │ ss -lntp   │
│  Conn timeout (75s+)       │ Firewall DROP  │ traceroute │
│  169.254.x.x assigned      │ DHCP failure   │ dhclient   │
│  DNS works, ping fails      │ ICMP filtered  │ traceroute │
│  Ping works, port fails     │ Firewall/app   │ nc -zv     │
│  HTTP 502                   │ Backend down   │ curl -v LB │
│  HTTP 504                   │ Backend slow   │ curl -w    │
│  Duplicate IPs on LAN       │ ARP conflict   │ arping -D  │
│  NAT connection drops       │ UDP 30s timeout│ conntrack  │
│  High retransmit rate       │ Packet loss    │ netstat -s │
│  CLOSE_WAIT accumulates     │ App not closing│ ss -tnp    │
│  TIME_WAIT accumulates      │ Normal (busy)  │ ss -tn     │
│  LB sees all same IP        │ LB IP in app   │ X-Fwd-For  │
└──────────────────────────────────────────────────────────┘
```

---

### 📌 The 12 Most Important Networking Commands

```bash
# 1. See your IP and interfaces
ip addr show

# 2. See routing table
ip route show

# 3. Which route handles specific IP?
ip route get TARGET_IP

# 4. ARP table (MAC → IP on LAN)
ip neigh show

# 5. DNS lookup
dig +short DOMAIN A

# 6. DNS with trace (full delegation chain)
dig +trace DOMAIN A

# 7. What's listening on what ports?
ss -lntp

# 8. What connections are established?
ss -tnp | grep ESTAB

# 9. Test TCP port
nc -zv HOST PORT

# 10. HTTP timing breakdown
curl -o /dev/null -w "%{time_namelookup}s DNS\n\
%{time_connect}s TCP\n%{time_appconnect}s TLS\n\
%{time_starttransfer}s TTFB\n" https://HOST

# 11. Trace packet path
traceroute -n HOST

# 12. Capture traffic
sudo tcpdump -i eth0 -n "host IP and port PORT" -v
```

---

### 📌 TCP vs UDP Decision - One Sentence Each

```
Use TCP when: every byte must arrive in order
  (HTTP, SSH, database, email, file transfer)

Use UDP when: retransmitting old data is worse
than dropping it (video, VoIP, gaming, DNS, NTP)

Use QUIC when: you need TCP reliability without
TCP head-of-line blocking (HTTP/3)
```

---

### 📌 The 5 Socket Options You Must Always Know

```python
# 1. SO_REUSEADDR - server restart without EADDRINUSE
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# 2. TCP_NODELAY - disable Nagle (interactive/real-time)
s.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)

# 3. SO_KEEPALIVE - detect dead connections
s.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)

# 4. settimeout() - never block forever
s.settimeout(5.0)

# 5. TCP is byte stream - always use recv_exact()
def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk: raise EOFError
        buf += chunk
    return buf
```

---

### 📌 Well-Known Port Numbers

```
20/21 FTP  │  22 SSH      │  25 SMTP
53 DNS     │  80 HTTP     │  110 POP3
143 IMAP   │  443 HTTPS   │  3306 MySQL
5432 Postgres │ 6379 Redis │ 27017 MongoDB
8080 HTTP-alt │ 9092 Kafka │ 2181 ZooKeeper
```

---

### 💎 The 5 Sentences That Win Networking Interviews

```
1. "TCP guarantees ordered, reliable byte stream delivery
   via seq numbers + ACK + retransmit. The cost is 1 RTT
   handshake and head-of-line blocking."

2. "UDP sends datagrams with 8-byte header and zero
   overhead. Use it when retransmitting stale data is
   worse than dropping it: video, gaming, DNS."

3. "CIDR /24 means 24 bits fixed, 8 bits for 254 hosts.
   Smaller prefix = more hosts. /16 >> /24 >> /28."

4. "Longest prefix match: /32 beats /24 beats /0. The
   most specific route always wins."

5. "A load balancer needs a /health endpoint. Read
   X-Forwarded-For for real client IP - remote_addr
   behind an LB returns the LB's IP."
```