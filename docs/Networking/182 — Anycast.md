---
layout: default
title: "Anycast"
parent: "Networking"
nav_order: 182
permalink: /networking/anycast/
number: "0182"
category: Networking
difficulty: ★★★
depends_on: IP Addressing, BGP, DNS
used_by: CDN, DNS, Networking, Cloud — AWS
related: BGP, DNS, CDN, Load Balancer L4_L7, IP Addressing
tags:
  - networking
  - anycast
  - bgp
  - routing
  - dns
---

# 182 — Anycast

⚡ TL;DR — Anycast assigns the same IP address to multiple servers in different locations, letting BGP routing direct each client to the topologically nearest instance — used by Cloudflare (1.1.1.1), Google (8.8.8.8), DNS root servers, and CDNs to provide low-latency global services with automatic failover at the routing layer.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A global DNS resolver service (1.1.1.1) without Anycast would have one IP pointing to one server location. All 5 billion internet users would query that one location — users in Tokyo would send DNS queries to a datacentre in Ashburn, Virginia (150ms RTT). Worse, if that server fails, the entire service fails.

**THE BREAKING POINT:**
DNS needs sub-millisecond resolution. With a centralised server, users 200ms away experience 200ms+ DNS latency on every uncached lookup. Load balancers in a single datacenter don't help — the RTT from the user to the datacenter is the bottleneck, not the server processing time.

**THE INVENTION MOMENT:**
Anycast uses BGP's path selection to route packets to the "nearest" node announcing a prefix. Every Cloudflare PoP announces 1.1.1.1/32 to its upstream ISPs. A user in Tokyo's ISP sees a BGP path to 1.1.1.1 via Tokyo IXP (5 hops, 5ms) AND via New York (28 hops, 200ms). BGP selects the shorter path. The user's DNS query goes to the Tokyo PoP. Simultaneously, a user in London hits the London PoP. Same IP, different destinations — that's Anycast. If the Tokyo PoP fails, BGP withdraws its prefix announcement; Tokyo ISPs reroute to the next-nearest PoP (maybe Singapore) in under 30 seconds.

---

### 📘 Textbook Definition

**Anycast** is a network addressing and routing method where a single IP address is assigned to multiple nodes and packets are routed to the topologically nearest (by BGP metric) node announcing that address. Contrast with: **Unicast** (one-to-one), **Broadcast** (one-to-all on a network), **Multicast** (one-to-many group). Anycast works by each PoP announcing the same IP prefix to its BGP peers. BGP's path selection (AS path length, local preference, MED) routes packets to the PoP with the best BGP path from each vantage point. Used for: DNS resolution (root servers, 1.1.1.1, 8.8.8.8), CDN routing (Cloudflare), DDoS scrubbing, NTP.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Anycast assigns the same IP to servers worldwide — your traffic is automatically routed to the nearest one by BGP, with no DNS TTL delays, no central load balancer, and instant failover when a PoP goes down.

**One analogy:**

> Anycast is like an emergency phone number (911/999/112). No matter where you are in the country, you dial the same number. The phone network automatically connects you to the nearest emergency centre. You don't need to know the specific number of your local fire station — the infrastructure routes you there. If your local emergency centre is overwhelmed, calls re-route to the next nearest. Same number, different destinations based on where you call from.

**One insight:**
BGP Anycast has no "sticky sessions" — a long-lived TCP connection from one client always hits the same PoP (routed consistently), but UDP traffic (DNS) may route to different PoPs as network conditions change. This is why Anycast is ideal for stateless protocols (DNS, NTP, UDP-based DDoS scrubbing) and why CDNs that use Anycast for routing still need stateful session handling within each PoP.

---

### 🔩 First Principles Explanation

**HOW ANYCAST ROUTING WORKS:**

