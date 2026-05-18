---
id: NET-043
title: "DNS Resolution Deep Dive"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-003
used_by: NET-050, NET-055
related: NET-003, NET-048, NET-055
tags:
  - networking
  - dns
  - resolution
  - ttl
  - caching
  - dig
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/net/dns-resolution-deep-dive/
---

**⚡ TL;DR** - DNS resolution traverses a hierarchy of
4 server types: Root → TLD → Authoritative → Resolver.
Understanding this chain explains why DNS propagation
takes hours (TTL-based caching at each tier), why
`dig +trace` is the most useful debugging tool, and why
lowering TTL before a DNS change is critical. DNS is
the first thing to diagnose in any connectivity issue -
most "it's not working" problems are either DNS or TLS.

| #043 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DNS (NET-003) | |
| **Used by:** | Network Performance Testing, Networking System Design Interview Patterns | |
| **Related:** | DNS (NET-003), Network Latency Sources, Networking System Design Interview Patterns | |

---

### 🔥 The Problem This Solves

You updated an A record to point to your new server.
15 minutes later, users in Tokyo still see the old IP.
Users in São Paulo see the new one. Your local machine
sees the new one. Is the DNS change broken? No - each
resolver has its own cache with the old TTL countdown.
Understanding the DNS resolution chain explains why
this happens and how to predict and control it.

---

### 🧠 Intuition: A Delegated Hierarchy

```
DNS is a globally distributed database, delegated:
  ICANN controls the root (.)
  VeriSign controls .com, .net
  Whoever owns the domain controls its records
  Each zone delegates to the next

Resolution: asking each level for the next level's address
  "Where is api.example.com?"
  Root: "I don't know, but .com is at 192.5.6.30"
  .com: "I don't know, but example.com NS is ns1.exampleDNS.net"
  ns1.exampleDNS.net: "api.example.com = 93.184.216.34"
  Done.
```

---

### ⚙️ The Four Server Types

**1. Recursive Resolver (Resolver)**

```
Who: Your ISP, Google (8.8.8.8), Cloudflare (1.1.1.1)
What: Does the full lookup on behalf of clients
How: Caches results per TTL, serves from cache when hot
Config: /etc/resolv.conf on Linux, DHCP-assigned on most systems

Client → Resolver: "What is api.example.com's IP?"
Resolver → Root, TLD, Auth → caches result → replies to client
Resolver cache: TTL countdown from authoritative server
```

**2. Root Nameservers**

```
Who: 13 logical servers (a.root-servers.net through m.root-servers.net)
     Actually 1,500+ physical servers via Anycast routing
What: Know addresses of all TLD nameservers
How: Respond to queries about TLDs (.com, .org, .io, etc.)
TTL: Root zone TTL = 172,800 seconds (48 hours)

Key insight: Root servers are rarely the bottleneck.
They return NS records for TLDs, which are then cached
for 48 hours. Real-world bottleneck is authoritative servers.
```

**3. TLD Nameservers**

```
Who: VeriSign for .com/.net, AFILIAS for .org, etc.
What: Know NS records for all domains in their TLD
How: Return NS records + glue records for authoritative servers
TTL: TLD delegation TTL = 172,800 seconds (48 hours)

Glue records: if NS is ns1.example.com and domain is example.com,
the glue record provides ns1's IP directly
(avoids circular dependency)
```

**4. Authoritative Nameservers**

```
Who: Route53, Cloudflare DNS, your hosting provider
What: The authoritative source for your domain's records
How: Returns actual A, AAAA, CNAME, MX records
TTL: YOU control this (commonly 300-86400 seconds)

This is where you create and manage DNS records.
No caching here - always returns current data.
```

---

### ⚙️ Full Resolution Trace with dig

```bash
# See the entire resolution chain
dig +trace api.example.com A

# Example output:
# . NS a.root-servers.net.     ← Root zone NS record
# . NS b.root-servers.net.
# Received 263 bytes from 8.8.8.8#53(8.8.8.8) in 15ms
#                               ↑ resolver contact
#
# com. NS a.gtld-servers.net.  ← .com TLD NS records
# com. NS b.gtld-servers.net.
# Received 864 bytes from 198.41.0.4#53(a.root-servers.net) in 22ms
#                               ↑ root server contact
#
# example.com. NS ns1.exampledns.net.  ← authoritative NS
# example.com. NS ns2.exampledns.net.
# Received 347 bytes from 192.5.6.30#53(a.gtld-servers.net) in 35ms
#                               ↑ TLD server contact
#
# api.example.com. A 93.184.216.34  TTL 300
# Received 60 bytes from 205.251.196.1#53(ns1.exampledns.net) in 18ms
#                               ↑ authoritative server contact

# Total: root(22ms) + TLD(35ms) + auth(18ms) = 75ms uncached
# Cached (second query): ~1ms (resolver cache hit)
```

