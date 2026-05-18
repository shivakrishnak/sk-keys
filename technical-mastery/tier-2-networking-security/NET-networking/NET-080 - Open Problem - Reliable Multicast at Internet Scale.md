---
id: NET-080
title: "Open Problem - Reliable Multicast at Internet Scale"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★★
depends_on: NET-028, NET-079
used_by: NET-083
related: NET-028, NET-079, NET-083
tags:
  - networking
  - multicast
  - open-problem
  - distributed-systems
  - research
  - ip-multicast
  - gossip
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/net/open-problem-reliable-multicast-at-internet-scale/
---

**⚡ TL;DR** - Reliable multicast is an unsolved hard
problem: how do you send one message to N recipients
with delivery guarantees, without N separate TCP
connections? IP multicast exists but scales poorly and
isn't supported across internet routing domains. The
practical solutions (gossip protocols, CDN replication,
Kafka consumer groups) are workarounds, not true
multicast. This entry explores why the problem is hard,
what existing approaches fail at, and where current
research and practice meet.

| #080 | Category: Networking | Difficulty: ★★★★★ |
|:---|:---|:---|
| **Depends on:** | BGP Border Gateway Protocol (NET-028), Congestion Control Theory (NET-079) | |
| **Used by:** | Networking Career Paths (NET-083) | |
| **Related:** | BGP, Congestion Control Theory, Networking Career Paths | |

---

### 🔥 Why This Problem Is Hard

```
Unicast (TCP): 1 sender → 1 receiver
  Well-solved: TCP provides reliability, ordering, flow control
  Scale: 1 connection per recipient = O(N) connections
  At 1,000,000 recipients: 1M TCP connections from one sender
  Not viable
  
IP Multicast: 1 sender → multicast group (many receivers)
  One packet: routers copy at branching points
  Receiver: subscribes to group address (IGMP)
  Sender: sends once → network does the copying
  
  Scale: network-level efficiency
  
  Problem 1: Reliability
  UDP multicast: no ACK per receiver
  How does sender know all N receivers got the packet?
  N receivers × ACK = N ACKs to sender (ACK implosion)
  
  Problem 2: State at routers
  Every multicast group: router must store group state
  At internet scale (billions of groups): impossible for routers
  Result: IP multicast is only deployed within single AS domains
          (within an organization, not across the internet)
  
  Problem 3: Flow control
  Different receivers: different network speeds
  Fast sender → some receivers fall behind
  TCP: flow control per connection (easy)
  Multicast: how do you slow down without slowing down everyone?
```

---

### ⚙️ Approach 1 - IP Multicast (Works Within Networks)

```
How IP multicast works:
  Multicast address: Class D (224.0.0.0 - 239.255.255.255)
  Receiver: sends IGMP Join to local router (interest in group)
  Router: builds multicast distribution tree
  Sender: sends UDP packet to multicast group address
  Network: router copies packet at each tree branch
  
PIM (Protocol Independent Multicast):
  PIM-SM (Sparse Mode): used for internet-scale groups
  Rendezvous Point (RP): central meeting point for senders/receivers
  Source tree: SPT (Shortest Path Tree) from source to receivers
  
  Deployment today:
  Within ISP: live TV over IPTV, financial market data feeds
  Financial: stock exchanges send market data via multicast
             1 feed → thousands of traders receive
             
  Not deployed: between different AS (BGP domains)
  Each AS: would need to participate in interdomain multicast
  Requires: coordination between ISPs
  Not done: business and technical complexity
  
Where IP multicast is used today:
  IPTV: within ISP network (telco TV distribution)
  Trading: NYSE, NASDAQ market data (within co-location)
  Gaming: some LAN games use multicast for discovery
  Corporate: enterprise internal video distribution
  
  Not used: Netflix, YouTube, CDNs (use unicast with HTTP)
```

---

### ⚙️ Approach 2 - Gossip Protocols

