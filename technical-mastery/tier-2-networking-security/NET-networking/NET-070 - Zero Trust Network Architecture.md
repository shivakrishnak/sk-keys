---
id: NET-070
title: "Zero Trust Network Architecture"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-052, NET-062
used_by: NET-075, NET-083
related: NET-052, NET-062, NET-075, NET-083
tags:
  - networking
  - zero-trust
  - security
  - beyondcorp
  - mtls
  - identity
  - micro-segmentation
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/net/zero-trust-network-architecture/
---

**⚡ TL;DR** - Zero Trust: "never trust the network,
always verify the identity." Replace the castle-and-moat
model (trust everything inside the perimeter) with:
authenticate and authorize every request regardless of
network location. Core primitives: identity-based access
(not IP-based), device posture checking, mTLS for
service-to-service, least-privilege micro-segmentation.
BeyondCorp (Google) pioneered this in 2014. Now the
standard model for any post-perimeter organization.

| #070 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | Network Segmentation (NET-052), Service Mesh (NET-062) | |
| **Used by:** | Build a Secure Network Platform (NET-075), Networking Career Paths (NET-083) | |
| **Related:** | Network Segmentation, Service Mesh, Build a Secure Network Platform, Networking Career Paths | |

---

### 🔥 Why the Old Model Fails

```
Traditional perimeter model:
  Firewall: everything outside is untrusted
  LAN: everything inside is implicitly trusted
  Result: once an attacker gets past the firewall,
          they move freely (lateral movement)
  
  Example: phishing attack → employee laptop compromised
  Attacker: now inside the network
  Old model: laptop can reach any internal database
  Zero Trust: laptop must still authenticate per resource

The SolarWinds attack (2020) is the perfect example:
  SolarWinds software: trusted (installed by IT teams)
  Software update: installed on thousands of internal machines
  Attacker: "inside" on thousands of trusted machines
  Old model: had full internal access to all systems
  Zero Trust: each resource access requires identity + context
              device posture: is it actually healthy?
              lateral movement blocked even with valid credentials
```

---

### 🧠 Intuition: The Five Principles

```
1. Verify explicitly:
   Never assume "this IP is from our internal network"
   Verify: who is making this request? (identity)
   Verify: from what device? (device posture)
   Verify: is the device healthy? (no malware, patched)

2. Use least-privilege access:
   Access only what is needed for the job
   Temporary credentials: expire automatically
   No "read all databases" - specific per-resource grants

3. Assume breach:
   Design for "when (not if) someone gets in"
   Micro-segment: breach of one service ≠ access to others
   Audit everything: logs of every access attempt

4. Verify device posture:
   Corporate laptop (MDM enrolled, patched): full access
   Personal laptop: lower trust level, limited access
   Unknown device: no access or read-only public only

5. Network location is not trust:
   Home network, office network, cloud VPC = same treatment
   VPN gives network access but NOT elevated trust
   (common misconception: "on VPN = trusted")
```

---

### ⚙️ The BeyondCorp Model (Google)

```
Google's original paper (2014): "BeyondCorp: A New
Approach to Enterprise Security"
Key insight: Google moved from VPN model to:
  Access Proxy: all requests go through a gateway
  No direct access to internal resources (even from corp LAN)
  Gateway: checks identity + device posture for every request

Components:
  1. Identity Provider (IdP): Google Workspace, Okta, Azure AD
     Issues: JWT tokens after authentication
     Includes: group membership, role claims
     
  2. Device Inventory: who owns this device? Is it managed?
     MDM (Mobile Device Management): enrollment proof
     Certificate on device: issued at enrollment
     
  3. Access Proxy: receives all requests (like a reverse proxy)
     Checks: is this user authenticated? Valid JWT?
     Checks: device certificate present and valid?
     Checks: policy allows this user+device to access this resource?
     
  4. Policy Engine: evaluates all the above together
     If: user is in group "engineers" + device is managed
         + accessing "internal-app.corp.com"
     Then: allow
     
  5. Logging: every access decision logged
     Who, what resource, what device, what time, allow/deny

Modern equivalents:
  Google BeyondCorp Enterprise: commercial product
  Cloudflare Access: same model as a service
  Tailscale: zero trust VPN alternative (WireGuard-based)
  AWS IAM + STS: identity-based (not network-based) access
  Teleport: SSH and Kubernetes zero trust access
```

