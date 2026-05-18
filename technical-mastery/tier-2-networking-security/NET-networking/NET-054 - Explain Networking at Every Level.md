---
id: NET-054
title: "Explain Networking at Every Level"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-003, NET-030, NET-044
used_by: NET-067
related: NET-003, NET-030, NET-044, NET-067
tags:
  - networking
  - explanation
  - mental-models
  - interviews
  - communication
  - tcp-ip
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/net/explain-networking-at-every-level/
---

**⚡ TL;DR** - "Explain how the internet works" is a
classic interview question. The right answer adapts to
the audience. For a child: postal letter analogy. For
a PM: request-response with routing. For a junior dev:
TCP/IP layer walk-through with DNS and HTTP. For a
senior dev: packet journey with TCP handshake, TLS,
multiplexing, and routing tables. This entry gives you
all four levels and a complete technical walk-through of
"what happens when you type a URL and press Enter."

| #054 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | How Does DNS Work (NET-003), How HTTP Works (NET-030), TLS Handshake Deep Dive (NET-044) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067) | |
| **Related:** | How Does DNS Work, How HTTP Works, TLS Handshake Deep Dive, Networking Deep-Dive Interview Questions | |

---

### 🔥 The Interview Problem

"Explain what happens when you type google.com and press Enter." This question tests breadth (do you know all the layers?) and depth (can you go deep on any layer?). The best answers tell a story, ask what level of detail the interviewer wants, and go progressively deeper when prompted. One-sentence answer vs five-minute walk-through.

---

### 🧠 Level 1 - For a Child (Analogy)

```
"Imagine you want to send a letter to a friend.
 You write the letter (your message/request).
 You put it in an envelope with their address (IP address).
 The post office figures out the route (routing).
 Other post offices pass it along until it arrives (hops).
 Your friend reads it and sends a letter back (response).
 
 The internet is like a giant postal system for computers.
 Instead of letters, it sends small packets of data.
 Instead of one letter, big files are cut into many
 small envelopes and put back together on arrival."
```

---

### 🧠 Level 2 - For a Product Manager

```
"You type google.com. Three things happen:

 1. Finding the address (DNS):
    Your browser doesn't know where google.com lives.
    It asks a DNS server (like a phone book):
    'What is the IP address for google.com?'
    Gets back: '142.250.80.14'
    Now it knows where to send the request.

 2. Sending the request (HTTP):
    Your browser sends: 'GET /search?q=cats HTTP/1.1'
    to Google's servers. This request travels through
    multiple network devices (routers) to reach Google.

 3. Getting the response:
    Google's server processes the request and sends back
    the HTML, images, and scripts for the page.
    Your browser assembles them into the page you see.

 Why it feels instant:
    All of this takes ~200ms for a local server,
    or ~500ms for a server across the world.
    Networks are fast - data travels at ~200,000 km/s."
```

---

### 🧠 Level 3 - For a Junior Developer

```
"Step-by-step from URL to page load:

 1. DNS Resolution
    Type: google.com
    OS checks: /etc/hosts (local override)
    Check: local DNS cache (browser + OS)
    If miss: query DNS resolver (usually your ISP or 8.8.8.8)
    DNS resolver asks: root → .com TLD → google authoritative
    Returns: 142.250.80.14 (and caches for TTL seconds)

 2. TCP Connection
    Browser opens TCP connection to 142.250.80.14:443
    3-way handshake: SYN → SYN-ACK → ACK
    Takes 1 RTT (round-trip time) = ~10ms same country

 3. TLS Handshake (since HTTPS)
    Browser and server exchange cryptographic keys
    Server sends certificate (proves it's actually Google)
    Browser verifies certificate chain up to trusted root CA
    Session keys established
    Takes 1-2 RTT (TLS 1.3 = 1 RTT, TLS 1.2 = 2 RTT)

 4. HTTP Request
    Browser sends: GET / HTTP/1.1
    Headers: Host: google.com, Cookie: ..., Accept: text/html
    Server processes and sends back HTML response

 5. Parsing and Rendering
    Browser parses HTML, discovers CSS/JS/image URLs
    Opens parallel connections for each resource
    Renders page progressively as resources arrive"
```

