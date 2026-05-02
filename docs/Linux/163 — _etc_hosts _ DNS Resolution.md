---
layout: default
title: "/etc/hosts & DNS Resolution"
parent: "Linux"
nav_order: 163
permalink: /linux/etc-hosts-dns-resolution/
number: "0163"
category: Linux
difficulty: ★★☆
depends_on: Networking, Linux File System Hierarchy
used_by: Networking, Kubernetes, DevOps
related: DNS, Networking, Linux File System Hierarchy
tags:
  - linux
  - networking
  - devops
  - os
---

# 163 — /etc/hosts & DNS Resolution

⚡ TL;DR — `/etc/hosts` is a static local hostname-to-IP mapping file that takes precedence over DNS; `/etc/nsswitch.conf` controls the resolution order (files → dns by default); together they determine how Linux resolves every hostname in every application.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every hostname resolution requires a DNS query to a remote server. If the DNS server is down, unreachable, or returns wrong results, the system cannot resolve any hostname — including `localhost`. Development environments need to test services using domain names before DNS records exist. Container orchestrators need to resolve service names within the cluster without relying on external DNS.

**THE BREAKING POINT:**
A developer wants to test `api.myapp.local` pointing to their local machine. There's no DNS record for `.local` in any public DNS. A Kubernetes pod needs to resolve `myservice.default.svc.cluster.local` — this is a cluster-internal hostname that external DNS knows nothing about.

**THE INVENTION MOMENT:**
`/etc/hosts` predates DNS. In the original ARPANET (1970s), every host maintained a hosts.txt file downloaded from a central server — this was the only name resolution mechanism. DNS replaced this in 1983, but `/etc/hosts` was retained as a local override. Today it's used for: localhost (127.0.0.1 always resolves to localhost via /etc/hosts), development domain aliases, container networking (Kubernetes injects per-pod `/etc/hosts` entries), blocking domains (point ads/malware to 0.0.0.0), and emergency DNS override.

---

### 📘 Textbook Definition

**`/etc/hosts`** is a plain-text file mapping hostnames to IP addresses. Entries take the form `<IP> <hostname> [<alias>...]`. Entries are checked before DNS queries by default.

**`/etc/nsswitch.conf`** (Name Service Switch) defines the resolution order for each type of system database (hosts, passwd, groups, etc.). The `hosts:` line typically reads `files dns` — meaning: check `/etc/hosts` first (`files`), then DNS (`dns`). On systems with `mDNS`, the line may be `files mdns4_minimal [NOTFOUND=return] dns`.

**`/etc/resolv.conf`** configures which DNS servers to query, which search domains to append to short names, and resolver options (timeout, ndots).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Linux hostname resolution is: check `/etc/hosts` first, then ask DNS (configured in `/etc/resolv.conf`), in the order defined by `/etc/nsswitch.conf`.

**One analogy:**

> Hostname resolution is like looking up a phone number. `/etc/hosts` is your personal address book — fast, local, always available, your entries override everything. `/etc/resolv.conf` is the phone book service (DNS) to consult when your address book doesn't have the number. `/etc/nsswitch.conf` is your personal rule: "always check my address book first; if not found, call directory enquiries."

**One insight:**
The `hosts:` line in `/etc/nsswitch.conf` is the single most important line for understanding name resolution. Changing it from `files dns` to `dns files` makes DNS primary — every system call to `getaddrinfo()` will hit DNS before checking `/etc/hosts` (breaking localhost on DNS outage).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All hostname resolution goes through `getaddrinfo()` (POSIX) or `gethostbyname()` (legacy).
2. These library functions consult NSS (Name Service Switch) which reads `/etc/nsswitch.conf` to determine resolution order.
3. `/etc/hosts` entries are exact matches (no wildcards, no regex). The first match wins.
4. `/etc/resolv.conf` must specify at least one valid `nameserver` or DNS queries fail with timeout.
5. `search` or `domain` in `/etc/resolv.conf` appends suffixes to short names — `curl myservice` may resolve as `myservice.default.svc.cluster.local` in Kubernetes.

**DERIVED DESIGN:**

**`/etc/hosts` format:**

