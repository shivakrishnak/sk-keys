---
id: NET-067
title: "Networking Deep-Dive Interview Questions"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-053, NET-062, NET-063
used_by: NET-083
related: NET-053, NET-062, NET-063, NET-083
tags:
  - networking
  - interviews
  - questions
  - deep-dive
  - preparation
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/net/networking-deep-dive-interview-questions/
---

**⚡ TL;DR** - Senior networking interview questions
test whether you understand the WHY behind protocols,
can diagnose failures, and know what changes at scale.
This entry covers 20 deep-dive questions with full
model answers: TCP state machine, TLS internals, DNS
failures, load balancing selection, HTTP/2 vs HTTP/3,
service mesh trade-offs, network debugging methodology,
and production incident analysis. Each answer goes
beyond surface-level to demonstrate production experience.

| #067 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Networking System Design (NET-053), Service Mesh (NET-062), Network Observability (NET-063) | |
| **Used by:** | Networking Career Paths (NET-083) | |
| **Related:** | Networking System Design, Service Mesh, Network Observability, Networking Career Paths | |

---

### 🔥 The Interview Problem

Networking questions differentiate candidates who
understand protocols from those who memorized definitions.
"TCP is connection-oriented" is entry level. "Explain
why TIME_WAIT exists and when you'd tune
tcp_fin_timeout in production" shows you've debugged
real systems. These 20 questions are the ones that
actually appear in senior/staff interviews.

---

### ⚙️ TCP and Transport Layer Questions

**Q1: What happens to a TCP connection when a server process crashes?**

```
The kernel sends RST (Reset) to all open TCP connections
for that process's sockets.

Sequence:
  Server process crashes → kernel cleans up sockets
  For each connected socket: kernel sends RST + FIN
  (Actually: OS sends FIN+ACK if graceful, RST if abrupt)
  
  Client receives RST or FIN
  RST: immediate connection abort → ECONNRESET error
  FIN: graceful close → client reads 0 bytes → closes

In practice:
  kill -9 (SIGKILL): kernel closes socket, sends FIN
  OOM kill: same as kill -9
  Server segfault: kernel sends RST (abrupt)
  
Implication for clients:
  Client must handle: ECONNRESET, ETIMEDOUT, ECONNREFUSED
  Connection pool: detect and remove broken connections
  Use: SO_KEEPALIVE or application-level heartbeat
  Pattern: validate connection before use (testOnBorrow)
```

**Q2: Why does TIME_WAIT exist? When does it cause problems?**

```
Purpose: prevents delayed packets from old connection
reaching a new connection with same src/dst IP:port.

After connection A closes (port 54321):
  If port 54321 immediately reused for connection B
  A delayed packet from A could arrive and be accepted as B
  TIME_WAIT holds port for 2 × MSL = 60-120 seconds

When it causes problems:
  High-throughput services closing many connections/second
  100 RPS × 60 seconds = 6,000 TIME_WAIT sockets
  Port range: 28,231 ports → exhausted at 471 RPS sustained
  
Symptoms: EADDRNOTAVAIL errors under load

Fixes (in order of preference):
  1. Connection reuse: HTTP keep-alive, connection pools
  2. tcp_tw_reuse=1: allow reuse for outbound connections
  3. Expand port range: net.ipv4.ip_local_port_range=1024 65535
  4. Reduce fin_timeout: net.ipv4.tcp_fin_timeout=30
```

**Q3: Explain SYN cookies. What problem do they solve?**

```
SYN flood: attacker sends millions of SYN with spoofed IPs
Server allocates TCB per SYN, waits for ACK
Listen backlog (512-1024) fills → legitimate SYNs dropped

SYN cookies: state in the sequence number
  Server receives SYN: does NOT allocate TCB
  Instead: encodes (timestamp, MSS, IP, port hash) in ISN
  Server sends SYN-ACK with encoded ISN
  
  If real client: sends ACK with ISN+1
  Server: decodes ACK-1 = recovers connection state
  Server: allocates TCB only when ACK arrives (proof of reachability)
  
  Fake SYN with spoofed IP:
  SYN-ACK goes to victim (spoofed IP)
  Victim doesn't know this connection → sends RST
  Server: no ACK arrives, no TCB was allocated → no resource wasted

Trade-offs of SYN cookies:
  Pro: survives SYN floods without exhausting state
  Con: cannot use TCP SACK during handshake phase
       (cookie only holds 5 bits of MSS info)
  Con: first RTT loses some TCP options negotiation
  Net result: mostly invisible, slightly suboptimal in edge cases
  Enable: sysctl net.ipv4.tcp_syncookies=1 (default on Linux)
```