```
┌─────────────────────────────────────────────────────┐
│  Anycast IP: 1.1.1.1/32                            │
└─────────────────────────────────────────────────────┘

BGP announcements:
  Tokyo PoP  → announces 1.1.1.1/32 to Tokyo IXP
  London PoP → announces 1.1.1.1/32 to London IXP
  New York PoP → announces 1.1.1.1/32 to NY IXP
  Sydney PoP → announces 1.1.1.1/32 to Sydney IXP

Internet routing tables (partial):
  Tokyo ISP:
    1.1.1.1/32 → via Tokyo IXP (2 hops) ← BGP picks this
    1.1.1.1/32 → via NY (18 hops)
    1.1.1.1/32 → via London (22 hops)

  London ISP:
    1.1.1.1/32 → via London IXP (2 hops) ← BGP picks this
    1.1.1.1/32 → via NY (8 hops)
    1.1.1.1/32 → via Tokyo (20 hops)

Result:
  Tokyo user queries 1.1.1.1 → routed to Tokyo PoP
  London user queries 1.1.1.1 → routed to London PoP
  Same IP, different physical destinations
```

**BGP PATH SELECTION:**
BGP selects paths based on (in order of preference):

1. Highest Local Preference (prefer specific providers)
2. Shortest AS path length (fewer autonomous systems = "closer")
3. Origin type (IGP > EGP > Incomplete)
4. Lowest MED (Multi-Exit Discriminator — hint from peer)
5. eBGP over iBGP
6. Lowest IGP cost to next-hop
7. Lowest router ID (tiebreaker)

For Anycast, AS path length is typically the dominant factor: the nearest PoP (fewer BGP hops) wins.

**ANYCAST FAILOVER:**

```
Tokyo PoP fails:
1. PoP stops announcing 1.1.1.1/32 to BGP peers
2. BGP peers withdraw route
3. Internet routing tables update (BGP convergence: 30-90 seconds)
4. Tokyo-area traffic reroutes to next-best PoP (Singapore: 80ms vs 5ms)
5. No DNS change required, no IP change required

Recovery is automatic — no operator intervention for routing.
BGP convergence is the limiting factor (~30-90 seconds).
```

**ANYCAST vs DNS-BASED LOAD BALANCING:**

```
DNS-based routing:
- Resolves to different IPs per location
- Failover speed: limited by DNS TTL
- Requires DNS TTL change + propagation
- Complex: manage many IPs per service

Anycast:
- Single IP worldwide
- Failover speed: BGP convergence (~30-90s)
- Automatic at BGP level
- Simple: one IP to manage
- Limitation: no application-level routing (not by country, not by cookie)
```

---

### 🧪 Thought Experiment

**SETUP:**
Compare Anycast vs DNS-based routing for a global API service during a PoP failure event.

**ANYCAST FAILURE SCENARIO:**
t=0: Tokyo PoP hardware failure
t=0: PoP stops routing, BGP withdraws 1.1.1.1/32 announcement
t=30s: BGP convergence complete; Tokyo ISPs reroute to Singapore PoP
t=30s: All Tokyo users now hitting Singapore (80ms instead of 5ms)
t=10min: Tokyo PoP restored, BGP re-announces prefix
t=10min+30s: BGP converges; Tokyo users back to Tokyo PoP

**DNS-BASED FAILURE SCENARIO:**
t=0: Tokyo PoP hardware failure
Health check detects failure in 30 seconds
t=30s: Route 53 health check fails
t=30s: Route 53 updates DNS to point to Singapore
BUT: DNS TTL = 60s → Tokyo users keep hitting (dead) Tokyo PoP for up to 60s
t=90s: DNS propagated to most clients (varies by TTL and caching)
Some clients: cached old IP for hours (long TTL caches, CDNs ignoring TTLs)

**CONCLUSION:**
Anycast converges faster for PoP failures (BGP, no TTL issues). DNS-based routing is more flexible (can route by country, user attribute, latency measurement) but has TTL propagation delays.

---

### 🧠 Mental Model / Analogy

