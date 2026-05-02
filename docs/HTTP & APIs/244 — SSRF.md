---
layout: default
title: "SSRF"
parent: "HTTP & APIs"
nav_order: 244
permalink: /http-apis/ssrf/
number: "0244"
category: HTTP & APIs
difficulty: ★★★
depends_on: HTTP, Networking, Cloud Infrastructure
used_by: Web APIs, Cloud-hosted Applications
related: SQL Injection, XSS, API Security, Cloud Metadata Service
tags:
  - security
  - ssrf
  - api
  - cloud
  - owasp
  - advanced
---

# 244 — SSRF (Server-Side Request Forgery)

⚡ TL;DR — SSRF is an attack where an attacker tricks a server into making HTTP requests to internal network resources or external URLs — using the server's privileged network position to access services that are unreachable from the internet, such as cloud instance metadata endpoints (AWS `169.254.169.254`) that expose IAM credentials; prevented by URL allowlisting, disabling redirects, and network-level egress controls.

| #244 | Category: HTTP & APIs | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | HTTP, Networking, Cloud Infrastructure | |
| **Used by:** | Web APIs, Cloud-hosted Applications | |
| **Related:** | SQL Injection, XSS, API Security, Cloud Metadata Service | |

### 🔥 The Problem This Solves (The Threat)

**THE ATTACK:**
A web application has a "fetch URL preview" feature: user submits a URL, the server
fetches that URL and returns a preview. Attacker submits:
`http://169.254.169.254/latest/meta-data/iam/security-credentials/`

This is the AWS EC2 instance metadata URL — accessible only from within an AWS instance,
not from the internet. The server (running on an EC2 instance) fetches this URL on the
attacker's behalf. Response includes the instance's IAM role credentials with
`Access Key`, `Secret Key`, and `Token`. Attacker now has AWS credentials equivalent
to the EC2 instance's permissions — granting access to S3 buckets, databases, Lambda
functions, and potentially the entire AWS account.

This is how the 2019 Capital One breach occurred ($80M fine, 100M customer records).
A misconfigured WAF on an EC2 instance was vulnerable to SSRF, allowing an attacker
to retrieve IAM credentials and access S3 buckets with stored personal data.

---

### 📘 Textbook Definition

**SSRF (Server-Side Request Forgery)** is a web security vulnerability (OWASP Top 10 #10
as of 2021 — its own category due to severity in cloud) in which an attacker causes
the server to make HTTP requests to a target of the attacker's choosing, using the
server's privileged network position. SSRF exploits the trust gap: the server is
inside the network boundary (can reach internal IPs, private subnets, and cloud
metadata services), while the attacker is outside. By manipulating a URL parameter
or any feature that causes the server to make outbound HTTP requests (fetching images,
link previews, webhook verification, PDF generation with external resources, XML
parsers), the attacker can: access internal services (databases, admin panels, key
vaults), read cloud instance metadata credentials, scan internal network ports
(port scanning via SSRF), and in some cases achieve Remote Code Execution via
vulnerable internal services.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SSRF makes the server act as a proxy to access internal or privileged resources on
the attacker's behalf — exploiting the server's trusted network position.

**One analogy:**

> SSRF is like a trusted employee (the server) being tricked into fetching files
> from the secure archive room (internal network) on behalf of an outsider.
> Security only checks WHO is making the request (the trusted employee, not the
> outsider who directed them). The outsider gets the confidential files without
> ever entering the secure room.

**One insight:**
SSRF is critically dangerous in cloud environments because cloud providers expose
an instance metadata HTTP endpoint (`169.254.169.254`) that returns IAM credentials,
user data, and other sensitive information. This endpoint is accessible only from
within the instance — but an SSRF vulnerability effectively moves the attacker inside.
The Capital One breach (2019) demonstrated this real-world impact at scale.

---

### 🔩 First Principles Explanation

**ATTACK VECTORS — HOW SSRF IS TRIGGERED:**