```
Gossip (epidemic) protocols: probabilistic multicast
  Sender: sends message to K random peers
  Each peer: forwards to K random different peers
  Propagation: exponential → entire network in O(log N) rounds
  
  Example with N=1,000, K=3:
  Round 1: 1 node tells 3 others → 4 nodes know
  Round 2: 4 nodes each tell 3 → ~16 nodes know
  Round 3: ~64 nodes know
  Round 10: ~1,000 nodes know (log₃(1000) ≈ 6 rounds)
  
Properties:
  Probabilistic: not 100% reliable (some nodes may be missed)
  Self-healing: node failure doesn't stop propagation
  Decentralized: no single root of failure
  Overhead: each message copies K times at each hop
             Total: O(N log N) messages (not O(N))
  
Use in distributed systems:
  Cassandra: gossip for cluster membership (which nodes are alive)
  Consul: gossip for service discovery
  Kubernetes: etcd raft = consensus variant, not pure gossip
  Bitcoin: gossip for transaction propagation
  
Reliability tradeoff:
  Pure gossip: probabilistically reliable
  For 99.999% delivery: increase K, add multiple rounds
  Storage: remember which messages you've seen (dedup)
  
Practical limits:
  Message size: gossip works for small metadata, not large data
  Large data: gossip for notification, unicast for data transfer
```

---

### ⚙️ Approach 3 - Application-Level Multicast

```
Application-level multicast:
  Build multicast tree in application layer
  Don't rely on IP multicast
  Receivers connect to a tree of intermediate nodes
  
Example: live video distribution
  Broadcaster → CDN Edge PoP (100 PoPs)
  CDN Edge → 10,000 subscribers each
  Total: 100 × 10,000 = 1,000,000 viewers
  
  Efficient: broadcaster sends once to CDN origin
  CDN: replicates to 100 PoPs, each PoP to viewers
  
  This IS application-level multicast, just done by CDN infrastructure
  
Kafka consumer groups (a form of multicast):
  Producer → Kafka partition (1 write)
  Consumer group A: reads each message once
  Consumer group B: reads same messages independently
  
  Multicast: multiple consumer groups independently consume same messages
  Guaranteed delivery: at-least-once per consumer group
  Not IP multicast: Kafka handles replication (N followers per partition)
  
BitTorrent (receiver-driven multicast):
  Sender: divides file into chunks
  Receivers: download different chunks from each other
  As more download: more sources for others to download from
  
  "Swarm": N receivers cooperate to distribute to each other
  Scales: more receivers = more bandwidth available
  The more popular, the faster the download
  
Challenges of app-level multicast:
  Intermediate nodes: require compute/bandwidth resources
  Who pays? (CDN charges by egress)
  Reliability: still need ACK/NACK per receiver at application level
```

---

### ⚙️ Approach 4 - Reliable Multicast Protocols (Research)

```
Several protocols attempt "true" reliable multicast:

PGM (Pragmatic General Multicast, RFC 3208):
  Uses: NAK (Negative ACK) instead of ACK
  Receiver: NACK when packet is missing (not ACK for every packet)
  Benefit: N receivers × 1 NACK each (if 1 packet lost) vs N ACKs
  NACK suppression: if you hear someone else's NACK → don't send yours
  
  Congestion still unsolved: different receivers, different speeds
  
SRM (Scalable Reliable Multicast):
  File transfer over IP multicast
  Uses: NACK with randomized exponential backoff
  Avoids: NACK implosion (random delay before sending NACK)
  
NACK implosion problem:
  1,000,000 receivers, 1 packet lost:
  All 1M receivers: detect loss → all send NACK simultaneously
  Sender: receives 1M NACKs at once (implosion)
  Solution: NACK suppression (hear first NACK → cancel yours)
  
  With suppression: sender receives ~K NACKs (O(1) or O(log N))
  Not solved: what K is in practice under different conditions
  
Current research areas:
  FEC (Forward Error Correction): add redundant packets
    Receiver: recovers from N-K lost packets without retransmit
    Cost: bandwidth overhead for redundant packets
    
  AL-FEC (Application-Layer FEC): used in broadcast
    DVB broadcast: sender adds 20% redundant data
    Receiver: recovers up to 20% loss without requesting retransmit
    
  RLNC (Random Linear Network Coding):
    Receivers: send combinations of received packets to others
    Network: becomes self-healing multicast
    Theoretical optimality, but practical overhead
```

---

### ⚙️ Why It Remains Unsolved