---

### ⚙️ DNS Record Types

```
┌──────────────────────────────────────────────────────────┐
│  Record Type Reference                                   │
├────────┬─────────────────────────────────────────────────┤
│ A      │ Domain → IPv4 address                           │
│        │ api.example.com → 93.184.216.34                 │
├────────┼─────────────────────────────────────────────────┤
│ AAAA   │ Domain → IPv6 address                           │
│        │ api.example.com → 2606:2800:220:1:248:1893:25c8 │
├────────┼─────────────────────────────────────────────────┤
│ CNAME  │ Alias → canonical name (follows chain)          │
│        │ www → loadbalancer-123.us-east-1.elb.amazonaws  │
│        │ No other records can coexist with CNAME         │
│        │ Cannot use CNAME at zone apex (example.com)     │
│        │ ALIAS/ANAME records solve zone apex problem     │
├────────┼─────────────────────────────────────────────────┤
│ MX     │ Mail exchange servers (with priority)           │
│        │ example.com MX 10 mail1.example.com             │
├────────┼─────────────────────────────────────────────────┤
│ TXT    │ Text data (SPF, DKIM, verification, DMARC)      │
│        │ "v=spf1 include:_spf.google.com ~all"           │
├────────┼─────────────────────────────────────────────────┤
│ NS     │ Nameserver for a zone                           │
│        │ example.com NS ns1.exampledns.net               │
├────────┼─────────────────────────────────────────────────┤
│ SOA    │ Start of Authority (zone metadata, serial no.)  │
├────────┼─────────────────────────────────────────────────┤
│ PTR    │ Reverse DNS (IP → domain, for mail servers)     │
│        │ 34.216.184.93.in-addr.arpa → api.example.com   │
├────────┼─────────────────────────────────────────────────┤
│ SRV    │ Service record (host + port for discovery)      │
│        │ _http._tcp.example.com SRV 0 5 80 www.example   │
├────────┼─────────────────────────────────────────────────┤
│ CAA    │ Certificate Authority Authorization             │
│        │ Which CAs may issue certs for this domain       │
└────────┴─────────────────────────────────────────────────┘
```

---

### ⚙️ TTL Strategy: Before and After DNS Changes

```
TTL = Time To Live = how long resolvers cache the record

Common TTL values:
  60 seconds   = aggressive, rapid changes possible
  300 seconds  = standard, 5-minute propagation
  3600 seconds = 1-hour, stable records
  86400 seconds = 24-hour, very stable (CDN origins)

Change strategy (Critical Pattern):
  Week before:   Lower TTL from 3600 → 60 seconds
  Change day:    Update the A record → new IP
  Wait 60s:      All caches expire (old TTL already flushed)
  Verify:        dig +short api.example.com @8.8.8.8
                 dig +short api.example.com @1.1.1.1
  After stable:  Raise TTL back to 3600+

BAD: Change A record with TTL = 86400
  Resolvers cache old IP for UP TO 24 hours
  Users stuck on old server for hours
  No control over when they migrate

GOOD: Lower TTL first, wait for it to propagate,
      then change record, then raise TTL again
      Total migration window: 2 × lower_TTL
```

---

### ⚙️ Wrong vs Right: The Zone Apex CNAME Trap

```
# BAD: CNAME at zone apex (example.com, not www.example.com)
# DNS spec prohibits CNAME at apex - it conflicts with SOA and NS
example.com CNAME my-lb.us-east-1.elb.amazonaws.com
# This breaks your entire zone - email (MX), SPF (TXT) all fail

# WHY: CNAME means "use all records from the target domain"
# But example.com needs its own NS and SOA records
# A CNAME there would override them → DNS breaks

# GOOD options for zone apex:
# 1. A record pointing to load balancer IP (if static):
example.com A 1.2.3.4

# 2. ALIAS record (Route53-specific, flattened CNAME):
example.com ALIAS my-lb.us-east-1.elb.amazonaws.com
# Route53 resolves the CNAME at query time and returns A record
# Looks like an A record to resolvers, acts like CNAME

# 3. ANAME record (Cloudflare and others):
# Same concept as ALIAS, varies by DNS provider
```

---

### ⚙️ Diagnosing DNS Problems