---

### ⚙️ HTTP and Application Protocol Questions

**Q4: How does HTTP/2 multiplexing work? What problem does it solve?**

```
HTTP/1.1 head-of-line (HOL) blocking:
  One request per TCP connection (keep-alive: one at a time)
  Browsers open 6 parallel connections as workaround
  But: 6 connections × TCP overhead = inefficient

HTTP/2 multiplexing:
  Single TCP connection, multiple "streams" simultaneously
  Stream: a sequence of HEADERS + DATA frames
  Frame: binary, includes stream ID
  
  Client sends: stream 1 (GET /api), stream 3 (GET /img),
                stream 5 (POST /data) - all at once
  Server responds: interleaved DATA frames from all streams
  
  HPACK compression: request headers deduplicated
  First request: headers sent in full
  Second request: delta only (e.g., just :path changes)
  
  Does NOT solve TCP HOL blocking:
  A dropped TCP packet stalls ALL streams (TCP reorders in order)
  HTTP/3 (QUIC): per-stream loss recovery solves this
```

**Q5: Why would you choose gRPC over REST? What are the trade-offs?**

```
Choose gRPC when:
  Internal microservices: controlled clients, you own the .proto
  High-throughput: protobuf 2-10x smaller than JSON
  Streaming needed: bidirectional streams in one connection
  Strong contract: .proto is a precise schema, auto-validates

Trade-offs of gRPC:
  Pro: protobuf is smaller, faster to serialize/deserialize
  Pro: HTTP/2 multiplexing (multiple streams in one connection)
  Pro: built-in deadlines, cancellation, status codes
  Pro: code generation in 12+ languages
  
  Con: harder to debug (binary, not human-readable)
       Tools: grpcurl, grpc-gateway, Envoy gRPC-JSON transcoding
  Con: no browser support without gRPC-Web proxy
  Con: more infrastructure (protobuf toolchain, code gen CI)
  Con: versioning requires care (field numbers in .proto)
       Breaking change: removing a field or changing its type
       Safe change: adding new optional field
  
Choose REST when:
  Public API: any client can call without SDK
  Cacheable: HTTP caching, CDN for GET requests
  Browser clients: no gRPC-Web proxy needed
  Simple CRUD: REST is more natural for resource-oriented APIs
```

---

### ⚙️ DNS and Service Discovery Questions

**Q6: What causes "DNS propagation delay"? How long is it, really?**

```
"DNS propagation" is often misunderstood.

What actually happens when you change DNS:
  1. You update record at authoritative nameserver (instant)
  2. TTL on old record: cached by resolvers worldwide
  3. Each resolver keeps cached value for remaining TTL
  4. After TTL expires: resolver queries authoritative again
  
  "Propagation delay" = time for all caches to expire
  
If TTL was 86400 (24 hours):
  Some resolvers cached 23 hours ago → 1 hour to expire
  Some cached 1 hour ago → 23 hours to expire
  "Propagation": up to 24 hours for ALL resolvers to refresh
  
Best practice for migrations:
  1. Lower TTL to 60-300 seconds, 1 hour before change
  2. Verify low TTL is live (dig +short @8.8.8.8 example.com)
  3. Make the DNS change
  4. Wait 300 seconds (or your new TTL)
  5. Roll back TTL to normal (86400 or similar)
  
  With 60s TTL: "propagation" takes ~60 seconds
  With 86400s TTL: up to 24 hours (if you didn't lower TTL)

Negative caching:
  NXDOMAIN (non-existent domain): cached for 1-3 minutes
  SERVFAIL: cached per resolver policy
  Can't "propagate" a removal faster than negative TTL
```

**Q7: A service returns "connection refused" but it's definitely running. Debug this.**

```
Systematic approach:

Step 1: Confirm "running" with ss:
  ss -lntp | grep 8080
  → LISTEN? Means it's listening. What IP?
  127.0.0.1:8080 → only loopback (wrong interface!)
  0.0.0.0:8080 → all interfaces (correct)

Step 2: Confirm connectivity:
  curl -v http://localhost:8080/health  # from same host
  curl -v http://actual_ip:8080/health  # from remote

Step 3: Check firewall:
  sudo iptables -L -n | grep 8080
  # Is there a DROP rule for port 8080?
  
  On AWS: check security group inbound rules
  On K8s: check NetworkPolicy

Step 4: Check binding mismatch:
  Application bound to IPv4 but you're connecting via IPv6?
  ss -lntp6 | grep 8080  # IPv6 listeners
  vs. curl http://[::1]:8080  # IPv6 connection

Step 5: Process is listening but immediate RST:
  Application accepts connection but immediately drops
  → Application-level: check app logs for connection errors
  → TCP queue full: netstat -s | grep overflowed

Step 6: Port forwarding / NAT:
  In Kubernetes: kube-proxy, iptables rules for Service
  kubectl get svc, kubectl describe svc
  kubectl port-forward pod/name 8080:8080 → test directly
```