```
127.0.0.1   localhost
127.0.1.1   myhostname
::1         localhost ip6-localhost ip6-loopback
# Multiple hostnames on one line — all map to same IP
192.168.1.10  webserver webserver.internal
```

**`/etc/nsswitch.conf` hosts line:**

```
hosts: files dns          # files first (default)
hosts: dns files          # DNS first
hosts: files mdns4_minimal [NOTFOUND=return] dns
# mdns4_minimal: resolve .local via multicast DNS first
```

**`/etc/resolv.conf` format:**

```
nameserver 8.8.8.8
nameserver 8.8.4.4
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5 timeout:2 attempts:3
```

The `ndots:5` option: if a name has fewer than 5 dots, append search domains before trying as-is. Critical in Kubernetes: `myservice` becomes `myservice.default.svc.cluster.local` due to the `search` list.

**THE TRADE-OFFS:**
**`/etc/hosts`:** Always available, no network required, instant. But: manual maintenance, no TTL, changes require file edit, not scalable past a few dozen entries.
**DNS:** Scalable to millions of records, automatic TTL expiry, centralised management. But: requires network, can fail, adds latency.

---

### 🧪 Thought Experiment

**SETUP:**
A developer's application connects to `database.local` in development and `database.prod.example.com` in production. They want to test the production code path locally without changing the application.

**WITHOUT `/etc/hosts`:**
`database.prod.example.com` resolves to the production IP (dangerous) or NXDOMAIN if the developer is offline. They must either hardcode IPs (fragile) or maintain environment-specific code paths.

**WITH `/etc/hosts` override:**

```
# /etc/hosts on developer machine
127.0.0.1  database.prod.example.com
```

Now `database.prod.example.com` resolves to `127.0.0.1` — the developer's local database. The application uses its production code path but connects to local. `/etc/hosts` takes precedence over DNS. This is "DNS override" for local development. The key: this is local to the machine — the production DNS record is unchanged.

**THE INSIGHT:**
`/etc/hosts` is a local override layer. It intercepts hostname lookups before DNS is consulted. This makes it powerful for testing (redirect prod hostnames locally), potentially dangerous (malware modifies `/etc/hosts` to redirect banking sites), and fundamental to container networking (Kubernetes writes `/etc/hosts` in each pod).

---

### 🧠 Mental Model / Analogy

> Think of hostname resolution as a secretary answering calls. `/etc/nsswitch.conf` is the secretary's lookup procedure: "First, check my personal Rolodex (`/etc/hosts`). If the name is there, use that number — done. If not, call Directory Enquiries (`/etc/resolv.conf` DNS server) and use their answer." The secretary's Rolodex entries are always trusted over Directory Enquiries — even if Directory Enquiries has a different number for the same name. This is why `/etc/hosts` can "override" DNS: the secretary checks the Rolodex first and never calls Enquiries if a match is found.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you type `curl google.com`, Linux needs to find Google's IP address. It first checks `/etc/hosts` (a local list of "this name → that IP"). If the name isn't there, it asks a DNS server (configured in `/etc/resolv.conf`). The order is defined in `/etc/nsswitch.conf`. You can add any hostname→IP mapping to `/etc/hosts` to override DNS on your machine.

**Level 2 — How to use it (junior developer):**
Test resolution: `getent hosts google.com` (uses NSS, same as applications) or `nslookup google.com` (DNS only, ignores `/etc/hosts`). Add an entry to `/etc/hosts`: `echo "127.0.0.1 myapp.local" | sudo tee -a /etc/hosts`. Check resolution order: `grep ^hosts /etc/nsswitch.conf`. In containers: `kubectl exec -it mypod -- cat /etc/hosts` shows Kubernetes-injected entries. Flush DNS cache (systemd): `systemd-resolve --flush-caches`.

