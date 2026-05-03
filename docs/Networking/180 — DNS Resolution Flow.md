---
layout: default
title: "DNS Resolution Flow"
parent: "Networking"
nav_order: 180
permalink: /networking/dns-resolution-flow/
number: "0180"
category: Networking
difficulty: ★★☆
depends_on: DNS, UDP, IP Addressing
used_by: HTTP & APIs, Microservices, Kubernetes, CDN
related: DNS, CDN, Load Balancer L4_L7, DHCP, Anycast
tags:
  - networking
  - dns
  - resolution
  - recursive
  - caching
---

# 180 — DNS Resolution Flow

⚡ TL;DR — DNS resolution follows a 4-level lookup cascade (browser cache → OS cache → recursive resolver → authoritative server hierarchy) taking 1-100ms for uncached queries and <1ms for cached; understanding this flow is essential for diagnosing latency, TTL propagation, and split-horizon DNS in cloud and Kubernetes environments.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (PRECISE MECHANISM):**
If every DNS query went all the way to authoritative servers, the 13 root DNS server IP sets would receive billions of queries per second — the same few hundred names (google.com, facebook.com, etc.) queried by billions of users would generate hundreds of millions of root server queries per second. The DNS hierarchy itself would collapse under load.

**THE BREAKING POINT:**
Even with caching, DNS queries add latency to every new connection. A browser making 50 requests to different subdomains must resolve each one before connecting. Without understanding the resolution flow, developers attribute latency to their application when the actual bottleneck is repeated DNS lookups that bypass the cache.

**THE INVENTION MOMENT:**
DNS resolution is designed as a multi-layer caching system. Each layer handles different failure and latency scenarios. The key design: authoritative servers only handle queries for their zones; recursive resolvers cache and aggregate queries from many clients; local OS caches reduce network round trips; browser caches reduce OS calls. Understanding each layer tells you exactly where to look when names don't resolve correctly or propagation is slow.

---

### 📘 Textbook Definition

**DNS resolution flow** is the sequence of lookups performed to resolve a hostname to an IP address: (1) **Browser/application cache** — checks in-memory cache first; (2) **OS resolver cache** — checks the system-level DNS cache and `/etc/hosts`; (3) **Recursive resolver** (configured via `/etc/resolv.conf` or DHCP) — checks its cache, then performs the recursive resolution: querying root → TLD → authoritative servers, caching each response per TTL; (4) **Authoritative DNS server** — returns the definitive answer for a zone. The process uses UDP port 53 (TCP for responses >512 bytes or zone transfers). EDNS0 extends the UDP payload limit to ~4096 bytes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DNS resolution is a 4-level cache waterfall — browser cache, then OS cache, then resolver cache, then a hierarchy of authoritative servers — with each layer serving the vast majority of queries so the next level rarely gets hit.

**One analogy:**