---

### ⚙️ TLS and Security Questions

**Q8: What is mutual TLS (mTLS)? When do you need it?**

```
Standard TLS:
  Server presents certificate → client verifies
  Client: anonymous (any client can connect)
  Used: public HTTPS websites

mTLS (mutual TLS):
  Server presents certificate → client verifies
  Client ALSO presents certificate → server verifies
  Both sides are authenticated
  
When you need mTLS:
  Microservice-to-microservice (service mesh)
  Machine-to-machine (no human users)
  Zero trust networking (verify identity before access)
  API clients with elevated privileges
  
Implementation (service mesh handles this automatically):
  Istio: issues SPIFFE certificates per service account
    spiffe://cluster.local/ns/prod/sa/payment-service
  Server: verifies client cert AND checks authorization policy
  No application code changes: Envoy sidecar handles it
  
Without mTLS:
  Network can carry traffic from "unknown" sources
  If a pod is compromised: can impersonate any other service
  mTLS: compromised pod can only use its own certificate identity
  
Certificate management for mTLS:
  Short-lived certs (24h): limits blast radius of compromise
  Automatic rotation: service mesh rotates before expiry
  CA: internal PKI (istiod, Vault) not public CA
```

**Q9: Explain TLS 1.3 improvements over TLS 1.2.**

```
TLS 1.2 (2008):
  Handshake: 2 round-trips before data
    RTT 1: ClientHello → ServerHello + Certificate + ServerHelloDone
    RTT 2: ClientKeyExchange + ChangeCipherSpec + Finished
            ← ServerChangeCipherSpec + ServerFinished
    Data: starts on RTT 3
  Total: 3 RTTs to first byte of application data
  Cipher: RSA key exchange (or DHE) - multiple options
  Cipher suite negotiation: client sends list, server picks

TLS 1.3 (2018):
  Handshake: 1 round-trip to first application data
    RTT 1: ClientHello + KeyShare (Diffie-Hellman guess)
            ← ServerHello + EncryptedExtensions + Certificate
              + CertificateVerify + Finished
    Data: starts on RTT 2 (simultaneously with ClientFinished)
    Optimization: 0-RTT for session resumption (replay risk)
  
  Improvements:
    1. 1-RTT handshake (vs 2-RTT in 1.2)
    2. Removed weak cipher suites (RC4, 3DES, export ciphers)
    3. Forward secrecy is MANDATORY (ECDHE only)
       In 1.2: RSA key exchange leaks past sessions if key compromised
       In 1.3: each session has ephemeral keys
    4. Encrypted more of handshake (certificate is encrypted)
       In 1.2: certificate sent in plaintext (SNI exposure)
    5. Removed: RSA key transport, MD5/SHA1, static DH, renegotiation
```

---

### ⚙️ Service Mesh and Infrastructure Questions

**Q10: When would you NOT use a service mesh?**

```
Service mesh is the right answer when:
  > 10 services, multiple languages, compliance needs
  Need canary deployments, circuit breaking, distributed tracing
  Zero trust security model required

When NOT to use:
  Small number of services (< 5):
    Overhead (50-100MB RAM per sidecar) exceeds benefit
    Application-level HTTP client with retry/timeout is sufficient
    
  Team without Kubernetes expertise:
    Service mesh requires deep K8s knowledge
    Debugging mesh issues is complex (Envoy configs, xDS)
    Learn K8s first, mesh later
    
  Non-Kubernetes environments:
    Service mesh assumes K8s or service mesh daemon sets
    VM-based: alternatives are HAProxy, Nginx, Consul Connect
    
  Latency-critical < 1ms paths:
    Envoy adds 0.1-1ms per hop
    High-frequency trading: every microsecond matters
    Cilium (eBPF): lower overhead alternative
    
  Simple architectures:
    Two services talking to each other
    TLS can be configured directly in application
    Retry/timeout in HTTP client library
    
Alternative to full service mesh:
  Linkerd (lighter than Istio): good middle ground
  Envoy as edge proxy only: gateway pattern
  Consul Connect: works with VMs and K8s
  Cilium network policy: eBPF, no sidecar overhead
```