```
1. DIRECT URL PARAMETER:
   GET /api/fetch?url=http://169.254.169.254/latest/meta-data/

2. IMAGE/FILE FETCH:
   POST /api/import { "imageUrl": "http://internal-admin.company.internal/admin" }
   (Server downloads the "image" → actually fetches an internal admin page)

3. WEBHOOK URL REGISTRATION:
   POST /webhooks { "callbackUrl": "http://10.0.0.1:8080/actuator/env" }
   (Server POSTs to the webhook → fetches Spring Actuator on internal service)

4. PDF GENERATION:
   POST /api/render { "html": "<img src='http://169.254.169.254/...'>" }
   (Headless Chrome fetches the img src → retrieves metadata)

5. XML EXTERNAL ENTITY (XXE):
   XML parser processes external entity reference:
   <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
   → XML parser makes the HTTP request → SSRF + file disclosure

6. DNS REBINDING:
   attacker.com DNS: initially resolves to 93.184.216.34 (allowed)
   After server validates the domain (allowlisted): DNS rebinds to 192.168.1.1 (internal)
   Server's HTTP fetch uses the already-"validated" hostname but now gets internal IP
```

**CLOUD METADATA SERVICES (the crown jewels of SSRF):**

```
AWS EC2 Metadata:
  http://169.254.169.254/latest/meta-data/iam/security-credentials/
  Response:
  {
    "AccessKeyId": "ASIAxxxxx",
    "SecretAccessKey": "xxxxxxxx",
    "Token": "IQoJb3JpZ2luX2VjEA==...",
    "Expiration": "2024-01-01T12:00:00Z"
  }
  → These credentials work for the IAM role attached to the EC2 instance
  → Attacker can call AWS API: list S3 buckets, read secrets, invoke Lambda...

AWS IMDSv2 (mitigation — Session-oriented IMDS):
  Requires PUT request with a TTL header BEFORE GET:
  PUT http://169.254.169.254/latest/api/token
  X-aws-ec2-metadata-token-ttl-seconds: 21600
  → Returns token
  Then: GET http://169.254.169.254/latest/meta-data/
  X-aws-ec2-metadata-token: <token>

  SSRF via GET can't get the token (requires PUT first — different method)
  But: if SSRF can make PUT requests → still vulnerable
  Defense-in-depth: use IMDSv2 AND application-level URL controls

Azure Instance Metadata:
  http://169.254.169.254/metadata/instance?api-version=2021-02-01
  Metadata: true header required → reduces simple SSRF impact
  But: if app adds the header for "metadata" requests → still vulnerable

GCP Metadata:
  http://metadata.google.internal/computeMetadata/v1/
  Metadata-Flavor: Google header required (without it: 403)
```

**PREVENTION LAYERS:**

```
LAYER 1 — URL Validation (application level):
  Parse URL → extract hostname
  Resolve hostname to IP (DNS lookup)
  Check IP against blocklist:
    - 127.0.0.0/8 (loopback)
    - 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (private ranges)
    - 169.254.0.0/16 (link-local, incl. AWS metadata)
    - ::1/128, fc00::/7 (IPv6 private)
  Block if on blocklist

  DNS Rebinding counter: resolve DNS → check IP → make request with RESOLVED IP
  (not the hostname, to prevent rebinding attacks)

LAYER 2 — Network Policy (infrastructure level):
  Block EC2 → 169.254.169.254 outbound (security group / NACLs)
  Block EC2 → RFC1918 ranges (unless specific internal services needed)
  → Even if app has SSRF bug, network blocks the metadata access

LAYER 3 — IMDSv2 (AWS-specific):
  Enforce Instance Metadata Service v2 on all EC2 instances
  IMDS v2 tokens require PUT → harder for SSRF (but not impossible)
  → Defense layer, not complete fix

LAYER 4 — Principle of Least Privilege:
  EC2 instance IAM role: only give exact permissions needed
  → Even if attacker gets credentials, they can access only allowed resources
```