> Anycast is like a franchise restaurant with the same address everywhere. There are hundreds of "1 High Street, [City]" addresses worldwide, all with the same brand and menu. When you walk to "1 High Street," you automatically go to the one in your city — you don't know or care that there are identical ones globally. If your local branch burns down, you walk a bit further to the next nearest branch. No one updated your map — the routing "just works" based on proximity.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Anycast lets the same IP address live in many places at once. When your computer sends a request to 1.1.1.1, the internet automatically routes it to the Cloudflare server nearest to you. If that server goes down, your traffic is automatically redirected to the next nearest. This makes services faster (shorter routes) and more resilient (automatic failover).

**Level 2 — How to use it (junior developer):**
As a developer, you mostly consume Anycast services rather than build them. Use 1.1.1.1 or 8.8.8.8 as DNS resolvers — they're anycast, so they're fast from everywhere. Cloudflare CDN and AWS CloudFront/Global Accelerator use Anycast routing. If your company is large enough to own an ASN and IP blocks, you can announce them via BGP from multiple datacenters. For most developers: use a CDN that does Anycast under the hood (Cloudflare) rather than building it.

**Level 3 — How it works (mid-level engineer):**
To set up Anycast: (1) Obtain a CIDR block from an RIR (or use provider-independent IPs); (2) Obtain an ASN (Autonomous System Number); (3) Announce the prefix via BGP from multiple PoPs using the same ASN (or via BGP with prepending to control preference). Key BGP concepts: AS path prepending (add your own AS multiple times to make a path appear longer, reducing its preference — used to "drain" traffic from a PoP before maintenance); MED (Multi-Exit Discriminator, to prefer one entry point over another). Real implementation: BIRDv2 or FRRouting are common open-source BGP daemons. Many cloud providers offer managed Anycast: AWS Global Accelerator, GCP Cloud CDN, Cloudflare Spectrum.

**Level 4 — Why it was designed this way (senior/staff):**
Anycast is elegant precisely because it reuses BGP's existing path selection rather than inventing a new routing protocol. The internet's BGP infrastructure, designed for interdomain routing, becomes a global load balancer for free. The trade-off: BGP convergence time (30-90 seconds) is too slow for some failure scenarios — this is why Anycast is combined with health checking and fast local failover within each PoP. The 13 DNS root server "sets" (a.root-servers.net through m.root-servers.net) use Anycast: the 13 root IP addresses actually represent 1,800+ physical servers in 900+ locations. BGP routes each resolver to the nearest root server instance automatically. This is how the root DNS infrastructure handles billions of queries daily with 13 apparent IP addresses.

---

### ⚙️ How It Works (Mechanism)

```bash
# Verify you're hitting an Anycast IP
# For 1.1.1.1: different traces from different locations
traceroute 1.1.1.1
# From Sydney: hops through Cloudflare Sydney PoP (cbr.1111.cloudflare.com)
# From London: hops through Cloudflare London PoP (lon.1111.cloudflare.com)
# Same destination IP, different actual machines

# Check which Cloudflare PoP you're hitting
curl -s https://1.1.1.1/cdn-cgi/trace | grep colo
# colo=SYD → Sydney PoP

# Check root DNS server locations
dig . NS @a.root-servers.net +short
traceroute a.root-servers.net
# Different routes from different locations = Anycast in action

# BGP looking glass (check routes to an Anycast IP from different ASes)
# https://bgp.he.net/ - search for 1.1.1.1
# https://lg.he.net/ - BGP looking glass across multiple PoPs

# Verify Anycast with Cloudflare trace
curl -s https://cloudflare.com/cdn-cgi/trace | head -10
# ip=X, ts=Y, h=cloudflare.com, visit_scheme=https,
# uag=..., colo=LHR (London Heathrow)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────────────────┐
│  Anycast routing: same IP, nearest PoP                  │
└─────────────────────────────────────────────────────────┘

 Global BGP routing table (simplified):

 Tokyo ISP:    1.1.1.1/32 via [Cloudflare-Tokyo] (5ms)
 London ISP:   1.1.1.1/32 via [Cloudflare-London] (8ms)
 Sydney ISP:   1.1.1.1/32 via [Cloudflare-Sydney] (6ms)
 Chicago ISP:  1.1.1.1/32 via [Cloudflare-Chicago] (12ms)

 User queries (all to 1.1.1.1):
   Tokyo user   → 5ms  → Cloudflare Tokyo
   London user  → 8ms  → Cloudflare London
   Sydney user  → 6ms  → Cloudflare Sydney
   Chicago user → 12ms → Cloudflare Chicago

 PoP failure (Cloudflare Tokyo goes down):
   BGP withdrawal propagates (30-90s)
   Tokyo ISP reroutes: 1.1.1.1/32 → Cloudflare-Singapore (80ms)
   Tokyo user → 80ms → Cloudflare Singapore (degraded, not down)
```

