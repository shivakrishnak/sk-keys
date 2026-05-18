---
id: NET-012
title: "DNS Overview"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-002
used_by: NET-043, NET-030, NET-044
related: NET-009, NET-043
tags:
  - networking
  - foundational
  - dns
  - application-layer
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/net/dns-overview/
---

**⚡ TL;DR** - DNS (Domain Name System) translates human-
readable domain names (`google.com`) into IP addresses
(`142.250.80.78`). It is a globally distributed hierarchical
database with ~2 billion queries per second - the phonebook
of the internet.

| #012 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, What Happens When You Type a URL | |
| **Used by:** | DNS Resolution Deep Dive, HTTP and HTTPS Basics, TLS Handshake | |
| **Related:** | IP Address, DNS Resolution Deep Dive | |

---

### 🔥 The Problem This Solves

Humans remember names; computers route by numbers. Without
DNS, every user would need to remember `142.250.80.78`
instead of `google.com`. Worse, IP addresses change when
servers move, but the domain name stays stable. DNS
decouples the human-readable name from the machine-readable
address, allowing either to change independently.

---

### 📘 Textbook Definition

**DNS** (Domain Name System) is a globally distributed,
hierarchical database that maps domain names to IP addresses
(A records for IPv4, AAAA for IPv6) and other resource
records. Defined in RFC 1034 and RFC 1035 (1987). The DNS
hierarchy consists of: root name servers (13 clusters of
root servers), Top Level Domain servers (TLDs: `.com`,
`.org`, `.io`), authoritative name servers (per domain),
and resolvers (recursive resolvers at ISPs and public DNS
like `8.8.8.8`). DNS queries use UDP port 53 for standard
queries and TCP port 53 for zone transfers and large responses.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DNS translates `google.com` to `142.250.80.78` by asking
a hierarchy of servers, starting from the root.

**One analogy:**

> DNS is like a phone book search tree. If you can't find
> "Smith, J." in the local directory, you call a regional
> operator. If they don't know, they escalate to the national
> operator. But once found, you write it in your personal
> address book (DNS cache) so you don't have to call the
> hierarchy every time. Most queries resolve from cache.

**One insight:**
DNS is the first thing that happens for almost every network
connection - before TCP, before TLS, before HTTP. A 300ms
DNS lookup adds 300ms to every first connection if not
cached. This is why DNS caching, TTL management, and DNS
prefetching exist.

---

### 🔩 First Principles Explanation

**DNS Record Types:**

```
┌──────────────────────────────────────────────────────────┐
│  Essential DNS Record Types                              │
├────────┬─────────────────────────────────────────────────┤
│  Type  │  Purpose and Example                           │
├────────┼─────────────────────────────────────────────────┤
│  A     │  IPv4 address mapping                          │
│        │  google.com → 142.250.80.78                   │
├────────┼─────────────────────────────────────────────────┤
│  AAAA  │  IPv6 address mapping                          │
│        │  google.com → 2607:f8b0:4004:c07::66          │
├────────┼─────────────────────────────────────────────────┤
│  CNAME │  Canonical Name (alias)                        │
│        │  www.example.com → example.com                │
│        │  (follow the alias, not an IP)                 │
├────────┼─────────────────────────────────────────────────┤
│  MX    │  Mail eXchange (email routing)                 │
│        │  example.com MX → mail.example.com (pri 10)  │
├────────┼─────────────────────────────────────────────────┤
│  TXT   │  Arbitrary text (SPF, DKIM, ownership verify) │
│        │  v=spf1 include:_spf.google.com ~all          │
├────────┼─────────────────────────────────────────────────┤
│  NS    │  Name Server records (authoritative servers)  │
│        │  example.com NS → ns1.registrar.com           │
├────────┼─────────────────────────────────────────────────┤
│  PTR   │  Reverse lookup (IP → name)                   │
│        │  78.80.250.142.in-addr.arpa → google.com      │
├────────┼─────────────────────────────────────────────────┤
│  SOA   │  Start of Authority (zone metadata)           │
│        │  Serial, refresh, retry, expire TTLs          │
└────────┴─────────────────────────────────────────────────┘
```

**DNS hierarchy:**