---

### ⚙️ Level 4 - Complete Technical Walk-Through

```
User types: https://google.com and presses Enter

=== PHASE 1: DNS Resolution ===

Browser cache: check for google.com TTL hit
  - Hit: use cached IP, skip DNS
  - Miss: ask OS resolver

OS resolver: /etc/nsswitch.conf (files then DNS)
  1. /etc/hosts lookup: 127.0.0.1 localhost, ...
  2. stub resolver: ask 127.0.0.53 (systemd-resolved)

Recursive resolver (8.8.8.8 or ISP):
  1. Ask root nameserver: "who handles .com?"
     Root returns: a.gtld-servers.net (TLD nameserver)
  2. Ask TLD nameserver: "who handles google.com?"
     TLD returns: ns1.google.com (authoritative nameserver)
  3. Ask authoritative nameserver: "IP for google.com?"
     Returns: 142.250.80.14, TTL 300

Note: actual Google has ANYCAST - 142.250.80.14 routes
to nearest Google PoP, not a single server


=== PHASE 2: TCP Connection ===

OS creates socket, selects ephemeral port (e.g., 54321)
tcpdump view:
  10.0.0.1.54321 > 142.250.80.14.443: Flags [S], seq N
  142.250.80.14.443 > 10.0.0.1.54321: Flags [S.], seq M, ack N+1
  10.0.0.1.54321 > 142.250.80.14.443: Flags [.], ack M+1

TCP handshake: SYN (client says hello + initial seq number)
              SYN-ACK (server responds + own seq number)
              ACK (client acknowledges)
TCP connection is ESTABLISHED after 1 RTT


=== PHASE 3: TLS 1.3 Handshake ===

(TLS 1.3: combined with first data, 1 RTT total)

ClientHello:
  - Supported TLS version: 1.3
  - Cipher suites: [TLS_AES_256_GCM_SHA384, ...]
  - Client random: 32 bytes
  - Key share: Diffie-Hellman public key (for server too)
  - SNI extension: server_name = "google.com"
    (critical for virtual hosting on shared IPs)

ServerHello + Certificate + Finished:
  - Selected cipher: TLS_AES_256_GCM_SHA384
  - Server random: 32 bytes
  - Server's DH public key
  - Certificate: google.com, signed by Google Internet Authority
  - Certificate chain: root CA (trusted by browser trust store)
  - Finished: HMAC over entire handshake

Client verifies certificate:
  - Signature valid for google.com?
  - Not expired?
  - Not revoked? (OCSP stapling check)
  - Chain leads to trusted root CA?

Session keys derived:
  Handshake traffic secret → Application traffic secret
  Both sides have the same keys (from DH key exchange)
  Without the private key, passive observer can't decrypt

Client Finished + First Request (1.5-RTT effectively):
  First GET request can be sent immediately after ClientHello
  (0-RTT mode in TLS 1.3, but has replay risks for non-GET)


=== PHASE 4: HTTP/2 Request ===

HTTP/2 over TLS (ALPN negotiated in TLS handshake):
  Binary framing instead of text
  Stream 1: GET /
    HEADERS frame:
      :method: GET
      :scheme: https
      :path: /
      :authority: google.com
      accept: text/html
      cookie: [...]
    (HPACK compressed: repeated headers not retransmitted)

Server response (stream 1):
  HEADERS frame: :status 200, content-type: text/html
  DATA frames: HTML body (chunked or single)

HTTP/2 multiplexing:
  Browser opens streams 3, 5, 7, ... for discovered resources
  All share ONE TCP connection
  (HTTP/1.1 would need 6 parallel connections)


=== PHASE 5: IP Routing and Packet Journey ===

Each TCP segment is wrapped in:
  TCP header: src port, dst port, seq/ack, flags, checksum
  IP header: src IP, dst IP, TTL, protocol=6 (TCP)
  Ethernet frame: src MAC, dst MAC (next-hop router)

Packet leaves your machine → home router (gateway)
  Router decrements TTL (prevents infinite loops)
  Router looks up 142.250.80.14 in routing table
  Forwards to ISP router

ISP router → Internet backbone (BGP routing)
  BGP: routers share which IP ranges they can reach
  Packet follows most-specific route (longest prefix match)
  3-20 hops to destination (traceroute shows each)

Arrives at Google's PoP → load balancer → server
  Reverse path: server → LB → Google router → Internet → your machine


=== END-TO-END TIMELINE ===

Event                    Time (same country, ~20ms RTT)
DNS resolution           ~20ms (if resolver needs to query)
TCP handshake            ~20ms (1 RTT)
TLS 1.3 handshake        ~20ms (1 RTT combined with TCP in optimized case)
HTTP request/response    ~20ms (1 RTT for first response)
Total first byte:        ~80ms
Full page load:          200-500ms (parallel resource loading)
```