---

### ⚙️ Service-to-Service: mTLS + SPIFFE

```
Zero trust for microservices (not human users):
  Problem: Service A talks to Service B
  Old model: both in same network, no authentication
  Zero Trust: service A must prove its identity to service B

SPIFFE (Secure Production Identity Framework):
  Standard for workload identity in distributed systems
  SPIFFE Verified Identity Document = SVID
  Format: X.509 certificate with URI SAN:
  spiffe://cluster.local/ns/payment/sa/checkout-service
  
  This identity: reflects what the workload IS
  (not which IP it comes from, which can change with K8s)

mTLS with SPIFFE:
  Istio issues SVID certificates automatically per service account
  Envoy sidecar: presents SVID to all outgoing connections
  Envoy sidecar: verifies peer's SVID on all incoming connections
  
  Authorization policy enforces identity:
```

```yaml
# Only allow payment-service to call billing-service /charge:
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: billing-authz
  namespace: payment
spec:
  selector:
    matchLabels:
      app: billing
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/payment/sa/checkout"
      to:
        - operation:
            paths: ["/charge"]
            methods: ["POST"]
```

```
Result:
  Even if an attacker compromises a pod in the same namespace,
  that pod cannot call billing-service /charge
  (it doesn't have the checkout service account identity)
  
  Certificate rotation: Istio rotates every 24 hours
  Compromise window: limited to certificate lifetime
```

---

### ⚙️ Human Access: Zero Trust vs VPN

```
Traditional VPN:
  Employee connects to VPN → gets "inside" network IP
  "Inside" IP: can reach any internal resource
  Problem: VPN = full internal access
  Attacker steals VPN credentials → full internal access
  
Zero Trust for humans:
  Employee connects to Access Proxy (Cloudflare Access, Teleport)
  Proxy: checks identity (SSO login, MFA required)
  Proxy: checks device certificate (is this a company device?)
  Proxy: checks policy ("does this user's role allow /admin?")
  Employee: only sees resources they are authorized for
  No network access to everything "behind the VPN"

Implementation with Cloudflare Access:
  Application: internal-app.corp.com
  Route: DNS → Cloudflare Access → Cloudflare Tunnel → your app
  User: browser → Cloudflare Access (SSO login + device check)
       → if allowed → Cloudflare edge → your app over encrypted tunnel
  
  What the user sees: a login flow (SSO), then the app
  What changed: no VPN client needed, device posture checked
  
Teleport (for SSH and Kubernetes):
  SSH session: user authenticates with SSO
  Teleport: issues short-lived SSH certificate (12-24 hours)
  Certificate: includes user identity and permissions
  Every SSH command: logged and auditable
  No static SSH keys anywhere (major attack surface eliminated)
  
  kubectl access: same model
  User: kubectl exec → Teleport → K8s RBAC check → allowed/denied
  Every kubectl command: logged
```

---

### ⚙️ Wrong vs Right: IP-Based Trust