---

### ⚙️ Scale and Performance Questions

**Q11: How would you design a system to handle 1M concurrent WebSocket connections?**

```
Challenge: WebSocket is persistent and stateful
  Each connection: 1 server process/thread holding the socket
  Thread-per-connection: 1M threads × 8MB = 8TB RAM (impossible)
  
Solution: Event-driven architecture with epoll
  Single thread handles many connections via epoll
  Node.js/nginx: proven at 50,000-100,000 per process
  At 1M: 10-20 event-loop processes (one per core)
  
Connection layer design:
  Horizontal scaling: many WebSocket gateway nodes
  Each node: 50,000-100,000 connections with epoll
  1M / 50K per node = 20 gateway nodes
  
State management (the hard problem):
  Message for user A arrives at node where user B is connected
  Need: routing table [user_id → gateway_node_id]
  Options:
    1. Redis pub/sub: all nodes subscribe to all channels
       20 nodes × 1M subscribers × message volume = fan-out
       Better: per-user channel, server subscribes to user's channel
    2. Presence service: user A is connected to node 5
       Route directly to node 5
       
  Sticky sessions (ip_hash): simpler but imbalanced
  
File descriptor limits:
  Default: 1024 per process (ulimit -n)
  Set: ulimit -n 1048576 or /etc/security/limits.conf
  System: sysctl fs.file-max = 2097152 (system-wide max)
  
Message delivery:
  At 1M connections × 1 message/second: 1M msg/sec throughput
  Kafka or Redis Streams: buffer messages, workers deliver
  Partitioned: user_id % N partitions → N delivery workers
```

**Q12: Explain what happens at the network level during a circuit breaker trip.**

```
Circuit breaker states: CLOSED → OPEN → HALF-OPEN

CLOSED (normal operation):
  Every request to upstream: network connection made
  Requests succeed → counter reset
  Requests fail → failure counter increments
  Threshold reached (5 failures in 30s) → trip to OPEN

OPEN (circuit is tripped):
  Network layer: NO connection attempt made
  Circuit breaker: immediately returns error (fail-fast)
  No TCP handshake, no waiting for timeout
  Duration: open for configured interval (e.g., 30s)
  
  Benefit: instead of 10,000 requests each timing out in 30s
  (waiting for TCP timeout), 10,000 requests fail-fast in 1ms
  This prevents: thread pool starvation in caller
  This prevents: cascading failure (slow upstream → caller queues fill)
  
HALF-OPEN (probe state):
  After interval: allow ONE test request through
  Success → close circuit (normal operation resumes)
  Failure → open again (upstream still unhealthy)

Envoy/Istio implementation:
  outlierDetection in DestinationRule
  consecutive5xxErrors: 5 → eject endpoint from load balancing
  ejected endpoint: TCP connections to it stop
  After baseEjectionTime: probe again with 1 request
  
Metric: envoy_cluster_outlier_detection_ejections_active
  Should be near 0 in normal operation
  High value: many backends being circuit-broken
```

---

### ⚙️ Debugging and Diagnosis Questions

**Q13: How do you debug intermittent connection timeouts?**

```
Systematic approach:

1. Characterize the pattern:
   - Always on first request (cold start, DNS cache miss)?
   - Under load (connection pool exhaustion)?
   - Periodic (GC pause? Cron job? Traffic spike)?
   - Geographic (routing issue? DNS for specific region)?

2. Capture with tcpdump:
   sudo tcpdump -i eth0 -n -w /tmp/timeout.pcap "host service_ip"
   Run during next occurrence, then analyze:
   - Did SYN go out? (client sent)
   - SYN-ACK received? (server responded)
   - No SYN-ACK: network issue or server overload
   - SYN-ACK received, then timeout: application not reading

3. Metrics during timeout:
   - TCP retransmit rate: node_netstat_Tcp_RetransSegs
   - Connection establishment failures: AttemptFails
   - Service latency histogram (P99 spike?)
   - JVM: GC pause times (stop-the-world)

4. Check connection pool:
   If connection pool is exhausted: new requests wait
   HikariCP: hikaricp_pending_threads metric
   Pool wait: waiting for available connection → timeout
   Fix: increase pool size, or reduce query time

5. DNS intermittent:
   High DNS TTL: cached until expiry, then miss
   DNS SERVFAIL: intermittent failure of authoritative server
   test: while true; do dig +norecurse svc.cluster.local; sleep 0.1; done
   
6. Load balancer stickiness:
   Round-robin LB: most requests fine
   One backend unhealthy: every 1/N requests fail
   Symptom: ~10% timeout rate (if 1 of 10 backends bad)
   check: LB health check configuration and backend health
```