---

### ⚙️ Wrong vs Right: Interview Pitfalls

```
BAD: "The browser sends a request to the server."
  Too vague - skips all the interesting parts
  Interviewer: "Can you go deeper?"

BAD: "TCP/IP handles everything."
  Shows memorized acronym without understanding
  Can't explain the layers individually

GOOD: Structured story with decision points
  1. "First, we need to resolve the hostname to IP..."
  2. "Then we establish a TCP connection..."
  3. "Then TLS negotiation..."
  4. "Then HTTP request..."
  
  Bonus: "I can go deeper on any of these layers"
  This shows you know there's more depth available

BEST: Add the "why" at each step
  "DNS TTL is short because Google uses anycast - the same
  IP needs to route to different PoPs depending on location"
  "TLS 1.3 reduced to 1-RTT from 1.2's 2-RTT by sending
  the key share in the ClientHello"
  "HTTP/2 multiplexes on one TCP to avoid TCP HOL blocking
  that HTTP/1.1 had with parallel connections"
```

---

### 📐 Scale Considerations

```
What changes at Google's scale (billion users):

DNS:
  Not a single server - anycast routing to nearest PoP
  8.8.8.8 is an anycast address, not one machine
  TTLs tuned: 300s for most, short during migrations

TCP:
  Millions of concurrent connections to single IP (anycast)
  TCP stack tuned: SO_REUSEPORT, kernel parameters
  BBR congestion control (Google's invention)

TLS:
  Session tickets for 0-RTT resume
  Certificate pinning in apps (additional security)
  TLS termination at edge, plain HTTP internally

HTTP/2 + HTTP/3:
  HTTP/3 (QUIC over UDP) for mobile clients
  Avoids TCP HOL blocking on lossy networks
  0-RTT connection resumption after interruption

Infrastructure:
  Anycast: single IP, 100+ PoPs globally
  BGP routing: each PoP advertises the same IP prefix
  Packet flows to nearest PoP (measured by BGP metric)
  DDoS mitigation: anycast absorbs volumetric attacks
    (traffic distributed across 100+ PoPs)
```

---

### 🧭 Decision Guide

```
Interview adaptations by role:

Backend engineer role:
  Emphasize: TCP connection management, HTTP/2 vs HTTP/1.1,
  connection pooling, TLS overhead, keep-alive

Frontend engineer role:
  Emphasize: DNS prefetch, preconnect hints, HTTP caching,
  CDN, critical rendering path, resource prioritization

Infrastructure/DevOps role:
  Emphasize: DNS TTL strategy, LB health checks, anycast,
  BGP, TLS certificate management, iptables/security groups

System design question:
  "Which parts are bottlenecks at scale?"
  DNS: cached, not bottleneck
  TCP: connection setup cost at scale → connection pooling
  TLS: computation cost → session resumption, hardware offload
  HTTP: bandwidth → compression, CDN for static assets

Depth questions the interviewer might ask:
  "How does DNS caching work?" → TTL, negative caching, NXDOMAIN
  "What is TLS session resumption?" → session tickets, PSK
  "How does HTTP/2 multiplexing work?" → streams, HPACK, flow control
  "What happens if a router goes down?" → BGP convergence, alternate paths
  "How does CDN reduce latency?" → edge cache, anycast, shorter RTT
```