```bash
# 1. What does MY resolver return?
dig api.example.com A

# 2. What does a specific resolver see?
dig api.example.com A @8.8.8.8       # Google
dig api.example.com A @1.1.1.1       # Cloudflare
dig api.example.com A @208.67.222.222 # OpenDNS

# 3. Is it propagated? (check multiple resolvers)
for ns in 8.8.8.8 1.1.1.1 9.9.9.9 208.67.222.222; do
    echo -n "$ns: "
    dig +short api.example.com A @$ns
done

# 4. Full delegation trace
dig +trace api.example.com A

# 5. Check authoritative answer (AA flag in response)
dig api.example.com A @ns1.exampledns.net
# Look for "aa" (authoritative answer) in flags section

# 6. TTL remaining on cached entry
dig +nocmd +noall +answer api.example.com A
# api.example.com.  287  IN  A  93.184.216.34
#                   ↑ 287 seconds remaining in cache

# 7. Reverse DNS lookup
dig -x 93.184.216.34

# 8. MX records (for mail delivery issues)
dig example.com MX

# 9. DNSSEC validation check
dig api.example.com A +dnssec

# 10. DNS response time measurement
dig +stats api.example.com A 2>&1 | grep "Query time"
# Query time: 2 msec  ← cached
# Query time: 87 msec ← uncached (full resolution)
```

---

### ⚙️ DNSSEC: Authenticating DNS Responses

```
Problem: DNS responses can be spoofed (cache poisoning)
  Attacker sends forged DNS reply → resolver caches it
  Next query gets attacker's IP → user connects to attacker

DNSSEC: cryptographically signs zone records
  Zone has DNSKEY record (public key)
  Each record has RRSIG (signature)
  Resolvers verify signature against DNSKEY
  Chain of trust: root zone signs TLD zone, TLD signs domain zone

Limitation:
  - Adds latency (signature verification)
  - Complex to operate
  - DNSSEC + DANE can authenticate TLS certificates via DNS
  - ~30% of .com zones signed (2024)

Check:
  dig api.example.com A +dnssec
  # Look for "ad" flag (authentic data) in answer
  delv api.example.com A  # DNSSEC-aware resolver tool
```

---

### ⚙️ DNS for Service Discovery (Kubernetes)

```
Kubernetes uses DNS for service discovery:

Service: my-service in namespace: my-namespace
DNS name: my-service.my-namespace.svc.cluster.local
  → resolves to ClusterIP of the service
  → round-robins across pod IPs for headless services

Pod DNS: pod-ip.namespace.pod.cluster.local
  10-0-0-5.my-namespace.pod.cluster.local → 10.0.0.5

Headless service (ClusterIP: None):
  dig my-service.my-namespace.svc.cluster.local
  → returns multiple A records (all pod IPs)
  → client does load balancing based on DNS round-robin

DNS search domains in pod:
  /etc/resolv.conf in pod contains:
    search my-namespace.svc.cluster.local
           svc.cluster.local
           cluster.local
  Short name 'my-service' resolves because of search list
  → my-service.my-namespace.svc.cluster.local
```

---

### 📐 Scale Considerations

```
DNS at 1M QPS:
  Authoritative servers (Route53, Cloudflare):
    Horizontally scaled, anycast routing
    Route53: ~1B queries/day (>11K QPS)
  
  Resolver caching reduces authoritative load:
    Cache hit rate > 99% for popular domains
    TTL=300: each domain queried ≤ once per 5 min per resolver
    At 1M users, 1 resolver: 1M users / 300s = ~3K QPS uncached

Negative caching (NXDOMAIN):
  "Domain does not exist" response is also cached (NXCACHE TTL)
  Important: a failed lookup is cached!
  Typo in DNS record name? Your service is unreachable for TTL seconds
  
DNS as a DDoS vector:
  DNS amplification: 40-byte query → 2,800-byte response (70x)
  Reflective DDoS: spoof source IP → amplified response → victim
  Defense: rate limiting on resolvers, BCP38 ingress filtering
```

---

### 🧭 Decision Guide

```
When DNS is your first suspect:
  1. Can you reach the IP directly? (bypass DNS)
     curl http://93.184.216.34  # use IP directly
     If YES → DNS problem, not service problem
     If NO  → service or network problem

  2. Different results from different resolvers?
     dig example.com @8.8.8.8 vs @1.1.1.1 vs @company-dns
     If different → propagation in progress, or split-horizon DNS

  3. SOA serial number to check if changes deployed:
     dig example.com SOA @ns1.exampledns.net
     # "2024032101" = year 2024, month 03, day 21, version 01
     # Compare with secondary NS - if different, replication issue

Interview answer for "how does DNS work":
  "Client asks recursive resolver. Resolver checks cache.
  Cache miss: resolver walks the hierarchy - asks root for
  TLD server, TLD for authoritative server, authoritative
  for the record. Each hop is cached by TTL. For fast
  propagation: lower TTL to 60s a week before changes,
  make the change, wait 60s, verify, then raise TTL back."
```