```
┌──────────────────────────────────────────────────┐
│  DNS Hierarchy                                   │
│                                                  │
│  . (Root)                                        │
│  └── .com (TLD)                                  │
│      └── google.com (Second-Level Domain)        │
│          └── www.google.com (Subdomain)          │
│              └── mail.google.com (Subdomain)     │
└──────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
You request `www.example.com` for the first time with an
empty DNS cache. Trace the full resolution:

1. Check local `/etc/hosts` - not there
2. Check local DNS cache - empty
3. Ask configured resolver (e.g., `8.8.8.8`)
4. Resolver asks root server: "Who handles `.com`?"
   Root: "Ask `.com` TLD server: `a.gtld-servers.net`"
5. Resolver asks `.com` TLD: "Who handles `example.com`?"
   TLD: "Ask authoritative server: `ns1.example.com`"
6. Resolver asks `ns1.example.com`: "What is `www.example.com`?"
   Authoritative: "`www.example.com` A `93.184.216.34` TTL 3600"
7. Resolver caches result for 3600 seconds (1 hour)
8. Resolver returns IP to your machine
9. Your machine caches the result
10. TCP connection begins to `93.184.216.34`

**THE INSIGHT:**
Steps 4-6 are the recursive resolution. But the resolver
caches each level independently: the root server delegation
to `.com` TLDs is cached for 2 days. The `.com` TLD
delegation to `ns1.example.com` is cached for 2 days.
Only the final A record uses the domain owner's TTL (3600s).
This is why DNS propagation for a newly registered domain
takes up to 48 hours - the TLD delegation cache must expire.

---

### 🧠 Mental Model / Analogy

> DNS is like asking for directions in an unfamiliar city:
> 1. You ask a local (recursive resolver) who knows a lot
>    but not everything.
> 2. They ask the city hall (root) which district the
>    address is in.
> 3. District office (TLD) points to the street's
>    information center (authoritative server).
> 4. Street information center gives exact address (IP).
> 5. The local helper writes it in their notebook (cache)
>    so the next person asking saves time.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DNS is the internet's phonebook: type in a name, get back
an IP address. Your computer needs the IP to connect.

**Level 2 - How to use it (junior developer):**
Use `dig` or `nslookup` to look up DNS records. `dig
google.com A` returns IPv4 addresses. The TTL field tells
you how long the record is cached. If DNS is failing,
`dig @8.8.8.8 google.com` bypasses your local DNS and
queries Google directly to verify the problem is local.

**Level 3 - How it works (mid-level engineer):**
DNS caching happens at multiple levels: OS resolver cache,
browser cache, and the recursive resolver's cache. The
resolver cache is shared across all users of that resolver.
When Google's `8.8.8.8` resolves `example.com`, it caches
the result for all users. TTL determines cache lifetime.
Low TTL (60 seconds) means every user triggers a fresh
lookup every minute. High TTL (86400 = 1 day) means changes
propagate slowly.

**Level 4 - Why it was designed this way (senior/staff):**
DNS was designed for a ~1000-node ARPANET where `HOSTS.TXT`
was manually distributed weekly. The hierarchical
distributed design allows it to scale to 1 billion+ domains
with billions of queries per second. The trade-off was
consistency: DNS is eventually consistent. A TTL-0 record
is resolved fresh every time but adds latency. A TTL-86400
record is fast but takes a day to propagate changes.

**Level 5 - Mastery (distinguished engineer):**
DNS is the single most abused protocol for both censorship
and attack. DNS over HTTPS (DoH) and DNS over TLS (DoT)
encrypt DNS queries to prevent interception and spoofing.
DNS-based load balancing (multiple A records returned in
round-robin or based on geolocation) has known failure
modes: clients often use the first IP and ignore TTL on
cached records. This is why health-check-aware DNS (Route
53 latency routing) still needs application-layer health
checks - DNS alone cannot route around a failed endpoint
fast enough due to caching.

---

### ⚙️ How It Works (Mechanism)

**Essential DNS query tools:**

```bash
# Basic A record lookup
dig google.com A
# Shows: Answer section with IP, TTL, record type

# Check all record types for a domain
dig google.com ANY

# Reverse DNS lookup (IP → name)
dig -x 8.8.8.8

# Bypass local resolver, query specific server
dig @8.8.8.8 example.com A

# Trace the full recursive resolution
dig +trace google.com

# Check TTL of a cached record
# (TTL counts down from original value)
dig google.com +noall +answer
# google.com.   299   IN  A  142.250.80.78
#               ^^^
#               299 seconds remaining in cache

# Query authoritative nameservers
dig google.com NS
```

**DNS response interpretation:**

```
;; QUESTION SECTION:
;google.com.    IN  A        ← Querying for IPv4

;; ANSWER SECTION:
google.com.  299 IN  A  142.250.80.78
              ^^^
              TTL: 299 seconds until cache expires
```

**DNS record TTL strategy:**

```
┌──────────────────────────────────────────────────────────┐
│  TTL Strategy                                            │
├────────────────┬─────────────────────────────────────────┤
│  TTL           │  Use Case                               │
├────────────────┼─────────────────────────────────────────┤
│  60-300s       │  Records you need to change quickly     │
│                │  (e.g., load balancer failover, deploy) │
├────────────────┼─────────────────────────────────────────┤
│  3600s (1hr)   │  Standard web records (good balance)    │
├────────────────┼─────────────────────────────────────────┤
│  86400s (1day) │  Stable records (MX, NS, rarely change)│
├────────────────┼─────────────────────────────────────────┤
│  300s 24h pre  │  Lower TTL 24h before planned change    │
│  change        │  so old records expire faster           │
└────────────────┴─────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DNS in the context of an HTTP request:**