---

### 💻 Code Example

```python
import subprocess
import re

def check_anycast_pop(hostname: str = "1.1.1.1") -> dict:
    """Determine which Anycast PoP you're connected to.
    Works for Cloudflare (1.1.1.1) and similar services.
    """
    import urllib.request, json

    result = {"ip": hostname, "pop": "unknown", "latency_ms": None}

    # For Cloudflare: check colo field
    if hostname in ("1.1.1.1", "cloudflare.com"):
        try:
            with urllib.request.urlopen(
                "https://1.1.1.1/cdn-cgi/trace", timeout=5
            ) as resp:
                data = resp.read().decode()
                for line in data.splitlines():
                    if line.startswith("colo="):
                        result["pop"] = line.split("=")[1]
                        break
        except Exception as e:
            result["error"] = str(e)

    # Measure RTT via ping
    try:
        ping = subprocess.run(
            ["ping", "-c", "3", "-q", hostname],
            capture_output=True, text=True, timeout=10
        )
        # Parse: "round-trip min/avg/max/stddev = 5.2/5.8/6.4/0.5 ms"
        match = re.search(r'(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)',
                         ping.stdout)
        if match:
            result["latency_ms"] = float(match.group(2))  # avg
    except Exception:
        pass

    return result

# Check which DNS PoPs we're closest to
for dns_ip in ["1.1.1.1", "8.8.8.8", "9.9.9.9"]:
    info = check_anycast_pop(dns_ip)
    print(f"{dns_ip}: PoP={info.get('pop','?')} "
          f"latency={info.get('latency_ms','?')}ms")
```

---

### ⚖️ Comparison Table

| Aspect                    | Anycast                  | DNS-based Routing  | GeoDNS             |
| ------------------------- | ------------------------ | ------------------ | ------------------ |
| Routing mechanism         | BGP path selection       | DNS response       | DNS + geo IP DB    |
| Failover speed            | ~30-90s (BGP)            | TTL-dependent      | TTL-dependent      |
| Single IP                 | Yes                      | No (multiple IPs)  | No (multiple IPs)  |
| Application-level routing | No                       | No                 | Limited (geo only) |
| TCP session sticky        | Yes (per path)           | Yes (same IP)      | Yes (same IP)      |
| Use cases                 | DNS, NTP, DDoS scrubbing | APIs, CDN fallback | Regional content   |

---

### ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                                                                                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Anycast load balances evenly    | Anycast routes to the nearest PoP by BGP metrics — if one PoP is near many users, it receives disproportionate traffic. True load balancing requires additional mechanisms within the PoP                |
| TCP doesn't work with Anycast   | TCP works with Anycast because BGP routing for a given connection is stable (packets in the same TCP flow take the same path). Issues arise only if BGP re-routes mid-connection (uncommon but possible) |
| Anycast requires many ASNs      | A single ASN can announce the same prefix from multiple PoPs. This is how Cloudflare and Google run their networks — one ASN, hundreds of PoPs, all announcing the same prefixes                         |
| Anycast is complex to implement | For services built on cloud providers (AWS Global Accelerator, GCP Cloud CDN, Cloudflare), Anycast is a configuration option. DIY Anycast requires an ASN + IP block + BGP routers at each PoP           |

