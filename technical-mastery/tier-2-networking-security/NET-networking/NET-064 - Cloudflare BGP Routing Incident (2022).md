---
id: NET-064
title: "Cloudflare BGP Routing Incident (2022)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-060, NET-061
used_by: NET-067
related: NET-060, NET-061, NET-065
tags:
  - networking
  - bgp
  - incident
  - postmortem
  - routing
  - cloudflare
  - case-study
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 64
permalink: /technical-mastery/net/cloudflare-bgp-routing-incident-2022/
---

**⚡ TL;DR** - On June 21, 2022, Cloudflare experienced
a significant outage affecting 19 data centers when a
network configuration change caused BGP to withdraw
Cloudflare's IP prefixes from the global routing table.
Traffic that should have reached those 19 PoPs had
nowhere to go - connections failed or timed out globally.
Lesson: BGP changes are global and instant. A single
misconfigured routing policy can take a CDN segment
offline. Rollback is slower than the damage. Defense:
staged BGP changes, extensive validation, and circuit
breakers on routing policy deployment.

| #064 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Anycast Routing (NET-060), DDoS Attack Types (NET-061) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067) | |
| **Related:** | Anycast Routing, DDoS Attack Types, Facebook Network Outage | |

---

### 🔥 Why This Incident Matters

BGP is the internet's routing system. Everyone assumes
it is stable - it changes rarely. But when it does change
incorrectly, the impact is global and immediate. No
gradual rollout. No canary deployment. When BGP says
"this IP is unreachable," every router on the internet
updates within minutes. Cloudflare serves ~20% of web
traffic. A BGP mistake at this scale is visible worldwide.
This incident teaches: treat BGP config like production
code. Test, stage, review, have rollback planned.

---

### 🧠 What Happened (Timeline)

```
June 21, 2022 - Cloudflare BGP Incident

06:27 UTC: Network team begins rolling out infrastructure
  changes to 19 data centers as part of planned maintenance.
  The changes include new BGP configuration.

06:27 UTC: Configuration deployed. BGP sessions come up.
  But: the new BGP policy incorrectly WITHDRAWS IP prefixes
  that should remain advertised.
  
  What "withdrawing a prefix" means:
  - Cloudflare normally announces: "I can reach 1.1.1.1/32"
  - Withdrawn: "I am withdrawing my announcement for 1.1.1.1/32"
  - Internet routers: "Cloudflare can no longer reach 1.1.1.1"
  - Result: traffic to those IPs has no route = black hole

06:27 UTC: BGP withdrawal propagates globally.
  BGP convergence: ~30 seconds for most of internet
  After 30 seconds: 19 Cloudflare PoPs are unreachable
  Traffic: 100% of requests to affected PoPs fail

06:27-06:37 UTC: Cloudflare systems detect the failure.
  Automated alerting fires. Engineers paged.

06:37 UTC: Root cause identified. Rollback initiated.
  But: rolling back BGP config takes time per PoP.
  BGP withdrawal was instant; restoration is per-hop.

06:58 UTC: All 19 data centers restored to service.
  Total outage: ~31 minutes for most affected PoPs.

Impact:
  ~19 data centers offline
  Significant fraction of Cloudflare's global traffic
  Millions of end users affected
  Cloudflare's own DNS (1.1.1.1), CDN, Zero Trust all affected
```

---

### ⚙️ Root Cause: BGP Policy Error

```
Cloudflare uses BGP anycast:
  Multiple PoPs announce the same IP prefixes
  Internet routes to nearest PoP
  
New configuration intent:
  Improve BGP route attributes for better traffic steering
  No intent to withdraw prefixes
  
Actual effect:
  New routing policy contained a logic error
  The policy matched more routes than intended
  Matching routes were incorrectly withdrawn
  Instead of modifying route attributes, routes were removed

Technical BGP details:
  Route maps: filter and modify BGP routes
  Community tags: BGP communities used for traffic engineering
  If-then logic: "IF route matches community X, THEN..."
  Bug: community matching was too broad
  Included prefixes that should only be modified, not withdrawn

Analogy:
  You want to change the color tag on certain packages
  But your instruction reads "re-tag OR discard if tagged blue"
  All blue packages (your own announcements) are discarded
  They never leave your facility → nobody can route to you
```

---

### ⚙️ The Cascading Effect

```
Direct impact:
  19 PoPs lose their BGP announcements
  Traffic to those PoPs → no route → TCP connection fails
  HTTP/TCP: immediate failure (SYN with no response)

Secondary cascading:
  Cloudflare provides: CDN, DDoS protection, DNS (1.1.1.1),
  Zero Trust (ZTNA), Workers, Stream, Pages
  
  All affected customers simultaneously:
  → CDN: websites served by Cloudflare unreachable
  → DNS: 1.1.1.1 resolver unreachable from affected regions
  → DDoS protection: bypassed (traffic can't reach Cloudflare)
  
  For customers behind Cloudflare:
  Their origin was still running but unreachable:
  Cloudflare was the only path to their service

Why traffic didn't failover:
  Anycast: other PoPs were still up and serving
  But: traffic was being routed to the 19 affected PoPs
  BGP had already routed users to nearby (now-withdrawn) PoPs
  
  BGP reconvergence after withdrawal:
  "Nearest PoP unreachable" → route to next-nearest PoP
  This reconvergence: happens within 30-60 seconds
  But: depends on how many PoPs are still announcing the prefix
  Complete reconvergence may take several minutes for all paths
```