**Level 3 — How it works (mid-level engineer):**
Resolution flow: `curl google.com` → libc `getaddrinfo("google.com", ...)` → NSS dispatcher reads `/etc/nsswitch.conf` → `hosts: files dns` → `nss_files` module reads `/etc/hosts` (no match) → `nss_dns` module queries stub resolver → stub resolver reads `/etc/resolv.conf` → UDP DNS query to `nameserver` IP → response → IP returned to curl. The stub resolver in modern Linux is `systemd-resolved` (listening on `127.0.0.53:53`); older systems use the libc stub resolver directly. `ndots` behaviour: with `ndots:5` and search domain `svc.cluster.local`, `nslookup myservice` first tries `myservice.default.svc.cluster.local.`, then `myservice.svc.cluster.local.`, then `myservice.cluster.local.`, then `myservice.` (as absolute name). This causes 3-4 DNS queries per resolution of short names in Kubernetes — a performance concern at scale.

**Level 4 — Why it was designed this way (senior/staff):**
NSS (Name Service Switch) was originally Sun's innovation in Solaris 2.x (1990s) and was adopted by Linux glibc. The design principle was to make name resolution pluggable: the same API (`getaddrinfo`) can consult local files, NIS, LDAP, DNS, mDNS, or any custom NSS module, in any order, with configurable fallback behaviour. This pluggability is what enables Kubernetes's in-pod DNS (CoreDNS), macOS's mDNS for `.local` discovery, LDAP-based user lookup (`passwd: files ldap`), and custom service discovery. The `[NOTFOUND=return]` NSS action means "if this source says NOTFOUND, stop looking — don't try the next source." This is used with mDNS to prevent `.local` names from leaking to upstream DNS, which would generate unnecessary traffic and potentially incorrect answers.

---

### ⚙️ How It Works (Mechanism)

**Inspect resolution configuration:**

```bash
# Check resolution order
grep ^hosts /etc/nsswitch.conf
# hosts: files dns

# View /etc/hosts
cat /etc/hosts
# 127.0.0.1  localhost
# 127.0.1.1  myhostname

# View DNS configuration
cat /etc/resolv.conf
# nameserver 127.0.0.53  (systemd-resolved)
# search default.svc.cluster.local svc.cluster.local
# options ndots:5

# Use NSS resolution (same as applications)
getent hosts google.com         # uses files + dns
getent hosts localhost          # from /etc/hosts

# DNS-only resolution (bypasses /etc/hosts)
nslookup google.com
dig google.com
host google.com
```

**Test the override mechanism:**

```bash
# Add a test override
echo "127.0.0.1 test.example.com" | sudo tee -a /etc/hosts

# Verify getaddrinfo sees it (applications use this)
getent hosts test.example.com
# 127.0.0.1  test.example.com

# Verify DNS bypasses it
dig test.example.com
# NXDOMAIN or public IP (not 127.0.0.1)

# Clean up
sudo sed -i '/test.example.com/d' /etc/hosts
```

**Kubernetes pod DNS inspection:**

```bash
# Kubernetes injects /etc/hosts per pod
kubectl exec mypod -- cat /etc/hosts
# # Kubernetes-managed hosts file.
# 127.0.0.1 localhost
# ::1       localhost
# 10.244.1.5 mypod

# Kubernetes configures resolv.conf for service discovery
kubectl exec mypod -- cat /etc/resolv.conf
# nameserver 10.96.0.10           (CoreDNS cluster IP)
# search default.svc.cluster.local svc.cluster.local cluster.local
# options ndots:5

# Resolve a service from inside the pod
kubectl exec mypod -- getent hosts myservice
# 10.100.50.3  myservice.default.svc.cluster.local

# Resolve across namespaces
kubectl exec mypod -- getent hosts \
  myservice.other-namespace.svc.cluster.local
```

**systemd-resolved management:**

