---
id: DST-057
title: Distributed Systems Security Threats
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-009, DST-021
used_by: []
related: DST-009, DST-021, DST-025
tags:
  - distributed
  - security
  - mtls
  - zero-trust
  - ssrf
  - confused-deputy
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/distributed-systems/security-threats/
---

⚡ TL;DR - Distributed systems introduce security
threats absent in monoliths: inter-service traffic
is a new attack surface requiring mTLS (mutual TLS)
to prevent impersonation; confused deputy allows a
compromised service to abuse its elevated privileges;
SSRF (Server-Side Request Forgery) exploits internal
network trust; zero-trust architecture treats every
service call as untrusted regardless of network position.

---

### 📋 Entry Metadata

| #057 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Microservices Fundamentals, Service Mesh | |
| **Used by:** | N/A (cross-cutting security concern) | |
| **Related:** | Microservices, Service Mesh, Rate Limiting | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A monolith has one attack surface: the HTTP API.
Internally: all code runs in the same process.
A distributed system with 20 services has 20 API
surfaces, 20×19 inter-service call paths, N internal
databases, and a message bus. Most of these
communication paths are trusted by default ("it's
internal traffic, it must be safe"). An attacker
who compromises service A (via a dependency CVE)
can now call service B, C, D... as a legitimate
internal service. No authentication required. Full
access to all data across the system.

The expansion of attack surface in distributed
systems is not linear - it is combinatorial.
Securing the perimeter (API gateway) is insufficient
when the interior is completely open.

---

### 📘 Textbook Definition

**Distributed systems security** addresses the
unique threat model created by inter-service
communication, shared infrastructure, and expanded
attack surface in distributed architectures.

**Key threats:**
- **Man-in-the-Middle (MITM) on inter-service calls:**
  traffic between services intercepted or modified
- **Confused deputy:** a service with elevated
  privileges is tricked into performing unauthorized
  actions on behalf of a less-privileged caller
- **SSRF (Server-Side Request Forgery):** an attacker
  controls what URL a service requests, using the
  service's internal network access as a proxy
- **Credential leakage:** secrets in environment
  variables, logs, or configuration
- **Privilege escalation through service chaining:**
  compromised service A calls privileged service B

**Defense model:** Zero-trust - never trust based
on network position alone; always verify identity,
authenticate every call, authorize every action.

---

### ⏱️ Understand It in 30 Seconds

```
MONOLITH SECURITY:
  Only one attack surface: external HTTP API.
  Internal code calls: no auth needed (same process).

DISTRIBUTED SECURITY THREAT MODEL:
  Each service = potential attacker.
  Each service-to-service call = potential attack vector.

THREATS:
  MITM: Service A → (attacker) → Service B
        Attacker reads/modifies traffic.
        Fix: mTLS (both services verify each other's cert).

  CONFUSED DEPUTY:
        User → Service A (low trust) → Service B (high
          trust)
        Service A passes user's request to B without
        re-verifying authorization at B.
        B trusts A and performs privileged operation.
        Fix: B verifies the ORIGINAL caller's
          identity/scope.

  SSRF:
        User → Service A: "fetch URL http://..."
        Service A fetches http://169.254.169.254/
        (AWS metadata endpoint - returns instance
          credentials!)
        Fix: Allowlist URLs; deny internal IP ranges.
```

---

### 🔩 First Principles Explanation

**MUTUAL TLS (mTLS) FOR SERVICE AUTHENTICATION:**

```
STANDARD TLS: Client verifies server's certificate.
  Server has certificate. Client checks it.
  Server does NOT verify client identity.
  Used for: browsers connecting to websites.

mTLS: Both parties verify each other's certificate.
  Server has cert. Client has cert.
  Both verify. Both are authenticated.
  Used for: service-to-service authentication.

WHY mTLS:
  Without: "Internal network = trusted" assumption.
  If attacker gains access to internal network
  (lateral movement after initial compromise),
  they can impersonate any service.
  
  With mTLS: attacker needs the private key of a
  legitimate service certificate to communicate.
  Even inside the network perimeter, identity
  must be proven cryptographically.

CERTIFICATE MANAGEMENT:
  SPIFFE (Secure Production Identity Framework
  For Everyone): standard for workload identity.
  SVID (SPIFFE Verifiable Identity Document) =
  certificate with identity like:
    spiffe://cluster.local/ns/orders/sa/order-service
  Issued automatically by SPIRE (SPIFFE Runtime Env).
  Rotated automatically (short TTL: hours/days).
  Service Mesh (Istio, Linkerd) handles mTLS
  transparently - services need no code change.
```

**CONFUSED DEPUTY:**

```python
# BAD: Service B trusts Service A to enforce authorization
# (confused deputy vulnerability)

# Service A (API layer, called by users):
def api_get_user_data(user_id: str,
                      requester_token: str) -> dict:
    # Service A checks if requester has access:
    if not check_access(requester_token, user_id):
        raise Unauthorized()
    
    # Calls Service B with user_id only:
    return service_b_client.get_user_data(user_id)

# Service B (internal data service):
def get_user_data(user_id: str) -> dict:
    # WRONG: Trusts that Service A already checked auth.
    # Any caller claiming to be Service A can get ANY user's data.
    # If Service A is compromised: attacker gets all users.
    return db.get_user(user_id)
```

```python
# GOOD: Service B verifies original caller's authorization

# Service A passes original caller's token to Service B:
def api_get_user_data(user_id: str,
                      requester_token: str) -> dict:
    # Service A checks first (defense in depth):
    if not check_access(requester_token, user_id):
        raise Unauthorized()
    
    # Pass original caller context to Service B:
    return service_b_client.get_user_data(
        user_id=user_id,
        caller_token=requester_token  # Original context
    )

# Service B re-verifies independently:
def get_user_data(user_id: str, caller_token: str) -> dict:
    # Service B does NOT trust Service A's authorization.
    # Service B verifies the ORIGINAL caller's token:
    if not check_access(caller_token, user_id):
        # Even if Service A approved, B double-checks.
        raise Unauthorized()
    return db.get_user(user_id)

# ALTERNATIVE: Pass original caller's JWT claim forward.
# Service B extracts scope/sub from JWT and checks.
# Centralizes auth logic in auth service.
```

**SSRF PREVENTION:**

```python
import ipaddress
import urllib.parse
from typing import Optional
import httpx

BLOCKED_PRIVATE_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # AWS metadata
    ipaddress.ip_network("::1/128"),         # IPv6 loopback
]

ALLOWED_SCHEMES = {"https"}
ALLOWED_DOMAINS: set[str] = {
    "api.trusted-partner.com",
    "cdn.trusted-cdn.com",
}

def safe_fetch(url: str) -> bytes:
    """Fetch external URL with SSRF protection."""
    parsed = urllib.parse.urlparse(url)

    # Check scheme:
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(
            f"Scheme {parsed.scheme} not allowed. "
            f"Use HTTPS only."
        )

    # Check domain against allowlist:
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError(
            f"Domain {parsed.netloc} not in allowlist."
        )

    # DNS resolution check for SSRF bypass:
    # (Some attacks use DNS to resolve allowed domain
    # to a private IP. Re-check after DNS resolution.)
    import socket
    resolved_ip = socket.gethostbyname(parsed.netloc)
    ip = ipaddress.ip_address(resolved_ip)
    for blocked_range in BLOCKED_PRIVATE_RANGES:
        if ip in blocked_range:
            raise ValueError(
                f"Resolved IP {resolved_ip} is in "
                f"blocked private range."
            )

    # Safe to fetch:
    response = httpx.get(url, timeout=10.0,
                         follow_redirects=False)
    return response.content
```

**ZERO-TRUST CHECKLIST:**

```
ZERO-TRUST PRINCIPLES:

1. AUTHENTICATE EVERY SERVICE CALL
   - mTLS between all services
   - SPIFFE/SPIRE for certificate management
   - Service mesh (Istio/Linkerd) for enforcement

2. AUTHORIZE EVERY ACTION
   - Not just "is this service allowed to call me?"
   - But: "is THIS action on THIS resource allowed?"
   - Carry original user context through calls

3. LEAST PRIVILEGE
   - Service A can call Service B but not Service C
   - Network policies (k8s NetworkPolicy) enforce
   - IAM roles per service (not shared credentials)

4. ENCRYPT ALL TRAFFIC
   - No plaintext traffic even on internal network
   - TLS 1.2 minimum; TLS 1.3 preferred
   - mTLS for service-to-service

5. SECRETS MANAGEMENT
   - No secrets in env vars or config files
   - HashiCorp Vault or AWS Secrets Manager
   - Rotate automatically; never log

6. AUDIT ALL CALLS
   - Structured access logs with caller identity
   - Anomaly detection: service calling unusual APIs
```

---

### 🧠 Mental Model / Analogy

> Traditional network security is like a castle with
> a moat: the perimeter is hard to breach, but once
> inside, everyone trusts everyone. Zero-trust is
> like a secure building where every door has a
> badge reader - even internal doors. Getting into
> the lobby doesn't let you into the server room.
> Every door checks: "Who are you? Are you authorized
> to be in THIS room right now?" In distributed
> systems: entering the internal network (getting
> past the API gateway) doesn't grant access to
> every service. Every service verifies: "Who is
> calling? Do they have a valid certificate? Are
> they authorized for this specific operation?"

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The new attack surface:**
A monolith has one API. 20 microservices have 20
APIs. Every service-to-service call is a potential
attack vector. Simply being "inside the network"
should not grant trust.

**Level 2 - mTLS is the foundation:**
mTLS ensures both parties in a service call are
authenticated by certificate. A compromised service
cannot impersonate another service without stealing
its private key. Service mesh (Istio, Linkerd) makes
this transparent - no code change needed.

**Level 3 - Confused deputy is the authorization bug:**
Authentication (who are you?) is not the same as
authorization (what can you do?). A service correctly
authenticated can still perform unauthorized actions
on behalf of another caller (confused deputy). Fix:
pass and re-verify the original caller's context
at every service hop.

**Level 4 - SSRF exploits internal trust:**
SSRF is particularly dangerous in cloud environments:
AWS, GCP, Azure expose instance metadata (including
credentials) via 169.254.169.254. An SSRF in any
service can exfiltrate cloud credentials. Defense:
allowlist URLs, validate DNS resolution, use IMDSv2
(requires token, not vulnerable to SSRF).

**Level 5 - Zero-trust as architecture:**
Zero-trust is not a product - it is an architectural
approach. Implementation requires: SPIFFE for identity,
service mesh for mTLS enforcement, IAM for per-service
roles, secrets manager for credential rotation,
NetworkPolicy for lateral movement prevention, and
audit logs for anomaly detection. Each layer
independently reduces the blast radius of a
compromise.

---

### 💻 Code Example

**Credential Leakage: Wrong vs Right**

```python
# BAD: Credentials in environment variables,
# logged or exposed in error messages

import os

def connect_to_db():
    password = os.environ["DB_PASSWORD"]
    conn = db.connect(
        host="db.internal",
        password=password
    )
    return conn

def process_request(user_id: str):
    try:
        conn = connect_to_db()
        return conn.query(user_id)
    except Exception as e:
        # BAD: Exception message may contain password!
        logger.error(f"DB error: {e}")
        # If the exception includes the connection string
        # (many JDBC drivers do), password is in the log.
        raise
```

```python
# GOOD: Secrets from Vault; sanitize errors

import hvac  # HashiCorp Vault client
from contextlib import contextmanager

def get_db_credentials() -> tuple[str, str]:
    """Fetch credentials from Vault (rotated automatically)."""
    vault_client = hvac.Client(
        url="https://vault.internal:8200",
        token=os.environ["VAULT_TOKEN"]  # Only Vault token
    )
    # Vault dynamic secrets: credentials valid for 1 hour
    secret = vault_client.secrets.database.generate_credentials(
        name="my-db-role"
    )
    return (
        secret["data"]["username"],
        secret["data"]["password"]
    )

@contextmanager
def db_connection():
    """Get DB connection with Vault-rotated credentials."""
    username, password = get_db_credentials()
    conn = None
    try:
        conn = db.connect(host="db.internal",
                          user=username,
                          password=password)
        yield conn
    except db.AuthenticationError:
        # GOOD: Log the error type, NOT the credentials
        logger.error("Database authentication failed",
                     extra={"db_host": "db.internal"})
        raise DatabaseConnectionError(
            "Could not authenticate to database"
        )
        # Never include credentials in error messages
    finally:
        if conn:
            conn.close()

def process_request(user_id: str):
    with db_connection() as conn:
        return conn.query(user_id)
```

---

### ⚖️ Comparison Table

| Threat | Attack Vector | Impact | Defense |
|---|---|---|---|
| **MITM** | Internal network access | Traffic intercept/modify | mTLS between all services |
| **Confused deputy** | Compromised service A | Unauthorized access via service B's privilege | Re-verify original caller at each service |
| **SSRF** | User-controlled URL | Cloud credential exfiltration | URL allowlist; IP blocklist |
| **Credential leakage** | Logs, config, error messages | Full system compromise | Secrets manager; sanitize errors |
| **Lateral movement** | Compromised service | Access to all internal services | NetworkPolicy; zero-trust |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Internal network is trusted" | The most dangerous assumption in distributed system security. Internal network compromise via lateral movement is how most major breaches escalate. mTLS + NetworkPolicy enforces zero-trust internally. |
| "HTTPS between services is sufficient" | One-way TLS verifies the server but not the client. Any caller can make HTTPS requests to a service. mTLS verifies BOTH sides - the service proves its identity to its caller AND verifies the caller's identity. |
| "Service mesh handles all security" | Service mesh handles mTLS and network policy enforcement. It does NOT handle application-level authorization (confused deputy), input validation (SSRF), or secrets management. Defense in depth requires all layers. |
| "Short-lived tokens expire before being exploited" | Short-lived tokens reduce the window of compromise (minutes vs months). But an attacker who exfiltrates a token can use it immediately. Short-lived tokens help with stale credential risk (ex-employee, leaked config), not real-time theft. |

---

### 🚨 Failure Modes & Diagnosis

**SSRF Attack via User-Controlled URL**

**Symptom:** Unusual outbound requests from a
service to internal IP ranges (169.254.169.254,
10.x.x.x). Audit logs show: service fetched
a metadata URL. Cloud credentials were accessed.

**Diagnosis:**
```bash
# Check for SSRF indicators in application logs:
grep -E "169\.254\.169\.254|169\.254\.\d+\.\d+" \
  /var/log/app/*.log

# Check network flow logs (AWS VPC Flow Logs):
# Look for connections FROM app subnet TO 169.254.169.254
# (AWS metadata) or to other private ranges

# AWS: check if instance metadata was accessed:
aws cloudtrail lookup-events \
  --lookup-attributes \
  AttributeKey=EventName,AttributeValue=AssumeRole \
  --start-time 2024-03-15T00:00:00Z
# Unexpected AssumeRole calls = potential SSRF compromise

# Check if IMDSv2 (token-required) is enforced:
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].{
    ID:InstanceId,
    IMDSv2:MetadataOptions.HttpTokens
  }'
# Should be "required" not "optional"
```

**Fix:**
1. Enable IMDSv2 (token-required) on all EC2 instances
   - prevents SSRF from accessing metadata without a token.
2. Add URL allowlist validation before any user-controlled
   fetch operations.
3. Add network egress rules: deny outbound to
   169.254.169.254 from application subnets.
4. Rotate any potentially compromised credentials
   immediately.

---

### 🔗 Related Keywords

**Prerequisites:** `Microservices Fundamentals`
(DST-009), `Service Mesh` (DST-021)

**Related:** `Rate Limiting` (DST-025)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ THREATS     │ MITM, Confused Deputy, SSRF, Cred Leak    │
├─────────────┼───────────────────────────────────────────┤
│ mTLS        │ Both sides verify cert; prevents MITM     │
│             │ Service mesh (Istio/Linkerd) → transparent│
├─────────────┼───────────────────────────────────────────┤
│ CONFUSED    │ Service B must verify original caller's   │
│ DEPUTY FIX  │ token, not just trust Service A           │
├─────────────┼───────────────────────────────────────────┤
│ SSRF FIX    │ URL allowlist; block 169.254.169.254;     │
│             │ IMDSv2 (AWS); DNS re-validate after resolv│
├─────────────┼───────────────────────────────────────────┤
│ ZERO TRUST  │ Authenticate + authorize every call,      │
│ PRINCIPLES  │ regardless of network position            │
├─────────────┼───────────────────────────────────────────┤
│ ONE-LINER   │ "Zero-trust: the network is not trusted   │
│             │  even inside the perimeter."              │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The confused deputy problem and its solution -
propagate and re-verify original caller context -
embodies the principle of "don't trust claims that
pass through untrusted intermediaries." This extends
beyond service-to-service calls: in OAuth 2.0,
the access token represents the original user's
grant and is passed through every API call to enforce
the user's actual permissions. In database row-level
security, the application passes the user's identity
to the database which enforces access. In message
queues, the original producer's identity should
be in the message metadata so that the consumer
can enforce the right policy. The pattern: never
accept authorization claims from a caller that
cannot prove it is the original authority - always
carry original context and verify at the resource
being accessed.

---

### 💡 The Surprising Truth

The confused deputy problem was first described by
Norm Hardy in 1988 in the context of file system
access control in early operating systems - but
it remains one of the most common security bugs in
modern microservices architectures, nearly 40 years
later. The Ethereum DAO hack (2016, $50M stolen) was
essentially a confused deputy at the smart contract
level: the contract trusted a malicious recursive
call from itself, not realizing the context had been
manipulated. The SSRF attack on Capital One in 2019
used an SSRF vulnerability in a web application
firewall to access the AWS metadata endpoint and
obtain credentials - exposing 100 million customers'
data. These are not theoretical bugs: they are the
most practically exploited vulnerabilities in
distributed and cloud architectures.

---

### ✅ Mastery Checklist

1. [IDENTIFY] For a 3-service system (user-facing
   API, order service, payment service), identify
   all potential confused deputy vulnerabilities.
   How does each service need to handle caller context?
2. [IMPLEMENT] Write a URL validation function that
   prevents SSRF by checking the allowlist and
   blocking private IP ranges after DNS resolution.
3. [COMPARE] One-way TLS vs mTLS: when does one-way
   TLS become insufficient? What specific threat
   does mTLS prevent that one-way TLS misses?
4. [DESIGN] You are deploying 5 services on
   Kubernetes. Design the security architecture:
   which components handle mTLS, secrets, network
   policy, and audit logging?
5. [AUDIT] Given an application that fetches user-
   provided URLs, describe the steps to check for
   and remediate SSRF vulnerabilities.