---

### ⚙️ Architecture Decision Questions

**Q14: When would you use UDP instead of TCP for a service?**

```
Use UDP when:
  1. Latency > reliability
     Examples: video streaming, VoIP, gaming
     Lost frame or voice sample: skip it, continue
     Retransmitting old data: worse than skipping
     
  2. Multicast/broadcast needed
     DHCP, mDNS, PTP (time protocol)
     TCP: point-to-point only; UDP: 1-to-many
     
  3. Stateless short queries
     DNS (mostly): one question, one answer
     TFTP: simple file transfer
     SNMP traps: monitoring events
     
  4. Custom reliability on top
     QUIC (HTTP/3): reliable delivery per-stream, not TCP-wide
     KCP, RUDP: game network protocols
     DTLS: datagram TLS, for UDP applications needing encryption
     
UDP vs TCP decision:
  Need delivery guarantee → TCP (unless you implement your own)
  Need ordering → TCP
  Need flow control → TCP
  Need low latency more than reliability → UDP
  Need multicast → UDP
  Building custom reliability with different semantics → UDP + custom
  
Real-world:
  DNS: UDP (small query/response), falls back to TCP if response > 512B
  QUIC: UDP (own reliability, per-stream)
  Video streaming (live): UDP, bitrate adaptation, skip lost frames
  Video calling (WebRTC): UDP via DTLS + SRTP
  Online gaming: UDP (position updates: old data useless)
  FTP/HTTP: TCP
  SSH: TCP (every character must arrive in order)
```

---

### ⚙️ 6 Additional Quick-Fire Interview Questions

```
Q15: What is SNI and why does it matter?
  Server Name Indication: TLS extension in ClientHello
  Sends hostname in plaintext BEFORE TLS is established
  Allows: one IP to serve multiple TLS certs (virtual hosting)
  Without SNI: need one IP per SSL certificate
  Privacy concern: ISP can see which site you're visiting
  Solution: ECH (Encrypted Client Hello) in TLS 1.3 extensions

Q16: What is BGP and why does a company need its own ASN?
  BGP: routing protocol between autonomous systems (networks)
  Own ASN: needed to announce your own IP address space
  Multi-homed: connect to 2+ ISPs, BGP routes around failures
  Without own ASN: dependent on single ISP's routing
  When needed: > 10 Gbps of bandwidth, multi-datacenter, CDN

Q17: HTTP/3 uses UDP. How does it guarantee delivery?
  QUIC (over UDP) implements its own reliability:
  - Stream-level delivery guarantee (not packet-level)
  - Acknowledgment per stream, not per connection
  - Lost packet: retransmit only affects that stream
  - Unlike TCP: one lost packet doesn't stall ALL streams
  - Congestion control: QUIC implements CUBIC or BBR in userspace

Q18: What is the difference between a reverse proxy and a load balancer?
  Reverse proxy: sits in front of servers, terminates connections
    Handles: TLS, compression, caching, routing
    Examples: nginx, Apache, Envoy
  Load balancer: distributes requests across multiple backend instances
    Handles: health checking, session affinity, algorithms
    Examples: AWS ALB, HAProxy
  In practice: most "load balancers" include reverse proxy features
  nginx: can be both simultaneously

Q19: What is ECMP and when does it matter?
  Equal-Cost Multi-Path: multiple equal-cost routes
  Router: has N paths to same destination, distributes traffic
  Hashing: per-flow (src IP:port + dst IP:port → consistent path)
  Benefit: full bandwidth from multiple links simultaneously
  Risk: hash polarization (most traffic hits one path)
  Where used: data center networks (spine-leaf topology)
  Kubernetes: ECMP on underlying network for multi-path pod traffic

Q20: Why does a firewall need to track connection state?
  Stateful firewall: remembers which connections are established
  Benefits:
    Return traffic allowed automatically (no explicit ALLOW rule)
    Attack protection: only accept responses to established sessions
    TCP reassembly: detects split-tunnel and fragmentation attacks
  Without state: must write rules for both directions
    → Accidentally write "allow all from destination to source"
    → Security hole: anyone can initiate from destination
  iptables CONNTRACK: -m conntrack --ctstate ESTABLISHED,RELATED
  This allows return traffic without overly permissive rules
```