---

### 🚨 Failure Modes & Diagnosis

**BGP Route Flapping: Unstable Anycast Performance**

**Symptom:**
Latency to an Anycast service (DNS, CDN) is inconsistent. Sometimes 5ms, sometimes 200ms. DNS resolution behaves erratically.

**Root Cause:**
BGP route flapping — a PoP is announcing and withdrawing its prefix repeatedly, causing the routing table to oscillate between the nearby PoP and a distant one.

```bash
# Check BGP routes to an IP (via looking glass)
# Use: https://lg.he.net/ or https://bgp.he.net/
# Search for your Anycast IP
# Look for: route flapping, multiple paths with similar metrics

# Measure traceroute stability over time
for i in $(seq 1 10); do
  traceroute -n 1.1.1.1 2>/dev/null | tail -3
  sleep 5
done
# If hop count changes: BGP instability

# Check if route changes are causing TCP resets
# (Anycast path change mid-TCP connection)
tcpdump -nn host 1.1.1.1 and tcp
# RST packets → connection terminated due to path change
```

**Fix:**
BGP route dampening (suppress flapping routes); check PoP health monitoring; contact network provider if upstream BGP peer is flapping.

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `BGP`, `DNS`

**Related:** `BGP` (the mechanism that makes Anycast work), `CDN` (Cloudflare/Fastly use Anycast), `DNS` (root servers and 1.1.1.1/8.8.8.8 are Anycast), `DDoS Protection` (scrubbing via Anycast)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Same IP on many servers; BGP routes to   │
│              │ nearest node by path metrics             │
├──────────────┼───────────────────────────────────────────┤
│ EXAMPLES     │ 1.1.1.1 (Cloudflare DNS), 8.8.8.8 (Google│
│              │ DNS), DNS root servers, CDN edge nodes   │
├──────────────┼───────────────────────────────────────────┤
│ FAILOVER     │ BGP withdrawal → convergence in 30-90s   │
│              │ (faster than DNS TTL for most cases)     │
├──────────────┼───────────────────────────────────────────┤
│ vs DNS-BASED │ Anycast: single IP, BGP routing, no TTL  │
│              │ DNS: multiple IPs, flexible routing      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Same IP everywhere; BGP routes you to   │
│              │ the nearest physical instance"           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Cloudflare operates 300+ PoPs worldwide all announcing the same IP prefixes via BGP. During a major network incident, the Singapore PoP (serving Southeast Asia) loses connectivity. Describe in detail: (a) exactly how BGP detects the failure (keepalive timeouts, hold timers), (b) how BGP withdrawal propagates to Singapore's upstream ISPs and IXPs, (c) what "BGP convergence" means and why it takes 30-90 seconds, (d) where traffic from Singapore users goes after convergence (next-nearest PoP via BGP path selection), (e) the latency impact on Singapore users during and after convergence, and (f) how Cloudflare's internal monitoring detects the rerouting and can accelerate convergence.

**Q2.** The 13 DNS root server "IP addresses" (a.root-servers.net through m.root-servers.net) actually represent ~2,000 physical servers. Explain: (a) how Anycast allows 13 IPs to serve 2,000 locations, (b) why DNS root server traffic is ideal for Anycast (stateless UDP, each query is independent), (c) how the "K-root" server (193.0.14.1, operated by RIPE NCC) is deployed across 40+ PoPs simultaneously, (d) what happens to a DNS query in flight if a root server PoP fails mid-UDP request (vs mid-TCP request — different consequences), and (e) why root server Anycast doesn't cause issues for authoritative delegation (NS record lookups are stateless).
