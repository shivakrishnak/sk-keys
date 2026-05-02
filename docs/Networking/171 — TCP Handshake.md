---
layout: default
title: "TCP Handshake"
parent: "Networking"
nav_order: 171
permalink: /networking/tcp-handshake/
number: "0171"
category: Networking
difficulty: ★★☆
depends_on: TCP, TCP/IP Stack
used_by: HTTP & APIs, TLS/SSL, Load Balancers
related: TCP Teardown, TCP, TLS/SSL, Congestion Control
tags:
  - networking
  - tcp
  - handshake
  - connection
---

# 171 — TCP Handshake

⚡ TL;DR — The TCP 3-way handshake (SYN → SYN-ACK → ACK) establishes a reliable, ordered connection by synchronising sequence numbers between client and server before any data flows — taking exactly 1.5 RTTs, which is why every new TCP connection adds 1-2 RTTs of latency before useful work begins.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a handshake, a server receiving a data packet has no way to know: Is this a new connection or the middle of an existing one? What sequence number should I start from? Is the client even reachable (is this a spoofed source IP)? The server would need to accept any packet as potentially meaningful, enabling SYN spoofing, replay attacks, and malformed connection attempts.

**THE BREAKING POINT:**
An HTTP server receives a packet with data. The server doesn't know: did the client start a new connection that was lost, or is this packet from an existing connection? Without a handshake, sequence numbers would need to start at 0 for every connection — easily exploited by an attacker who sends crafted packets with predicted sequence numbers to hijack an existing connection.