---

### 🧪 Thought Experiment

**SSRF IMPACT ESTIMATION FOR A CLOUD APP:**

```
Application: Public API on EC2 in a VPC
  - EC2 instance IAM role: S3 full access + DynamoDB full access + EC2 describe
  - Internal Kubernetes cluster on 10.0.0.0/16
  - Elasticsearch at 10.0.1.50:9200 (no auth, internal only)
  - Spring Actuator at http://k8s-pods.internal/actuator (internal only)

SSRF vulnerability in "fetch og-meta from URL" feature

Attacker steps:
  1. http://169.254.169.254/latest/meta-data/iam/security-credentials/
     → Gets IAM credentials for EC2 role
     → Exfiltrates all S3 bucket data, all DynamoDB tables (full database breach)

  2. http://10.0.1.50:9200/_all/_search?size=1000
     → Dumps all Elasticsearch index data (all user records, events, logs)

  3. http://k8s-pods.internal/actuator/env
     → Gets all Spring environment properties (database passwords, secret keys)

  4. Port scan: http://10.0.0.1:22, etc.
     → Time differences reveal which internal IPs have open ports
     → Maps internal network topology

IMPACT: Complete infrastructure compromise from a single SSRF bug in a URL preview feature.

PREVENTION:
  Network: block 169.254.169.254 in VPC security group → stops step 1
  Network: restrict EC2 → 10.0.0.0/16 to only needed services → stops steps 2-4
  Application: URL allowlist → only allow specific known-safe external domains → stops all
  IAM: EC2 role only needs S3 read for one bucket → limits step 1 blast radius
```

---

### 🧠 Mental Model / Analogy

> SSRF is like a VIP backstage pass exploit.
> You can't get backstage at a concert (internal network). But the event's server
> (website) has a backstage pass (trusted network position). If you can tell the
> server "go backstage and fetch me that document over there (internal service),"
> it will — because it has the pass, not you.
>
> Defense: tell the server "you only go backstage for these specific three things,
> not whatever a stranger tells you to fetch" (URL allowlist). Or: physically block
> the backstage door from the server's reach (network ACL).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
SSRF tricks your server into fetching URLs that an outsider couldn't access directly.
Since your server is inside your network, it can reach internal services. The attacker
uses your server like a puppet to reach places only your server can go.

**Level 2 — How to prevent it (junior developer):**
Validate URLs before making any outbound HTTP request. Block private/internal IP ranges.
Never pass user-supplied URLs directly to `HttpClient`, `RestTemplate`, or URL fetching
libraries without validation. Prefer explicit allowlists over blocklists.

**Level 3 — How it works (mid-level engineer):**
URL validation must happen AFTER DNS resolution, not before. Validate: scheme (https only),
resolved IP (block RFC1918 + 169.254.0.0/16 + 127.0.0.0/8 + IPv6 equivalent), port
(only 80/443). Resolve DNS yourself, then use the resolved IP in the HTTP request
(prevents DNS rebinding: hostname passes validation, later rebinds to internal IP
right before the HTTP request). Disable HTTP redirects or re-validate each redirect target
(a redirect to `http://169.254.169.254/...` would bypass initial URL validation).

**Level 4 — Why it's particularly dangerous in cloud (senior/staff):**
SSRF existed pre-cloud but was primarily useful for internal network scanning.
Cloud made it dramatically more impactful: every EC2/GCE/Azure VM has a link-local
metadata endpoint accessible via HTTP on a well-known IP, returning IAM credentials.
These credentials have real permissions in the cloud account — turning an SSRF in
a web app into a potential account takeover. AWS IMDSv2 (requiring PUT before GET)
is a partial mitigation but not complete (attacker with PUT SSRF capability can still
exploit). The defense-in-depth principle applies strongly: application-level URL
validation + network-level security groups blocking 169.254/link-local + IMDSv2 +
minimal IAM permissions. Each layer independently reduces impact even if others are
bypassed. SSRF is now OWASP Top 10 #10 as its own category (was previously under
injection in earlier lists) due to its cloud impact severity.