```bash
# Check systemd-resolved status
systemd-resolve --status

# View per-interface DNS servers
systemd-resolve --status | grep -A 5 "Link"

# Flush DNS cache
systemd-resolve --flush-caches

# Query with specific server
systemd-resolve --dns=8.8.8.8 google.com

# Check cache statistics
systemd-resolve --statistics
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  curl https://api.myapp.svc.cluster.local      │
│  (inside Kubernetes pod)                       │
└────────────────────────────────────────────────┘

 1. curl calls getaddrinfo("api.myapp.svc.cluster.local")
       │
       ▼
 2. glibc NSS reads /etc/nsswitch.conf:
    hosts: files dns
       │
       ▼
 3. nss_files: check /etc/hosts
    No match for "api.myapp.svc.cluster.local"
       │
       ▼
 4. nss_dns: consult stub resolver
       │
       ▼
 5. Stub resolver reads /etc/resolv.conf:
    nameserver 10.96.0.10
    search default.svc.cluster.local svc.cluster.local
    options ndots:5
       │
    ndots:5 check: "api.myapp.svc.cluster.local"
    has 4 dots → fewer than 5 → try search domains first
       │
       ▼
 6. DNS query #1:
    api.myapp.svc.cluster.local.default.svc.cluster.local.
    → CoreDNS: NXDOMAIN
       │
       ▼
 7. DNS query #2:
    api.myapp.svc.cluster.local. (absolute)
    → CoreDNS: A record → 10.100.50.3
       │
       ▼
 8. getaddrinfo returns 10.100.50.3
    curl connects to 10.100.50.3:443
```

---

### 💻 Code Example

**Example — Add hosts entries for local development:**

```bash
#!/bin/bash
# dev-hosts.sh — Manage local development host entries

MARKER="# dev-hosts managed"
HOSTS_FILE="/etc/hosts"

# Services and their local IPs
declare -A SERVICES=(
  ["api.local"]="127.0.0.1"
  ["db.local"]="127.0.0.1"
  ["redis.local"]="127.0.0.1"
  ["frontend.local"]="127.0.0.1"
)

add_dev_hosts() {
  echo "Adding dev host entries..."
  {
    echo ""
    echo "$MARKER start"
    for host in "${!SERVICES[@]}"; do
      echo "${SERVICES[$host]}  $host"
    done
    echo "$MARKER end"
  } | sudo tee -a "$HOSTS_FILE" > /dev/null
  echo "Done. Verify: getent hosts api.local"
}

remove_dev_hosts() {
  echo "Removing dev host entries..."
  sudo sed -i "/$MARKER start/,/$MARKER end/d" \
    "$HOSTS_FILE"
  # Remove blank line before marker
  sudo sed -i '/^$/N;/^\n$/d' "$HOSTS_FILE"
  echo "Done."
}

case "${1:-add}" in
  add)    add_dev_hosts ;;
  remove) remove_dev_hosts ;;
  *)      echo "Usage: $0 [add|remove]" ;;
esac
```

---

### ⚖️ Comparison Table

| Tool          | Scope        | Caching          | Override DNS     | Use Case                                 |
| ------------- | ------------ | ---------------- | ---------------- | ---------------------------------------- |
| `/etc/hosts`  | Host-local   | None (immediate) | Yes (before DNS) | Local dev, localhost, emergency override |
| DNS           | Network-wide | TTL-based        | No               | Production name resolution               |
| mDNS (Avahi)  | LAN-local    | Minimal          | No               | Zeroconf discovery on `.local`           |
| CoreDNS (K8s) | Cluster-wide | Yes              | Partial          | K8s service discovery                    |
| `dnsmasq`     | Host-local   | Yes              | Yes              | Local DNS cache + custom entries         |

How to choose: use `/etc/hosts` for static local overrides and localhost; DNS for anything that must be visible network-wide; dnsmasq for teams that want DNS semantics with local overrides and caching.

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                      |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nslookup` and `dig` reflect what applications see        | `nslookup` and `dig` query DNS directly; they bypass `/etc/hosts` and NSS; use `getent hosts` to see what applications see                                                                   |
| Editing `/etc/hosts` requires flushing DNS cache          | `/etc/hosts` has no cache — changes take effect immediately for all new resolution calls                                                                                                     |
| `/etc/resolv.conf` is always writeable                    | On systemd systems, `/etc/resolv.conf` is managed by systemd-resolved; direct edits may be overwritten; use `systemd-resolved` config or `resolvconf` instead                                |
| `127.0.0.1 localhost` in `/etc/hosts` is optional         | Many applications and system utilities assume `localhost` resolves to `127.0.0.1` via `/etc/hosts`; removing this entry breaks many tools                                                    |
| The `search` domain in K8s resolv.conf only adds a suffix | The `ndots:5` setting causes up to 5 DNS queries per short hostname resolution — a significant performance impact at scale that motivated the use of FQDN (trailing dot) in K8s service URLs |

---

### 🚨 Failure Modes & Diagnosis

**Application Can't Resolve Service Names in Kubernetes**

**Symptom:**
`curl myservice` fails with "Could not resolve host: myservice" from within a pod. `curl myservice.default.svc.cluster.local` works.

**Root Cause:**
`ndots:5` search domain resolution failing. The short name goes through search domains but CoreDNS can't resolve it, or the pod's `/etc/resolv.conf` is misconfigured.

**Diagnostic Commands:**

```bash
# Inside the failing pod
kubectl exec -it mypod -- bash

