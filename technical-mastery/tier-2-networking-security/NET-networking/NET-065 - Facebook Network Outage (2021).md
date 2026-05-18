---
id: NET-065
title: "Facebook Network Outage (2021)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-043, NET-060
used_by: NET-067
related: NET-043, NET-060, NET-064
tags:
  - networking
  - bgp
  - dns
  - incident
  - postmortem
  - facebook
  - case-study
  - single-point-of-failure
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/net/facebook-network-outage-2021/
---

**⚡ TL;DR** - On October 4, 2021, Facebook, Instagram,
and WhatsApp went offline for ~6 hours. Root cause: a
BGP configuration change that accidentally withdrew all
of Facebook's BGP routes. DNS servers became unreachable.
facebook.com stopped resolving. The deeper problem: the
management systems used to fix the issue also required
Facebook's network to be operational. Engineers couldn't
log in remotely - had to physically drive to data centers
with access cards. Critical lesson: your recovery system
must not depend on the system that is broken.

| #065 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DNS Resolution Deep Dive (NET-043), Anycast Routing (NET-060) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067) | |
| **Related:** | DNS Resolution Deep Dive, Anycast Routing, Cloudflare BGP Incident | |

---

### 🔥 Why This Incident Matters

The Facebook outage is the canonical example of a
cascading failure caused by a BGP mistake that also
severed the path to fix the problem. It demonstrates:
(1) BGP is the foundation everything else runs on,
(2) out-of-band management is non-negotiable for critical
infrastructure, (3) DNS depends on BGP reachability,
(4) a single config change can simultaneously take down
three billion users and prevent the engineers from
fixing it. Duration: 6 hours. Revenue loss: ~$6 billion
(stock impact). Reputational impact: incalculable.

---

### 🧠 Timeline of the Outage

```
October 4, 2021

15:40 UTC: Facebook network team runs a BGP configuration
  audit command on backbone routers.
  
  The command is a routine maintenance operation intended
  to check router configuration. Due to a bug in the
  audit tool, the command instead WITHDRAWS all BGP
  route advertisements.
  
  Specifically: Facebook's autonomous system (AS32934)
  stops announcing its IP prefixes to the internet.
  
15:40 UTC: BGP withdrawal propagates globally.
  Within 60 seconds: all internet routers see
  "Facebook's IPs are unreachable"
  Result:
    - facebook.com: no route to IP
    - instagram.com: no route to IP
    - whatsapp.com: no route to IP
    - Facebook's DNS servers: unreachable
    - Any Facebook-hosted service: unreachable

15:40 UTC: DNS impact compounds the failure.
  Facebook's authoritative DNS servers are also on
  Facebook's IP space. They are now unreachable.
  External DNS resolvers: "cannot reach Facebook's
  nameservers" → SERVFAIL responses
  Not just "connection failed" - DNS itself fails

15:40 UTC: Facebook's internal systems also break.
  Internal tools use Facebook's internal network.
  BGP misconfiguration affects internal routing too.
  Tools for: 
    - Monitoring → unreachable
    - Configuration management (FBTW, etc.) → unreachable
    - Remote access (VPN) → unreachable

15:40 - 17:00 UTC: Engineers attempt remote recovery.
  Cannot access network devices remotely.
  Normal VPN requires Facebook's network to be working.
  All attempts at remote remediation fail.

17:00 UTC: Physical access required.
  Teams dispatched with physical access credentials.
  Multiple data center locations.
  Access card system: some doors not opening (access card
  system might also depend on the network)
  Engineers physically at router consoles.

~21:00 UTC: Network traffic starts to return.
  BGP routes re-announced manually.
  Services come back online gradually.
  Total outage: ~6 hours.

~21:30 UTC: All services restored.
```

---

### ⚙️ DNS Cascading Failure Explained