---

### ⚙️ How It Works (Mechanism)

```
CLASSIC SSRF CHAIN — AWS Metadata Theft:

Internet          Application Server (EC2)        AWS Metadata Service
    │                       │                       169.254.169.254
    │                       │
    │ GET /api/preview       │
    │ ?url=http://169.254.  │
    │     169.254/latest/   │
    │     meta-data/iam/    │
    │     security-creds/   │
    ├──────────────────────►│
    │                       │
    │                       │ HTTP GET http://169.254.169.254/latest/meta-data/...
    │                       ├───────────────────────────────────────────────────►│
    │                       │                                                    │
    │                       │◄─ 200: { AccessKeyId: "ASIAxxx", Secret: "..." } ─┤
    │                       │
    │◄── 200: (page preview)│
    │    { "preview": "     │
    │     AccessKeyId:ASIAxxx│
    │     SecretAcc..." }   │
    │                       │
Attacker now holds          │
AWS IAM credentials         │
  → calls AWS API directly  │
```

---

### 🔄 The Complete Picture — End-to-End Prevention

```java
// SECURE URL FETCHING with SSRF prevention

@Component
public class SafeUrlFetcher {

    private static final List<String> ALLOWED_SCHEMES = List.of("https", "http");
    private static final List<InetAddressValidator> BLOCKED_RANGES = buildBlockedRanges();

    public String fetch(String rawUrl) throws SSRFException {
        URI uri = parseAndValidate(rawUrl);
        InetAddress resolvedIp = resolveAndCheck(uri.getHost());

        // CRITICAL: use resolved IP, not hostname (prevents DNS rebinding)
        // Rebuild URL with resolved IP to force use of pre-validated IP
        return httpClient.fetch(uri, resolvedIp);
    }

    private void validateScheme(URI uri) throws SSRFException {
        if (!ALLOWED_SCHEMES.contains(uri.getScheme().toLowerCase())) {
            throw new SSRFException("Scheme not allowed: " + uri.getScheme());
            // Block: file://, gopher://, dict://, etc.
        }
    }

    private InetAddress resolveAndCheck(String hostname) throws SSRFException {
        try {
            InetAddress ip = InetAddress.getByName(hostname);
            if (ip.isLoopbackAddress() ||
                ip.isSiteLocalAddress() ||
                ip.isLinkLocalAddress() ||
                ip.isAnyLocalAddress() ||
                isMetadataAddress(ip)) {
                throw new SSRFException("Blocked internal address: " + ip);
            }
            return ip;
        } catch (UnknownHostException e) {
            throw new SSRFException("Cannot resolve hostname");
        }
    }

    private boolean isMetadataAddress(InetAddress addr) {
        // Block 169.254.0.0/16 (AWS/Azure/GCP metadata)
        byte[] bytes = addr.getAddress();
        return bytes[0] == (byte)169 && bytes[1] == (byte)254;
    }
}
```

---

### ⚖️ Comparison Table

| Defense                        | Layer          | Stops                          | Notes                                                        |
| ------------------------------ | -------------- | ------------------------------ | ------------------------------------------------------------ |
| **URL allowlist**              | Application    | All non-allowlisted targets    | Most restrictive; broken if requirements need arbitrary URLs |
| **IP blocklist + DNS resolve** | Application    | RFC1918 + metadata + loopback  | Must validate resolved IP, not hostname                      |
| **Network security groups**    | Infrastructure | Metadata + internal ranges     | Defense-in-depth; stops at network level                     |
| **IMDSv2 (AWS)**               | Cloud          | Unauthenticated metadata fetch | PUT requirement; reduces but doesn't eliminate risk          |
| **Minimal IAM role perms**     | Cloud          | Limits blast radius            | Even with credential theft: limited access                   |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                              |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Validating the URL hostname is enough         | DNS rebinding: hostname passes validation, later resolves to internal IP. Must validate the RESOLVED IP and use it in the request                                    |
| SSRF only affects cloud environments          | Pre-cloud SSRF enables internal network scanning, accessing unprotected internal services (Redis, Mongo with no-auth), admin interfaces                              |
| Blocklisting private ranges covers everything | Cover ALL: 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16, ::1/128, fe80::/10. Also: 0.0.0.0 (often means 127.0.0.1 in some implementations) |
| HTTPS requirement prevents SSRF               | `https://169.254.169.254/` is still SSRF — the scheme doesn't prevent internal targets                                                                               |