---

### ⚙️ What Cloudflare Could Have Done Differently

```
Improvement 1: Staged BGP changes
  Current: deployed to all 19 PoPs simultaneously
  Better: deploy to 1 PoP, validate, then 5, then 14
  Time cost: +30 minutes for validation
  Risk reduction: single PoP impacted vs 19

Improvement 2: BGP dry-run or shadow announcement
  Test policy with: no-export community
  Announce routes with "no-export" community
  Routes accepted by upstream but NOT propagated globally
  Validate: routes correct, attributes correct
  Then: remove no-export, routes propagate globally

Improvement 3: Automated validation before deployment
  Check: "are all my prefixes still in BGP table after change?"
  Tool: gobgp, bird, FRR with configured assertions
  CI/CD: fail deployment if expected prefixes disappear

Improvement 4: Circuit breaker on routing policy deployment
  Validate: "after applying BGP policy, did prefix count decrease?"
  If YES: automatic rollback
  If NO: proceed
  Hard limit: "never withdraw more than 10% of prefixes in one change"

Improvement 5: Out-of-band management
  BGP changes should be controllable from a management network
  Not dependent on the same network being changed
  Cloudflare had: some PoPs inaccessible to engineers
  (the very network they were trying to fix was down)

What Cloudflare actually improved after the incident:
  More validation steps before BGP changes
  Staged rollouts for all BGP policy changes
  Automated testing of BGP policy changes in staging
  Enhanced monitoring of prefix counts and BGP session health
```

---

### ⚙️ BGP Incident Response Playbook

```bash
# Step 1: Detect - what's down?
# Check BGP prefix announcements:
# From external looking glass (route-views.oregon-ix.net):
telnet route-views.oregon-ix.net
# > show ip bgp 1.1.1.1
# If output empty or no path: prefix withdrawn globally

# Step 2: Diagnose - recent BGP changes?
# In your BGP router logs:
grep "withdrawn\|prefix removed" /var/log/bird.log | tail -50
# Or: FRRouting (FRR):
sudo vtysh -c "show bgp summary"
sudo vtysh -c "show bgp ipv4 unicast 1.1.1.0/24"

# Step 3: Rollback BGP change
# FRR/BIRD: revert routing policy config
# Apply previous working config
sudo systemctl reload bird
# Or per-interface:
sudo ip route add 1.1.1.0/24 via gateway_ip
# BGP re-announcement: restart BGP session
sudo vtysh -c "clear bgp * soft"

# Step 4: Verify recovery
# Check: prefix is now announced globally
# External looking glass: is route visible?
# BGP RIB shows the announcement
# Ping/HTTP test from external: now succeeds

# Step 5: Post-incident
# Capture: which prefixes were affected
# Timeline: when withdrew, when restored
# Root cause: which config line caused the withdrawal
# Action items: staging, validation, circuit breaker
```

---

### 📐 Scale Considerations

```
BGP change blast radius:

Single prefix (/32): minimal impact
  One IP unreachable
  
/24 or larger prefix: significant impact
  256+ IPs unreachable
  All services on those IPs fail
  
Entire AS prefix removal (Cloudflare case):
  All PoPs that relied on those announcements
  Anycast IP reachability for global CDN
  All customers behind those PoPs

BGP propagation speed:
  Single hop withdrawal: seconds
  Full global propagation: 30-300 seconds
  Full convergence with alternative paths: 5-10 minutes

Rollback speed:
  Re-announcing prefix: 30-60 seconds for first path
  Full global re-convergence: 5-15 minutes
  Contrast: outage happened instantly, recovery takes minutes

Why BGP is hard to test:
  Production BGP: global routing table
  Test BGP: simulated, can't capture all real-world paths
  BGP policy bugs may only surface with specific route patterns
  Comprehensive staging: requires real BGP feeds and policy testing

Notable BGP incidents:
  2010: China Telecom hijacked 15% of internet routes for 18 min
  2019: Cloudflare outage (different cause, similar impact)
  2021: Facebook DNS + BGP outage (6 hours, BGP withdrawn intentionally)
  2022: This Cloudflare incident (31 minutes)
  All: BGP config error or route leak
```

---

### 🧭 Decision Guide

```
Lessons for engineers who manage routing:

Treat BGP config as production code:
  Version control: all BGP config in Git
  Code review: peer review all BGP policy changes
  CI/CD: automated testing before apply
  Staging: test with real BGP feeds if possible

Staged deployment for BGP:
  Rule: never apply BGP changes to all PoPs simultaneously
  Process: 1 PoP → validate 5 min → 10% PoPs → validate → all
  Rollback plan: always have it before starting

Validation after BGP change:
  Check: prefix count unchanged (or expected changes only)
  Check: BGP session states all established
  Check: external probe shows IPs still reachable
  Check: traffic levels returning to baseline
  Automate all of the above

For Kubernetes/cloud engineers (without direct BGP):
  Same principle: infrastructure changes should be staged
  Kubernetes: node selector, affinity, PodDisruptionBudget
  Cloud LB: gradual weight shifts, not 0/100 flips
  DNS: short TTL (60s) before changes, change, restore TTL

Interview question: "How would you design a global network?"
  Always mention: BGP staged changes, validation, circuit breakers
  Always mention: runbook for BGP incidents
  Always mention: out-of-band management for network changes
  Strong answer: mention specific Cloudflare/Facebook incidents
    as motivation for these practices
```