```python
# BAD: trusting network location (IP) as authentication
from flask import request, abort

TRUSTED_INTERNAL_IPS = ["10.0.0.0/8", "192.168.0.0/16"]

def require_internal_network():
    client_ip = request.remote_addr
    # Checks if IP is "internal" - assumes internal = trusted
    if not is_internal(client_ip):
        abort(403)
    # If internal: full access to admin endpoints
    return True

@app.route("/admin/users")
def admin_users():
    require_internal_network()  # BAD: IP-based trust
    return get_all_users()

# Problems:
# 1. Any compromised internal machine has admin access
# 2. IP spoofing is possible in some network configs
# 3. Kubernetes: pod IPs change, IP-based rules break
# 4. Cloud: private IPs can belong to many services

# GOOD: identity-based authentication + authorization
import jwt
from functools import wraps

def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            try:
                claims = jwt.decode(
                    token,
                    options={"verify_signature": True},
                    algorithms=["RS256"],
                    audience="internal-api"
                )
                if role not in claims.get("roles", []):
                    abort(403)
            except jwt.InvalidTokenError:
                abort(401)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/admin/users")
@require_role("admin")  # identity-based check
def admin_users():
    return get_all_users()

# Token: issued by IdP (Okta, Cognito) after SSO login
# Verified: using IdP's public key
# Works: from any network (VPN or not)
# Auditable: user identity in every request log
```

---

### 📐 Maturity Levels

```
Zero Trust is a journey, not a binary state:

Level 1 - Basics (3-6 months):
  [ ] MFA enforced for all users
  [ ] Privileged Access Management (no shared admin accounts)
  [ ] Inventory of all applications and who can access them
  [ ] Audit logging enabled
  
Level 2 - Identity-Based Access (6-12 months):
  [ ] SSO for all internal applications
  [ ] VPN replaced or reduced for specific use cases
  [ ] Device management (MDM) for corporate devices
  [ ] Least-privilege review: who actually needs what access?
  
Level 3 - Service-to-Service (12-18 months):
  [ ] Service mesh with mTLS for microservices
  [ ] SPIFFE identity for workloads
  [ ] AuthorizationPolicy per service (not just network-level ACLs)
  [ ] Short-lived credentials for all services (AWS IAM roles, etc.)
  
Level 4 - Continuous Verification (18-24 months):
  [ ] Continuous device posture check (not just at login time)
  [ ] Anomaly detection: "this user usually accesses Europe, now Asia"
  [ ] Just-in-time access (temporary elevated access, auto-expires)
  [ ] Full audit trail with correlation IDs
  
Level 5 - Complete Coverage:
  [ ] All resources behind access proxy
  [ ] No implicit trust anywhere (even localhost)
  [ ] Regular access reviews (automated remove stale access)
  [ ] Zero standing privileges (everything temporary)
  
Most organizations: Level 2-3 is realistic and provides 80%
of the security value
```

---

### 🧭 Decision Guide

```
When to invest in Zero Trust:

High-value triggers:
  Remote workforce > 50%: VPN model becomes unmanageable
  Compliance requirement (SOC 2, FedRAMP): requires explicit
    access controls and audit logs
  Post-breach: after any security incident, rebuild on ZT model
  Cloud-first: no physical perimeter → ZT fits naturally
  Microservices at scale: service mesh mTLS is ZT for services

Starting point recommendation:
  Don't boil the ocean. Start with:
  1. Enforce MFA everywhere (immediate win, 1-2 weeks)
  2. Deploy SSO (Okta, Google Workspace) for all apps
  3. Replace VPN for web apps with Cloudflare Access or similar
     (keeps VPN for legacy systems only)
  4. Service mesh mTLS for new microservices
  
  This gets you to Level 2 with manageable effort.
  
Cost considerations:
  Free: SPIFFE, Teleport (open source), WireGuard, iptables
  Paid: Cloudflare Access, BeyondCorp Enterprise, Zscaler
  Cost of breach: average $4.5M (IBM 2023 report)
  Zero trust reduces lateral movement damage significantly
  
What it does NOT solve:
  Phishing → ZT helps (MFA, device check), but not complete
  Insider threat → ZT limits damage, but authorized user = access
  Application vulnerabilities → ZT is network-layer
                                 code must still be secure
  Data exfiltration → ZT controls access, but authorized access
                      can still exfiltrate
  DLP needed alongside ZT for data exfiltration prevention
```