> DNS lookup is like checking prices in a store. First, check your memory (browser cache — "I know Google's price"). If not, ask the store clerk (OS resolver — checks the store's price list). If not, ask the regional manager (recursive resolver — checks its database). If not, call corporate headquarters hierarchy (root → TLD → authoritative) and update the database for next time. Most queries never make it past the first two layers.

**One insight:**
`dig +trace example.com` shows you every step of the resolution hierarchy. Use this any time you're debugging "DNS propagation" issues — it reveals exactly which server returned what answer, at what TTL, and from which authoritative server.

---

### 🔩 First Principles Explanation

**THE FOUR LAYERS:**

**Layer 1: Application/Browser Cache**

- Stores DNS results in process memory
- TTL respected (or overridden — Chrome has its own 60-second minimum)
- Scope: single process
- Bypass: restart the process / `chrome://net-internals/#dns` → Clear host cache

**Layer 2: OS Resolver Cache**

- Linux: `systemd-resolved` (recent distros) or `/etc/nsswitch.conf` → `libc` resolver
- Windows: DNS Client service
- Checks `/etc/hosts` first (unless overridden in nsswitch.conf)
- Bypass: `systemd-resolve --flush-caches` (Linux) / `ipconfig /flushdns` (Windows)

**Layer 3: Recursive Resolver**

- Configured via DHCP or static `/etc/resolv.conf`
- Common: 8.8.8.8 (Google), 1.1.1.1 (Cloudflare), VPC DNS (169.254.169.253 in AWS)
- Caches answers per TTL, shared across all clients using this resolver
- If answer cached: returns immediately (typically <5ms)
- If not cached: performs iterative resolution (see below)

**Layer 4: Iterative Resolution by Recursive Resolver**

```
1. Recursive resolver queries one of 13 root server sets
   (a.root-servers.net ... m.root-servers.net)
   Root servers' IPs are hardcoded in resolver software (root hints file)

   Request:  "What's the NS for .com?"
   Response: NS records for .com TLD servers (delegated to Verisign)
             + Glue records (A records for the NS hosts)
   TTL: 172800 (2 days) — cached by resolver

2. Query a .com TLD server (e.g., a.gtld-servers.net)
   Request:  "What's the NS for example.com?"
   Response: NS records for example.com's authoritative servers
   TTL: 172800 — cached by resolver

3. Query example.com's authoritative server (e.g., ns1.example.com)
   Request:  "What's the A record for www.example.com?"
   Response: A 93.184.216.34, TTL 3600
   Cached by resolver for 3600 seconds

Total network round trips for uncached: 3 (root, TLD, authoritative)
Typical latency: root (~10ms) + TLD (~20ms) + auth (~30ms) = ~60ms
```

**KUBERNETES DNS (CoreDNS + search domains):**

```
/etc/resolv.conf in a Kubernetes pod:
nameserver 10.96.0.10          (CoreDNS ClusterIP)
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5

Lookup "payment-service":
1. Tries: payment-service.default.svc.cluster.local → FOUND (CoreDNS)
   (dot-count < ndots:5 → tries with search domains first)

Lookup "api.external.com":
1. Tries: api.external.com.default.svc.cluster.local → NXDOMAIN
2. Tries: api.external.com.svc.cluster.local → NXDOMAIN
3. Tries: api.external.com.cluster.local → NXDOMAIN
4. Tries: api.external.com → FOUND (public DNS)
→ 4 DNS queries for one external lookup!
Fix: use FQDN with trailing dot: api.external.com.
     or set ndots:1 for pods that only query external names
```

---

### 🧪 Thought Experiment

**SETUP:**
Your application starts and makes 1,000 new HTTP connections in the first second, all to different subdomains of `api.example.com`. DNS TTL = 300 seconds. Measure DNS impact on startup latency.

**SCENARIO A: 1,000 unique FQDNs (sub1.api.example.com, sub2.api.example.com, ...)**

- 1,000 DNS lookups in parallel (async HTTP client)
- DNS resolver caches per FQDN separately
- 1,000 cache misses in the first second
- Resolver makes 1,000 queries to ns1.example.com
- At 100ms per authoritative query: ~100ms until all resolved (parallel)
- ns1.example.com may rate-limit

**SCENARIO B: 10 unique FQDNs, called 100 times each**

- 10 cache misses on first request per FQDN
- 990 subsequent requests hit OS/resolver cache (TTL 300s)
- ~10ms for 10 parallel DNS lookups
- Startup latency: ~10ms (DNS) + connection time

**LESSON:**
Design APIs with a small number of stable FQDNs. Don't use per-request unique hostnames. Application-level DNS caching (TTL-aware) dramatically reduces DNS overhead.

---

### 🧠 Mental Model / Analogy

> DNS resolution is like a multi-level library research process. Your personal notes (browser cache) → the library's card catalogue (OS cache) → the reference librarian (recursive resolver, who knows every library in the city and caches commonly requested books) → inter-library loan (authoritative server, who actually owns the book). Most people find what they need in the first two steps. The librarian's cache means popular questions get answered instantly. The inter-library loan takes minutes but is rarely needed.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you type "google.com," your computer checks several places in order before actually going to the internet: its own memory, then the OS's memory, then asks your configured DNS server. If none of them know the answer, the DNS server runs up a chain of servers starting from the top of the internet's naming hierarchy down to Google's own name servers. Each answer is remembered (cached) so the next request is faster.

**Level 2 — How to use it (junior developer):**
Key insight: DNS lookups are not free. Test DNS latency: `time dig example.com`. For Java applications: set `networkaddress.cache.ttl=60` in `$JAVA_HOME/jre/lib/security/java.security` (default is forever, meaning stale IPs after deployments). For Node.js: DNS is cached at the OS level; restart may clear it. For Kubernetes: name lookup for internal services should use full FQDN (`service.namespace.svc.cluster.local`) to avoid 3 extra NXDOMAIN queries from search domain expansion. Use `dig +short` for quick IP lookup in scripts.

**Level 3 — How it works (mid-level engineer):**
Negative caching: NXDOMAIN (name does not exist) is cached for the SOA record's minimum TTL field. This means a typo in a hostname gets cached as "not found" for potentially hours. Check with `dig myservice.internal` — if you get NXDOMAIN with TTL > 0, you must wait for it to expire before the corrected record is visible. Negative TTL override: flush resolver cache to force re-lookup. EDNS Client Subnet (ECS, RFC 7871): recursive resolvers can forward a portion of the client's IP to authoritative servers, enabling geographic DNS responses (CDNs and Route 53 use this for latency-based routing). Split-horizon DNS: the same name resolves differently from inside vs outside your network (internal: private IP, external: public IP). AWS Route 53 Resolver implements split-horizon for VPC internal names.

**Level 4 — Why it was designed this way (senior/staff):**
DNS's iterative resolution model (client queries root, then TLD, then authoritative) vs recursive (root queries TLD, TLD queries authoritative on your behalf) is a deliberate load distribution design. With iterative resolution, the work of finding the authoritative server happens at the resolver — root servers only handle "who is responsible for this TLD?" queries, and TLD servers only handle zone delegation queries. Root servers receive ~100 billion queries/day, nearly all answered from resolver caches. The root server system (13 IP sets, ~2000 actual nodes via anycast) handles this load only because of multi-layer caching. The DNS protocol's simplicity (ASCII over UDP) enabled its global deployment on any hardware. This is why DNS still runs on 40-year-old protocol design.

---

### ⚙️ How It Works (Mechanism)

```bash
# Full resolution trace (shows every step)
dig +trace example.com
# Shows: root → TLD → authoritative, with TTLs

# Check resolution time
time dig example.com @8.8.8.8
# real 0m0.023s = 23ms (uncached)
time dig example.com @8.8.8.8   # run again
# real 0m0.005s = 5ms (cached at 8.8.8.8)

# Check OS DNS cache (systemd-resolved)
systemd-resolve --statistics
# Shows: cache hits, misses, total queries

# Flush OS DNS cache
systemd-resolve --flush-caches

# Check /etc/resolv.conf
cat /etc/resolv.conf
# nameserver 10.0.0.2  (DHCP-assigned)
# search example.internal

# Check /etc/nsswitch.conf (resolution order)
cat /etc/nsswitch.conf | grep hosts
# hosts: files dns  → check /etc/hosts FIRST, then DNS

# Test Kubernetes DNS from inside a pod
kubectl exec -it <pod-name> -- nslookup kubernetes.default
kubectl exec -it <pod-name> -- cat /etc/resolv.conf
# Check ndots setting and search domains

# DNS debugging with packet capture
tcpdump -nn -i any udp port 53 -v
# Shows DNS query/response packets
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────────┐
│  Complete DNS Resolution: api.payment.example.com  │
└────────────────────────────────────────────────────┘

 t=0ms   Application: connect("api.payment.example.com", 443)
         │
         ▼
 t=0ms   Browser/JVM cache: MISS
         │
         ▼
 t=0ms   OS resolver (systemd-resolved):
         Check /etc/hosts: no entry
         Check OS cache: MISS
         │
         ▼
 t=0ms   Query recursive resolver: 10.0.0.53
         │
         ▼
 t=0ms   Recursive resolver cache: MISS
         │
         ▼ (iterative resolution)
 t=5ms   Query root server (a.root-servers.net):
         ← NS: .com → a.gtld-servers.net  [TTL: 172800, cached]
         │
 t=15ms  Query a.gtld-servers.net:
         ← NS: example.com → ns1.example.com [TTL: 172800, cached]
         │
 t=30ms  Query ns1.example.com (authoritative):
         ← CNAME: api.payment → payment.example.com [TTL: 300]
         ← A: payment.example.com → 93.184.216.34  [TTL: 60]
         │
 t=30ms  Recursive resolver: cache both records
         Return 93.184.216.34 to OS resolver
         │
 t=30ms  OS resolver: cache (TTL=60)
         Return to application
         │
 t=30ms  Application: TCP connect to 93.184.216.34:443

Second call (< 60 seconds later):
 t=0ms   OS cache: HIT → immediate return
         Application: TCP connect immediately (0ms DNS overhead)
```

---

### 💻 Code Example

**Example — DNS-aware connection pooling with TTL:**

```python
import socket
import time
import threading
from typing import Optional

class DNSCachingResolver:
    """DNS resolver with TTL-aware caching.
    Prevents stale cached IPs after DNS changes.
    """

    def __init__(self, default_ttl: int = 30):
        self._cache: dict[str, tuple[str, float]] = {}
        # (resolved_ip, expires_at)
        self._lock = threading.Lock()
        self._default_ttl = default_ttl

    def resolve(self, hostname: str) -> Optional[str]:
        """Resolve hostname, using cache if still valid."""
        with self._lock:
            if hostname in self._cache:
                ip, expires_at = self._cache[hostname]
                if time.monotonic() < expires_at:
                    return ip  # Cache hit

        # Cache miss or expired: resolve
        try:
            start = time.perf_counter()
            infos = socket.getaddrinfo(hostname, None,
                                       socket.AF_INET,
                                       socket.SOCK_STREAM)
            elapsed = (time.perf_counter() - start) * 1000

            if infos:
                ip = infos[0][4][0]
                with self._lock:
                    self._cache[hostname] = (
                        ip,
                        time.monotonic() + self._default_ttl
                    )
                print(f"DNS resolved {hostname} → {ip} "
                      f"in {elapsed:.1f}ms")
                return ip
        except socket.gaierror as e:
            print(f"DNS resolution failed for {hostname}: {e}")
            return None

    def invalidate(self, hostname: str):
        """Force re-resolution on next call."""
        with self._lock:
            self._cache.pop(hostname, None)

    def cache_stats(self) -> dict:
        with self._lock:
            now = time.monotonic()
            return {
                'total': len(self._cache),
                'valid': sum(1 for _, (_, exp) in self._cache.items()
                            if exp > now),
                'expired': sum(1 for _, (_, exp) in self._cache.items()
                              if exp <= now),
            }

# Usage
resolver = DNSCachingResolver(default_ttl=30)
print(resolver.resolve("google.com"))   # DNS lookup
print(resolver.resolve("google.com"))   # Cache hit
print(resolver.cache_stats())
```

---

### ⚖️ Comparison Table

| Cache Layer                    | Scope             | Flush                            | Typical Hit Rate |
| ------------------------------ | ----------------- | -------------------------------- | ---------------- |
| Browser/app                    | Single process    | Process restart / API            | ~60%             |
| OS (systemd-resolved)          | System-wide       | `systemd-resolve --flush-caches` | ~30%             |
| Recursive resolver (ISP/cloud) | Millions of users | TTL expiry / admin flush         | ~9%              |
| Authoritative server           | Definitive        | New record publication           | <1%              |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DNS changes propagate instantly           | Changes are visible only after TTL expiry at each cache layer. Lower the TTL **before** making changes.                                                |
| Flushing your browser cache flushes DNS   | Browser DNS cache is separate from browser HTTP cache. Flush DNS: `chrome://net-internals/#dns` → Clear host cache                                     |
| DNS failures are rare                     | DNS is involved in every connection. A 1-second DNS timeout on 10% of requests adds 100ms average latency. Monitor DNS failure rates separately.       |
| The recursive resolver is always your ISP | Cloud instances use cloud provider DNS (AWS: 169.254.169.253, GCP: 169.254.169.254). Kubernetes pods use CoreDNS. Corporate networks use internal DNS. |

---

### 🚨 Failure Modes & Diagnosis

**Slow DNS Resolution Adding 100-500ms to Every Request**

**Symptom:**
`curl -w '%{time_namelookup}' -o /dev/null -s https://example.com` shows 200ms+ for name lookup. Application latency spikes on cold start.

```bash
# Measure DNS resolution time
curl -w "DNS: %{time_namelookup}\nConnect: %{time_connect}\n" \
     -o /dev/null -s https://example.com

# Check if recursive resolver is reachable
time dig google.com @$(grep nameserver /etc/resolv.conf | head -1 | awk '{print $2}')

# Check for slow resolver (try alternatives)
time dig google.com @8.8.8.8    # Google
time dig google.com @1.1.1.1    # Cloudflare

# In Kubernetes: check CoreDNS latency
kubectl -n kube-system logs <coredns-pod> | grep "slow"
kubectl top pods -n kube-system  # Check CoreDNS CPU/memory

# Check for ndots expansion causing extra queries
# (Kubernetes pods making external DNS calls)
tcpdump -nn -i any udp port 53 -c 50
# Look for repeated NXDOMAIN for .svc.cluster.local suffixes
```

**Fix:**
Use a faster recursive resolver; fix Kubernetes ndots setting; add application-level DNS caching with TTL awareness; pre-resolve hostnames at startup and refresh periodically.

---

### 🔗 Related Keywords

**Prerequisites:** `DNS`, `UDP`, `IP Addressing`

**Builds On This:** `CDN` (DNS-based routing to nearest edge), `Load Balancer L4/L7` (DNS-based LB), `Anycast` (DNS anycast routing), `DHCP` (configures DNS server IP)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 4 LAYERS     │ App cache → OS cache → Recursive resolver │
│              │ → Authoritative (root → TLD → zone)       │
├──────────────┼───────────────────────────────────────────┤
│ TRACE        │ dig +trace example.com                    │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ Uncached: 10-100ms; Cached: <1ms          │
├──────────────┼───────────────────────────────────────────┤
│ K8S ndots    │ ndots:5 causes 4+ lookups for external;   │
│              │ use FQDN (trailing dot) or ndots:1        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Layered cache cascade: most queries hit  │
│              │ cache; rare misses trigger full hierarchy" │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A production Kubernetes service starts receiving sporadic "temporary failure in name resolution" errors. The errors appear on ~0.1% of requests. Describe a complete diagnostic runbook: (a) how to determine whether the failure is at the application DNS cache, OS resolver, CoreDNS, or upstream DNS, (b) the specific `kubectl` and `tcpdump` commands to isolate the failure layer, (c) how CoreDNS metrics (`coredns_dns_request_duration_seconds_bucket`, `coredns_dns_responses_total{rcode="SERVFAIL"}`) help quantify the issue, (d) what "DNS negative caching" looks like in practice (NXDOMAIN TTL causing repeated failures), and (e) the circuit-breaker pattern for DNS: how to implement "if DNS fails, use last known good IP" in a service mesh.

**Q2.** Explain EDNS Client Subnet (ECS, RFC 7871) and its role in CDN DNS routing: (a) how a recursive resolver at 8.8.8.8 knows to send your query to a CDN PoP near you rather than near Google's data centres, (b) the privacy trade-off of ECS (forwarding client IP prefix to authoritative servers), (c) how Cloudflare and AWS CloudFront use ECS for latency-based routing, (d) what happens when a corporate resolver that doesn't support ECS is used (all users get the same CDN PoP), and (e) how "DNS-based global traffic management" compares to Anycast for CDN distribution.