---

### 🚨 Failure Modes & Diagnosis

**SSRF via Image URL in User Profile**

Symptom:
Users can upload a profile photo by URL. One day: unusual access patterns in AWS
CloudTrail — the EC2 instance's IAM role queried S3 ListBuckets for buckets not
related to the application. Investigation reveals the requests came from the
web application servers.

Root Cause:
Profile photo URL feature fetches user-provided URL without SSRF validation.
Attacker submitted `http://169.254.169.254/latest/meta-data/iam/security-credentials/ServiceRole`
→ App fetched URL → response (JSON with IAM credentials) stored as "profile photo"
→ Attacker retrieved it at their profile URL → used extracted credentials.

Diagnostic:

```
# Check CloudTrail for unusual IAM activity from EC2 instance role:
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventSource,AttributeValue=s3.amazonaws.com \
  --start-time "2024-01-01T00:00:00Z"
# Look for: ListBuckets, GetObject for unexpected S3 buckets, from EC2 instance ARN

# Application logs: look for requests to 169.254.x.x or 10.x.x.x ranges
# from the image URL fetcher component

# Immediate containment: rotate IAM credentials for the EC2 role
# (revoke existing session tokens via IAM role policy changes)
```

---

### 🔗 Related Keywords

- `SQL Injection` — analogous server-side injection attack targeting databases
- `XSS` — client-side injection vs SSRF (server-side request manipulation)
- `Cloud Metadata Service` — the primary high-value target for SSRF in cloud
- `DNS Rebinding` — the bypass technique that defeats hostname-only SSRF validation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Server makes HTTP requests to attacker-  │
│              │ chosen targets using its trusted position │
├──────────────┼───────────────────────────────────────────┤
│ CROWN JEWELS │ AWS 169.254.169.254 → IAM credentials    │
│ TARGET       │ internal Redis/MongoDB (no auth)          │
│              │ internal admin panels, k8s API            │
├──────────────┼───────────────────────────────────────────┤
│ PREVENT      │ URL allowlist (best) OR IP blocklist      │
│              │ + resolve DNS BEFORE checking IP          │
│              │ + Disable redirects (or re-validate)     │
├──────────────┼───────────────────────────────────────────┤
│ CLOUD BLOCK  │ SG/NACL: block 169.254.169.254 outbound  │
│              │ Enforce IMDSv2; minimal IAM role          │
├──────────────┼───────────────────────────────────────────┤
│ DNS REBIND   │ Resolve DNS → use RESOLVED IP in request │
│ DEFENSE      │ (not hostname) to prevent rebinding       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Attacker directs server to fetch        │
│              │ internal privileged resources"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SQL Injection → XSS → Cloud IAM → DNS    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A SaaS product needs to support user-defined webhook URLs AND let users import data from arbitrary URLs (CSV import from S3, public APIs, FTP). Both features require the server to make HTTP requests to user-provided URLs. Design an SSRF mitigation architecture that: allows legitimate HTTP requests to the public internet (user case 1: webhooks), allows legitimate fetches from controlled external sources (user case 2: imports), blocks all private/internal targets, is robust against DNS rebinding, and handles the operational complexity of maintaining an IP blocklist that must cover new cloud provider metadata ranges.