```
The fundamental tension:
  Reliability requires acknowledgment (receiver → sender)
  Multicast scales by eliminating per-receiver state
  These conflict
  
For N receivers:
  Every receiver acknowledges → O(N) ACKs (defeats purpose)
  No acknowledgment → sender doesn't know who got the message
  
NACK approach:
  Only notify on failure → reduces feedback
  But: need 100% coverage (silent receiver = unknown state)
  "Silence = success" assumption: requires reliable detection of loss
  
Heterogeneous receivers (the slow receiver problem):
  1 receiver at 1 Mbps, 999 at 1 Gbps
  Multicast rate: limited by slowest receiver
  OR: fastest receivers race ahead, slowest falls behind
  
  Solution approaches:
    Layer multicast: base layer + enhancement layers
    Slow receivers: subscribe to base layer only
    Fast receivers: subscribe to all layers
    
    Practical: used in scalable video coding (SVC)
    Still partial: no clean solution for arbitrary heterogeneity
    
The deployment problem (even if protocol solved):
  ISPs: must enable PIM multicast on all routers
  No business model: who pays for the infrastructure?
  Security: multicast groups difficult to authenticate
  Anycast DNS: solves one-to-nearest, not one-to-many
  
The practical answer (2024):
  For web-scale multicast: CDN + HTTP + adaptive bitrate
  For internal systems: Kafka, pub/sub
  For small trusted networks: IP multicast
  "True" internet-scale reliable multicast: open problem
```

---

### 📐 Scale Analysis

```
Why scale changes everything in multicast:

100 receivers:
  ACK implosion: manageable (100 ACKs)
  IP multicast: works within a single network
  App-level: easy (100 TCP connections possible)
  
10,000 receivers:
  ACK implosion: difficult (10,000 simultaneous ACKs)
  IP multicast: starts straining router state
  App-level: 10,000 TCP connections from one server: challenging
  Solution: CDN (2 tiers = 100 edges × 100 per edge)
  
1,000,000 receivers:
  ACK implosion: impossible without NACK + suppression
  IP multicast: breaks (router state, cross-ISP coordination)
  App-level: impossible from single origin
  CDN: 1,000 PoPs × 1,000 viewers each = practical
  
Gossip at 1,000,000:
  K=3, log₃(1,000,000) = 12 rounds
  12 × 1,000,000 × 3 = 36,000,000 messages total
  At 100ms per round: 1.2 seconds for propagation
  Acceptable for eventual consistency, not for real-time stream
  
The "broadcast" problem (all receivers, exact timing):
  Live event: 1,000,000 viewers exactly at kickoff
  TCP at 1M: 1M handshakes simultaneously = TCP SYN storm
  HTTP CDN: each viewer → nearest CDN PoP → origin
             PoP caches → absorbs the storm
  This is why CDNs are the practical answer
```

---

### 🧭 Decision Guide

```
For practical networking problems, choose:

Need to send data to many consumers independently:
  → Kafka topic: multiple consumer groups, replay, durable
  
Need real-time notification to many clients:
  → Pub/sub: Redis Pub/Sub, NATS, GCP Pub/Sub
  → Gossip: for internal service mesh metadata
  
Need to distribute large files/content:
  → CDN (Cloudflare, CloudFront): app-level multicast at scale
  
Need low-latency market data to many traders:
  → IP multicast (within co-location network)
  → Not over internet
  
Need to distribute video live streaming:
  → CDN + HLS/DASH (adaptive bitrate): proven at billions of users
  → RTMP origin → CDN edge → HTTP to viewers
  
Studying for interviews:
  Know: why IP multicast isn't deployed on the internet
  Know: gossip protocols for distributed system metadata
  Know: Kafka/pub-sub as practical multicast alternatives
  Know: CDN as application-level multicast for content
  
If an interviewer asks "can you do reliable multicast at scale?":
  Correct answer: "It's an open problem. In practice, we use
  CDN for content, pub/sub for events, Kafka for stream
  processing, and gossip for cluster metadata. True
  internet-scale reliable multicast requires solutions to
  the NACK implosion, heterogeneous receiver, and cross-ISP
  deployment problems - none of which are fully solved."
```