```
Why DNS failed after BGP withdrawal:

Normal DNS for facebook.com:
  1. Recursive resolver: "Who handles facebook.com?"
  2. Root servers: "Ask a.gtld-servers.net"
  3. TLD servers: "Ask a.ns.facebook.com (204.11.56.1)"
  4. facebook.com authoritative: IP returned

After BGP withdrawal:
  Step 4: "Ask a.ns.facebook.com (204.11.56.1)"
  204.11.56.1 is a Facebook-owned IP
  BGP withdrawal: no route to 204.11.56.1
  DNS resolver: timeout trying to reach nameserver
  Returns: SERVFAIL (server failed to respond)

Impact on global DNS:
  Recursive resolvers worldwide cache negative results
  TTL for SERVFAIL: typically 0 seconds (but negative cache)
  Result: every DNS resolver in the world repeatedly
  tries to reach unreachable Facebook nameservers
  DDoS effect on DNS root servers? (not primary cause,
  but DNS recursive resolvers storm the TLD servers)

Additional DNS records also cached and expiring:
  facebook.com had TTL=300s (5 minutes)
  After 5 minutes: cached IPs expire
  Fresh DNS lookup: SERVFAIL
  User: browser shows "server not found"
  Not "connection refused" (service running but unreachable)
  But "SERVFAIL" = DNS entirely broken
```

---

### ⚙️ The Out-of-Band Access Problem

```
Fundamental design flaw exposed:
  Management plane depends on data plane

Normal separation of concerns:
  Data plane: carries user traffic (Facebook posts, messages)
  Management plane: carries control traffic (SSH, monitoring)
  Control plane: BGP routing, configuration management
  
  Security principle: management plane should be INDEPENDENT
  of data plane. Data plane failure should not prevent
  management access.

Facebook's problem:
  Remote access (VPN) required Facebook's network
  When BGP withdrew all routes: VPN endpoints unreachable
  Internal DNS (used by VPN/SSH): unreachable
  Configuration management tools: unreachable
  Even monitoring tools: trying to reach unreachable endpoints

What should have been in place:
  Out-of-band management: separate network/connections
    - Options: IPMI/iDRAC (server management)
    - Options: cellular/LTE backup for critical network devices
    - Options: dedicated management VLAN not in data plane
    - Options: physical console servers (serial console)
  
  Console access: "break glass" procedure
    - Serial console to routers via physical access
    - Should be documented and tested BEFORE emergency
    - Access cards must work without network authentication

Facebook's actual recovery:
  Teams physically drove to data centers
  Some access card systems were also network-dependent
    (had to use manual overrides in some cases)
  Physical console access to routers → re-added routes
  Manual, tedious, time-consuming process

Industry response after the incident:
  Many companies audited their OOB management
  Verified: "can we manage network if network is down?"
  Cloud providers: enhanced console/serial access
  Best practice now: explicit "day 0" testing of OOB procedures
```

---

### ⚙️ The Real-World Impact

```
Direct impact during 6 hours:
  Facebook: ~2 billion daily active users unable to access
  Instagram: ~1 billion daily active users affected
  WhatsApp: ~2 billion users (primary communication in many countries)
  
  Business impact:
    Advertising revenue: ~$100M/day = ~$25M lost
    Stock price: -4.9% (day of), representing ~$40B market cap loss
    Reputational damage: harder to quantify

Secondary impacts:
  Third-party logins: "Login with Facebook" broken everywhere
  Many apps/websites use Facebook OAuth
  Any service that authenticates via Facebook: auth fails
  
  Businesses advertising on Facebook:
    Running ad campaigns: no impressions during outage
    Automated bidding systems: errors during outage
    
  Internal Facebook:
    Internal tools all depend on Facebook's infrastructure
    Employees couldn't communicate using internal tools
    (Yes, some resorted to other messaging apps)
    
For engineers: this is why "Login with X" is a liability
  Single third-party OAuth provider = single point of failure
  Better: support multiple auth providers
  Best: support both social login AND email/password fallback
```