DNS is step 0. Before TCP can connect to `example.com`, the
OS must know the IP address. The full sequence:

```
1. DNS lookup:    example.com → 93.184.216.34  (5-300ms)
2. TCP connect:   SYN to 93.184.216.34:443     (1 RTT)
3. TLS handshake: certificates + key exchange  (1-2 RTT)
4. HTTP request:  GET / HTTP/2                 (1 RTT)
```

If DNS takes 300ms, that's 300ms added to every cold request.
Browsers pre-fetch DNS for links on the current page to
hide this latency.

**WHAT CHANGES AT SCALE:**
At 100,000+ requests/second, DNS caching is critical. Every
DNS cache miss costs 10-300ms of latency and load on
upstream resolvers. Production architectures use:
- Local DNS caching (dnsmasq, systemd-resolved)
- DNS prefetching in browsers and applications
- TTL-aware connection pooling
- Anycast DNS (Google `8.8.8.8`, Cloudflare `1.1.1.1`)
  routing queries to the nearest server globally

---

### ⚖️ Comparison Table

| DNS Resolver | IP | Performance | Privacy |
|---|---|---|---|
| Google | `8.8.8.8` / `8.8.4.4` | Fast globally | No DoH by default |
| Cloudflare | `1.1.1.1` / `1.0.0.1` | Fastest by benchmark | DoH/DoT supported |
| Quad9 | `9.9.9.9` | Fast, blocks malware | Privacy-focused |
| ISP default | Varies | Often slow, monitored | Not private |
| System resolver | Configured in `/etc/resolv.conf` | Varies | Depends on config |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DNS propagation is instant | DNS changes propagate as slowly as the old record's TTL allows. A record with TTL 86400 takes up to 24 hours to propagate globally. Lower the TTL before making changes, not after. |
| DNS is just A records | DNS serves SPF records (TXT) for email anti-spam, DKIM signatures (TXT), CNAME for CDN routing, SRV records for service discovery (used by Kubernetes), and NAPTR records for VoIP. |
| You can point DNS to a domain name (not just IP) | A records must point to IPs. CNAME records can alias to other names. You CANNOT use CNAME for the zone apex (`example.com` itself) - only for subdomains. Use ALIAS or ANAME records for apex (AWS Route 53 alias). |

---

### 🚨 Failure Modes & Diagnosis

**DNS Failure - "Temporary failure in name resolution"**

**Symptom:**
```
curl: (6) Could not resolve host: example.com
getaddrinfo: Temporary failure in name resolution
```

**Root Cause:** DNS resolver is unreachable (no network),
misconfigured (`/etc/resolv.conf` missing), or the domain
doesn't exist.