**THE INVENTION MOMENT:**
The 3-way handshake solves three problems simultaneously: (1) it synchronises initial sequence numbers (ISNs) chosen randomly to prevent hijacking, (2) it verifies the client's source IP is reachable (the server sends SYN-ACK to the claimed source — if spoofed, the ACK never arrives), and (3) it establishes the connection state machine on both sides before data flows. The "3" in 3-way is the minimum required to accomplish all three: SYN (client to server), SYN-ACK (server to client, proving server received client's SYN), ACK (client to server, proving client received server's SYN-ACK).

---

### 📘 Textbook Definition

The **TCP 3-way handshake** is the connection establishment process defined in RFC 793. The process: (1) Client sends SYN segment with client's Initial Sequence Number (ISN_C). (2) Server responds with SYN-ACK: ACK=ISN_C+1 (acknowledging client's SYN) and its own ISN_S. (3) Client sends ACK: ACK=ISN_S+1 (acknowledging server's SYN). After step 3, both sides have each other's ISN, both sides have verified reachability, and the connection is ESTABLISHED on both sides. Duration: 1.5 RTTs (half RTT to send SYN, 1 RTT for SYN-ACK round trip, client sends ACK at 1.5 RTT).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The TCP handshake is a three-step call-and-response (SYN, SYN-ACK, ACK) that establishes a connection by verifying both sides can communicate and synchronising their sequence numbers.

**One analogy:**
> "Can you hear me?" (SYN) — "Yes, I can hear you; can you hear me?" (SYN-ACK) — "Yes, I can hear you too." (ACK) → Conversation can begin. This is the minimum exchange that proves both parties can send and receive messages to each other before the actual conversation (data transfer) starts.

**One insight:**
The 3-way handshake takes 1.5 RTTs. On a 100ms RTT link, that's 150ms before the first byte of HTTP data can be sent. This is why connection reuse (HTTP keep-alive, connection pooling) and 0-RTT protocols (QUIC) are so important for performance.

---

### 🔩 First Principles Explanation

**THE THREE STEPS IN DETAIL:**

**Step 1: SYN (Client → Server)**
```
TCP Header:
  Source Port: 54321 (ephemeral)
  Dest Port: 443 (HTTPS)
  Sequence: ISN_C (random, e.g., 2893456128)
  ACK: 0 (not used)
  Flags: SYN=1
  Window: 65535
```
Client transitions: `CLOSED → SYN_SENT`

**Step 2: SYN-ACK (Server → Client)**
```
TCP Header:
  Source Port: 443
  Dest Port: 54321
  Sequence: ISN_S (random, e.g., 987654321)
  ACK: ISN_C + 1 = 2893456129  (confirms receipt of SYN)
  Flags: SYN=1, ACK=1
  Window: 65535
```
Server transitions: `LISTEN → SYN_RECEIVED`

**Step 3: ACK (Client → Server)**
```
TCP Header:
  Source Port: 54321
  Dest Port: 443
  Sequence: ISN_C + 1 = 2893456129
  ACK: ISN_S + 1 = 987654322  (confirms receipt of server's SYN)
  Flags: ACK=1
  Window: 65535
```
Both sides transition: `→ ESTABLISHED`

**WHY RANDOM ISNs?**
If ISN were always 0, an attacker could send: `SYN(seq=0)` from a spoofed IP, then send `data(seq=1, ACK=1)` — predicting the server's ISN. RFC 6528 specifies ISNs should be generated using a secret key + connection 4-tuple + clock to prevent prediction.

**SYN COOKIES (SYN flood mitigation):**
In a SYN flood attack, attackers send millions of SYN packets from spoofed IPs. The server allocates a `SYN_RECEIVED` state entry for each, exhausting memory. SYN cookies: encode connection state (IP, port, timestamp) into the ISN_S. No state allocated until the ACK arrives with the cookie. Linux: `net.ipv4.tcp_syncookies = 1` (default on).

---

### 🧪 Thought Experiment

**SETUP:**
Measure the practical impact of TCP handshake latency on a web page load.

**SCENARIO: 100ms RTT, webpage with 10 resources**

**HTTP/1.1 (no connection reuse):**
- 10 resources × 1.5 RTTs handshake = 15 RTTs = 1500ms
- + actual data transfer time
- Just handshakes alone = 1.5 seconds wasted

**HTTP/1.1 with Keep-Alive (connection reuse):**
- 1 handshake (1.5 RTT = 150ms) for first resource
- 9 subsequent resources: 0 handshake overhead (reuse connection)
- Savings: 1350ms

**HTTP/2 (one connection, multiplexed):**
- 1 TCP handshake (1.5 RTT) + 1 TLS handshake (1 RTT) = 2.5 RTTs = 250ms
- All 10 resources multiplexed: 0 additional handshake overhead
- Savings: 14 RTTs compared to HTTP/1.1 without keep-alive

**QUIC/HTTP3 (1-RTT):**
- 1 QUIC handshake (1 RTT = 100ms)
- 0-RTT on return visit (0ms)
- All resources multiplexed with no HoL blocking

**THE INSIGHT:**
HTTP/1.1 keep-alive and HTTP/2 multiplexing exist primarily to amortise the cost of the TCP handshake across multiple requests.

---

### 🧠 Mental Model / Analogy

> The TCP handshake is like dialling a phone number to establish a call before speaking. SYN: you dial. SYN-ACK: the other person picks up and says "Hello?" ACK: you respond "Hello, I can hear you." Now you can have a conversation (exchange data). Without this exchange, you might start speaking to a number that's busy, disconnected, or spoofed. The "3" steps is the minimum number to prove both directions of communication work. Compare to a radio operator: "This is Alpha, do you copy? Over." (SYN) → "Alpha, this is Bravo, copy loud and clear. Do you copy? Over." (SYN-ACK) → "Bravo, copy. Ready to transmit. Over." (ACK) → Data transmission begins.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Before two computers can talk over TCP, they do a three-step check to make sure both can communicate. The first computer says "ready?" (SYN), the second responds "ready, you ready?" (SYN-ACK), and the first confirms "yes, ready" (ACK). Only after this do they start actually transferring data. This takes a small amount of time — which is why using existing connections is faster than creating new ones.

**Level 2 — How to use it (junior developer):**
As a developer, you don't directly control the handshake. `socket.connect()` in Python or `new Socket()` in Java triggers it. The handshake completes before `connect()` returns. Implications: always use connection pools — don't create a new connection per request. In HTTP clients: enable keep-alive (`Connection: keep-alive`) so the TCP connection is reused across multiple requests. In databases: use connection pools (HikariCP, PgBouncer) to reuse TCP connections. Monitor: `ss -tn | grep SYN_SENT` shows connections in handshake. Firewall drop of SYN-ACK causes `SYN_SENT` to linger until timeout (21 seconds default).

**Level 3 — How it works (mid-level engineer):**
TCP's initial sequence numbers (ISN) are randomly generated to prevent sequence number prediction attacks. The ISN uses a counter incremented every 4 microseconds (RFC 793) plus a random offset. Modern kernels (Linux, BSD) use a cryptographic hash of the connection 4-tuple + a secret + time (RFC 6528). SYN retransmission: if SYN-ACK not received within RTO (initial ~1s, doubles each retry), the SYN is retransmitted. Default: up to 6 retransmissions (127 seconds total). Set via `net.ipv4.tcp_syn_retries`. SYN queue: server maintains a backlog of unacknowledged SYN_RECEIVED connections (incomplete queue) and ESTABLISHED connections awaiting `accept()` (complete queue). `listen(socket, backlog)` sets the ESTABLISHED backlog size. Set `net.ipv4.tcp_max_syn_backlog` for incomplete queue.

**Level 4 — Why it was designed this way (senior/staff):**
The 3-way handshake is the minimum that provides: (1) ISN synchronisation in both directions, (2) proof of reachability of both source addresses. A 2-way handshake (SYN+ACK in one response) would have the server send ISN_S but never confirm the client received it — so both sides don't have verified, agreed-upon ISNs. The handshake also serves as a resource allocation gate: OS allocates connection state only after the 3rd step, preventing an attacker from creating unlimited half-open connections (mitigated by SYN cookies). The 1.5-RTT cost is fundamental to TCP's design. QUIC addresses this by combining the transport and TLS handshakes into 1 RTT and enabling 0-RTT for resumed connections — the only way to eliminate handshake overhead while maintaining security.

---

### ⚙️ How It Works (Mechanism)

```bash
# Capture the TCP 3-way handshake
tcpdump -nn -i any 'tcp[tcpflags] & (tcp-syn|tcp-ack) != 0' \
  and host example.com

# Expected output:
# Client→Server: Flags [S], seq 2893456128, win 65535
# Server→Client: Flags [S.], seq 987654321, ack 2893456129, win 65535
# Client→Server: Flags [.], ack 987654322, win 65535
# [S] = SYN, [S.] = SYN+ACK, [.] = ACK

# Check connection states
ss -tn state syn-sent
ss -tn state syn-recv

# SYN flood mitigation settings
sysctl net.ipv4.tcp_syncookies    # 1 = enabled (default)
sysctl net.ipv4.tcp_max_syn_backlog  # incomplete queue size
sysctl net.ipv4.tcp_syn_retries   # client-side SYN retransmits
sysctl net.ipv4.tcp_synack_retries # server-side SYN-ACK retransmits

# Time a TCP handshake
time curl -o /dev/null -s -w '%{time_connect}' https://example.com
# time_connect = time until TCP connection established

# Full timing breakdown
curl -o /dev/null -s -w \
  "DNS: %{time_namelookup}\nConnect: %{time_connect}\nTLS: %{time_appconnect}\nFirst byte: %{time_starttransfer}\n" \
  https://example.com
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  TCP 3-Way Handshake + Data Transfer Timeline  │
└────────────────────────────────────────────────┘

 Client                              Server
 
 t=0ms:    SYN →
 [CLOSED → SYN_SENT]              [LISTEN → SYN_RECEIVED]
 
 t=100ms:                         ← SYN-ACK
 [SYN_SENT → ESTABLISHED]
 
 t=100ms:  ACK →                  [SYN_RECEIVED → ESTABLISHED]
           GET /index.html →      ← HTTP 200 OK + data
 
 t=200ms:                         ← (more data)
 
 [First byte received at 200ms = 2 RTTs after initiating]
 [Handshake consumed 1.5 RTTs = 150ms]

 ════════════════════════════════════
 
 COMPARE: TCP connection reuse
 
 t=0ms:    GET /second.html →    (reusing ESTABLISHED conn)
 t=100ms:                        ← HTTP 200 OK + data
 
 [First byte at 100ms = 1 RTT — no handshake cost!]
 [Savings: 100ms (1 RTT) per request vs new connection]
```

---

### 💻 Code Example

**Example — Measuring TCP handshake time:**
```python
import socket
import time

def measure_tcp_connect(host: str, port: int) -> float:
    """Measure time to complete TCP 3-way handshake.
    Returns time in milliseconds.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    # Resolve DNS first (separate from TCP timing)
    addr_info = socket.getaddrinfo(host, port, socket.AF_INET,
                                    socket.SOCK_STREAM)[0]
    server_addr = addr_info[4]
    
    start = time.perf_counter()
    # connect() blocks until 3-way handshake completes
    sock.connect(server_addr)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    sock.close()
    return elapsed_ms

# Measure handshake to multiple targets
targets = [
    ('1.1.1.1', 443),       # Cloudflare (anycast — close)
    ('8.8.8.8', 443),       # Google DNS
    ('example.com', 443),   # example.com
]

for host, port in targets:
    try:
        ms = measure_tcp_connect(host, port)
        print(f"{host}:{port} TCP handshake: {ms:.1f}ms")
    except Exception as e:
        print(f"{host}:{port} failed: {e}")

# Output example:
# 1.1.1.1:443 TCP handshake: 12.3ms
# 8.8.8.8:443 TCP handshake: 15.7ms
# example.com:443 TCP handshake: 89.2ms
```

---

### ⚖️ Comparison Table

| Aspect | TCP Handshake | QUIC Handshake | TLS 1.3 (atop TCP) |
|---|---|---|---|
| RTTs | 1.5 RTTs | 1 RTT (first) | 1 RTT (TLS) atop TCP |
| 0-RTT resumption | No | Yes | Yes (TLS 0-RTT) |
| Security included | No (separate TLS) | Yes | Separate step |
| SYN flood risk | Yes (mitigated by SYN cookies) | Less (UDP-based) | Same as TCP |
| Connection ID | No (4-tuple) | Yes (migration) | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The handshake takes 3 RTTs | The handshake takes 1.5 RTTs — SYN takes 0.5 RTT to arrive, SYN-ACK takes 0.5 RTT back (1 RTT total), ACK is sent but client doesn't wait for a response (0.5 RTT). Client can send data immediately after ACK |
| The ACK in step 3 is the third "round trip" | The ACK (step 3) and first data bytes can be sent in the same packet (piggybacking); the server receives both together |
| SYN cookies break TCP | SYN cookies are fully transparent — clients never know the server used them; they only limit some TCP options (e.g., window scaling) which is a minor trade-off |
| A single TCP connection can be reused forever | TCP connections can be kept alive but servers often set a maximum idle timeout; HTTP/1.1 `Keep-Alive: timeout=65` sets 65s idle limit |

---

### 🚨 Failure Modes & Diagnosis

**SYN Flood / SYN_SENT Hanging**

**Symptom:**
Application hangs on `connect()`. `ss -tn` shows connection stuck in `SYN_SENT` for many seconds.

**Root Cause:**
Server not responding to SYN: server is down, network is dropping SYN packets, or firewall is blocking SYN-ACK responses.

**Diagnostic Commands:**
```bash
# Check for connections stuck in SYN_SENT
ss -tn state syn-sent
# If many: network issue to destination

# Trace packets to see if SYN is sent and if SYN-ACK returns
tcpdump -nn host <destination-ip> and tcp

# Check SYN retransmission count
ss -tn -o | grep <destination>
# Look for: timer:(on,Xs,N) where N = retransmit count

# Server-side: check SYN_RECV queue overflow
ss -tn state syn-recv | wc -l
# If high: SYN flood or accept() backlog full

# Check dropped SYN due to backlog overflow
netstat -s | grep "SYNs to LISTEN"
# "X SYNs to LISTEN sockets dropped"

# Server-side SYN queue tuning
sysctl -w net.ipv4.tcp_max_syn_backlog=4096
sysctl -w net.core.somaxconn=4096
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `TCP` — the handshake is part of TCP's connection lifecycle; TCP basics are prerequisite
- `TCP/IP Stack` — the handshake operates at Layer 4

**Builds On This (learn these next):**
- `TCP Teardown` — the complementary FIN process that closes connections
- `TLS/SSL` — TLS handshake happens after the TCP handshake; together they add 2+ RTTs before data
- `Congestion Control` — after the handshake, TCP starts Slow Start; understanding both explains initial connection performance

**Alternatives / Comparisons:**
- `QUIC` — combines transport + TLS handshake into 1 RTT; 0-RTT for resumed connections

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 3-step process to establish TCP connection│
│              │ SYN → SYN-ACK → ACK                      │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ 1.5 RTTs (SYN sent, SYN-ACK returns,     │
│              │ ACK + first data sent together)           │
├──────────────┼───────────────────────────────────────────┤
│ PURPOSE      │ Sync ISNs; verify reachability both ways; │
│              │ allocate connection state                 │
├──────────────┼───────────────────────────────────────────┤
│ COST         │ 100ms RTT = 150ms wasted per new conn;    │
│              │ reuse connections to amortise this        │
├──────────────┼───────────────────────────────────────────┤
│ SYN FLOOD    │ Mitigated by SYN cookies                  │
│              │ (net.ipv4.tcp_syncookies = 1)             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Can you hear me? / Yes, can you? / Yes." │
│              │ Minimum to prove bidirectional comms work │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TCP Teardown → TLS handshake → QUIC 0-RTT │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservices architecture makes 1000 upstream HTTP calls per second to a backend service, each on a new TCP connection (no connection pooling). The RTT between services is 2ms. Calculate: (a) the total milliseconds wasted on TCP handshakes per second, (b) what percentage of a 10ms request SLA is consumed by the handshake, (c) how many TCP connections per second need to be created at the OS level, and (d) the complete set of OS-level changes and application-level changes you would make to eliminate this overhead.

**Q2.** Explain SYN flood attacks and their mitigation in detail: (a) how a SYN flood works (spoofed source IPs, server state allocation), (b) why the incomplete SYN queue fills (SYN_RECEIVED state per half-open connection), (c) exactly how SYN cookies encode connection state (ISN = hash of 5-tuple + time + secret), (d) the trade-off of SYN cookies (which TCP options become unavailable), and (e) how `tcp_syncookies = 2` (always-on) differs from `tcp_syncookies = 1` (enabled under load).