---

### ⚙️ What Good BGP Change Management Looks Like

```bash
# Pre-change checklist (example):

# 1. Document the change intent
echo "Intent: adjust BGP route attributes for PoP-X to improve
traffic steering. Expected: route still announced, only
LOCAL_PREF attribute modified from 100 to 150."

# 2. Validate current state before change
show bgp ipv4 unicast | count  # count total prefixes
show bgp summary                 # all sessions established

# 3. Apply to staging router first
# Run exact same command on staging router (connected
# to BGP test lab, not internet)
# Verify: prefix count unchanged, attributes updated

# 4. Apply to 1 production PoP
# (NOT all PoPs simultaneously)

# 5. Validate immediately after each PoP change:
show bgp ipv4 unicast | count       # same as before?
ping 8.8.8.8                       # outbound reachability
curl -s https://example.com         # can reach internet?
# External probe: is my IP still reachable from internet?

# 6. Wait and monitor (5-10 minutes)
# Watch: did traffic levels recover to baseline?
# Watch: did error rates spike?

# 7. Proceed to next PoP only if all checks pass

# Emergency rollback:
# Pre-prepared rollback config, tested in staging
# Single command: router(config)# no route-map CHANGE_X
# Verify prefix count restored immediately

# Automation:
# Script that monitors prefix count and auto-reverts:
# if [current_prefixes < baseline_prefixes * 0.95]; then
#     apply_rollback_config
#     alert("BGP prefix count dropped, auto-rollback applied")
```

---

### 📐 Scale Considerations

```
Facebook's scale that amplified the impact:

3 billion users:
  Not just Facebook employees at risk
  3 billion people simultaneously lose communication platform
  Many countries: WhatsApp IS the primary communication tool
  Emergency communication: some people cannot call others
    (phone numbers only, no internet messaging)

Infrastructure dependencies:
  Hundreds of third-party apps using Facebook OAuth
  Facebook Pixel on millions of websites
  All stop working simultaneously

Recovery complexity at scale:
  Not 1 router: hundreds of edge routers globally
  BGP changes must be applied to each one
  Manual access: many data centers, many time zones
  Facebook's team: had to coordinate across locations

Lessons for building at scale:
  Single points of failure multiply in impact
  Management plane independence scales in importance
  At < 100k users: "management and data same network" is OK
  At > 1M users: separate management network is essential
  At > 100M users: dedicated teams, runbooks, quarterly drills
```

---

### 🧭 Decision Guide

```
Key lessons from this incident:

1. BGP affects everything
   If you use: BGP, anycast, or any internet routing
   Your BGP is as critical as your database
   Treat BGP config changes with same rigor as DB schema changes

2. Out-of-band access is mandatory
   Test: "can we SSH to our routers if the network is down?"
   If no: implement IPMI/iDRAC/LTE backup for network devices
   Cloud: ensure AWS/GCP console access works without VPC

3. DNS is load-bearing infrastructure
   DNS nameservers must be reachable even during incidents
   Use: multiple providers, geographically distributed
   Facebook: all nameservers on same IP space → all unreachable
   Better: split across different ASNs, providers

4. Avoid cascading dependencies
   "Recovery tool depends on broken system" is an anti-pattern
   Examples: VPN requires active network
             Monitoring depends on monitored system
             Access cards requires network authentication
   Audit: your recovery path for each critical failure mode

5. Change management for critical infrastructure
   Same as production code: test in staging, staged rollout
   Automated checks: prefix count unchanged = proceed
   Automated rollback: prefix count drops = revert immediately

Interview question: "What would you do differently from Facebook?"
   OOB management: serial console access independent of network
   Staged BGP changes: one PoP at a time
   Validation automation: prefix count monitoring
   Access card fallback: physical override, not network-dependent
   DNS resilience: nameservers on diverse infrastructure
```