**Diagnostic Command / Tool:**
```bash
# Step 1: Is DNS configured?
cat /etc/resolv.conf
# Should show: nameserver 8.8.8.8 (or similar)

# Step 2: Can we reach the DNS server?
ping -c 2 8.8.8.8
# If this fails: no network connectivity at all

# Step 3: Does DNS resolve from a known-good server?
dig @8.8.8.8 example.com A
# If this works: your local resolver is broken
# If this fails: the domain doesn't exist or 8.8.8.8 unreachable

# Step 4: Does the domain exist at all?
whois example.com | grep "Name Server"

# Fix: override resolver for testing
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

**Prevention:** Monitor DNS resolution with synthetic
monitoring. Set up multiple nameservers in `/etc/resolv.conf`
for redundancy. Use `search` directive for internal domains.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `IP Address` - DNS resolves names to these
- `What Happens When You Type a URL` - DNS as step 1

**Builds On This (learn these next):**
- `DNS Resolution Deep Dive` - full resolution mechanism,
  DNSSEC, DNS-based load balancing, split-horizon DNS
- `TLS Handshake Deep Dive` - TLS uses DNS for certificate
  validation (OCSP, CAA records)
- `HTTP and HTTPS Basics` - HTTP connections begin after
  DNS resolves the hostname

**Alternatives / Comparisons:**
- `mDNS / .local` - zero-config DNS for local networks
  without a DNS server (Apple Bonjour, Avahi)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Distributed hierarchical name→IP database  │
│              │ UDP/TCP port 53. ~2B queries/second.       │
├──────────────┼───────────────────────────────────────────┤
│ KEY RECORDS  │ A=IPv4, AAAA=IPv6, CNAME=alias,           │
│              │ MX=mail, TXT=verification/SPF,            │
│              │ NS=nameservers, PTR=reverse                │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ TTL controls cache lifetime. Lower TTL    │
│              │ before making changes, not after.         │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ dig @8.8.8.8 domain A (bypass local)     │
│              │ dig +trace domain (full recursion trace)  │
│              │ cat /etc/resolv.conf (check config)       │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ High TTL (86400) on records you need to   │
│              │ change quickly. Set TTL=300 24h before    │
│              │ any planned DNS change.                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "DNS is step 0 before every connection.   │
│              │  Cache miss = extra 10-300ms latency."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DNS Resolution Deep Dive → DNSSEC →       │
│              │ DNS-based load balancing                  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. DNS = name to IP. Hierarchy: Root → TLD → Authoritative.
   Recursive resolver caches results per TTL.
2. Diagnostic order: `cat /etc/resolv.conf`, then
   `dig @8.8.8.8 domain` to bypass local resolver.
   DNS failure is often a misconfigured resolver, not a
   missing domain.
3. Lower TTL before making DNS changes. High TTL means
   old IP cached for hours/days after you change records.

**Interview one-liner:**
"DNS is a distributed hierarchical database that maps
domain names to IP addresses. A recursive resolver (like
`8.8.8.8`) walks the hierarchy - root → TLD → authoritative
server - caching each response per its TTL. Key record
types: A (IPv4), AAAA (IPv6), CNAME (alias), MX (mail),
TXT (verification). DNS uses UDP port 53. DNS is step 0
before every TCP connection - a cache miss adds latency
to every cold request."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Hierarchical naming with delegated authority scales to
billions of entries with no central bottleneck. The same
pattern: LDAP/Active Directory (hierarchical OU structure),
Java package names (reverse domain: `com.google.cloud`),
URL path routing (hierarchical path matching in load
balancers), Kubernetes resource naming (namespace/name).

**Industry applications:**
- **Service discovery** - Kubernetes uses DNS to resolve
  service names to ClusterIP addresses. Every pod gets
  DNS configured to query the cluster's DNS server (CoreDNS).
- **CDN routing** - CDN providers use DNS to return
  different A records based on client geography.
  `cdn.example.com` → nearest CDN PoP IP.
- **Blue-green deployments** - swap DNS from blue to green
  environment after testing. TTL management is critical
  for rollback speed.

---

### 💡 The Surprising Truth

The internet runs on 13 root DNS server "addresses" but
these are served by hundreds of physical servers worldwide
via anycast routing. The "13 root servers" is a limit from
1987 when the root server list had to fit in a single UDP
DNS response (512 bytes). With 13 servers using 16-byte IPv4
addresses and overhead, it barely fit. IPv6 addresses (16
bytes each) would exceed the limit entirely. The anycast
trick - hundreds of servers sharing 13 IP addresses with
routing sending each query to the nearest - was the
engineering solution to scaling what is technically a
very small address space.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the full DNS resolution from query to answer,
   naming all four actors (client, resolver, TLD, authoritative).
2. **DEBUG** a DNS failure using `cat /etc/resolv.conf`,
   `dig @8.8.8.8`, and `dig +trace` to identify exactly
   which level of the hierarchy is failing.
3. **DECIDE** the right TTL for different record types
   (production web records vs stable MX vs pre-change TTL).
4. **BUILD** a mental model of DNS cache behavior and
   explain why "lowering TTL after the change" doesn't help.
5. **EXTEND** DNS knowledge to explain Kubernetes service
   discovery via CoreDNS and why `cluster.local` is the
   default domain suffix.

---

### 🧠 Think About This Before We Continue

**Q1.** Your deployment process changes the IP address of
`api.example.com`. The current TTL is 3600 seconds (1 hour).
Clients start failing 30 minutes after deployment because
some are still resolving to the old IP. What should you
have done 24 hours before the deployment? What can you do
NOW to speed up propagation for clients that have not yet
cached the record?

*Hint: TTL countdown started when the record was cached.
Some clients are at 3600s into their cache, others are at
1s. You cannot force cache eviction on clients you don't
control.*

**Q2.** In Kubernetes, a pod can reach the service
`my-service.my-namespace.svc.cluster.local`. How does the
pod's DNS configuration know to add `svc.cluster.local` as
a search suffix? What Kubernetes component serves DNS
queries for `cluster.local` domains? What does it do with
queries for external domains like `google.com`?

*Hint: Look at `/etc/resolv.conf` inside a Kubernetes pod.
The `search` line tells you what's automatically appended.*

**Q3.** [Hands-On] Run `dig +trace google.com A` and
observe the full recursive resolution. Count the round trips
(RTTs). Then run `dig google.com A` again (cached). Compare
the query time (shown at the bottom: `Query time: X msec`).
How much faster is the cached response? Now try
`dig +trace google.com A` with a short TTL record and
observe the difference.

*Hint: Recursive trace shows each delegation hop. Cached
response should be < 1ms. Uncached might be 50-200ms
depending on resolver proximity.*