# Check resolver config
cat /etc/resolv.conf

# Test search domain expansion
nslookup myservice
# This will show what domains are tried

# Test each form
getent hosts myservice
getent hosts myservice.default
getent hosts myservice.default.svc.cluster.local

# Check CoreDNS is responding
nslookup kubernetes.default
# Should return the k8s API server ClusterIP

# Check CoreDNS pods
kubectl get pods -n kube-system | grep coredns
kubectl logs -n kube-system coredns-xxxxx
```

**Fix:**
Use FQDN (trailing dot): `curl myservice.default.svc.cluster.local.` — the trailing dot prevents search domain appending and goes direct to DNS. Or fix CoreDNS if it's not running.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Networking` — DNS resolution, IP addresses, and network namespaces are required context
- `Linux File System Hierarchy` — `/etc/` directory structure and the role of system configuration files

**Builds On This (learn these next):**

- `DNS` — deep dive into DNS protocol, record types (A, AAAA, CNAME, SRV), TTL, and resolution flow
- `Kubernetes` — pod DNS configuration, CoreDNS, and service discovery all build directly on the concepts here
- `Networking` — network namespaces mean each container has its own `/etc/resolv.conf` view

**Alternatives / Comparisons:**

- `mDNS / Avahi` — LAN-level zero-configuration hostname resolution for `.local` domains
- `dnsmasq` — local DNS caching proxy that can serve custom entries, with DNS semantics and caching
- `CoreDNS` — Kubernetes's configurable DNS server; extends DNS with Kubernetes-specific plugins

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ /etc/hosts: local hostname→IP table       │
│              │ /etc/nsswitch.conf: resolution order      │
│              │ /etc/resolv.conf: DNS server config       │
├──────────────┼───────────────────────────────────────────┤
│ RESOLUTION   │ NSS order: files → dns (by default)       │
│ ORDER        │ /etc/hosts checked before DNS query       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ nslookup/dig bypass /etc/hosts;           │
│              │ use getent hosts to see what apps see     │
├──────────────┼───────────────────────────────────────────┤
│ KUBERNETES   │ CoreDNS + search domains + ndots:5        │
│ DNS          │ Short names → up to 5 DNS queries         │
│              │ FQDN (trailing dot) avoids this           │
├──────────────┼───────────────────────────────────────────┤
│ OVERRIDE DNS │ Add to /etc/hosts — takes effect          │
│              │ immediately, no cache flush needed        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Personal address book first, then        │
│              │ Directory Enquiries"                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DNS deep dive → CoreDNS → mDNS            │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes pod running a Java application uses the hostname `database` to connect to a PostgreSQL service. The pod's `/etc/resolv.conf` has `search default.svc.cluster.local svc.cluster.local cluster.local` and `ndots:5`. Trace every DNS query the JVM makes when resolving `database`, explain why Java's DNS caching (`networkaddress.cache.ttl`) interacts with Kubernetes service endpoint changes, and describe what happens to existing connections when the database pod is replaced and its DNS entry changes — distinguishing the behaviour with and without `networkaddress.cache.ttl=0`.

**Q2.** You're debugging a production incident where some pods can resolve `myservice.default.svc.cluster.local` and others cannot, despite identical spec. Describe the complete diagnostic process: what you'd check in CoreDNS, what you'd examine in the failing pod's network namespace, how you'd verify the pod got valid DNS configuration from DHCP/CNI, and what common misconfigurations (hostNetwork: true, custom dnsPolicy, CNI misconfiguration) could cause partial DNS failure across pods.
