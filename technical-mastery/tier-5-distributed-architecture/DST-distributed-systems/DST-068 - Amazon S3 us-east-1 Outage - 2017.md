---
id: DST-068
title: "Amazon S3 us-east-1 Outage - 2017"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-007, DST-008, DST-033
used_by: []
related: DST-007, DST-008, DST-033, DST-056
tags:
  - distributed
  - case-study
  - outage
  - aws
  - s3
  - cascading-failure
  - dependency-management
  - resilience
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 68
permalink: /technical-mastery/distributed-systems/s3-outage-2017/
---

⚡ TL;DR - On February 28, 2017, an S3 us-east-1
outage caused by a human error during a routine
maintenance playbook took down not just S3 but
also most of the visible internet for four hours;
a typo in a maintenance command removed a large
fraction of S3 Index subsystem capacity all at once,
triggering cascading failures in S3 billing and
location subsystems that required full restart
(which hadn't been done in years); key lessons:
large-scale system restart time is a critical metric,
minimum safe capacity change bounds should be
enforced by tooling, and AWS status page itself
depended on S3.

---

### 📋 Entry Metadata

| #068 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Cascading Failures, Blast Radius Reduction, Circuit Breakers | |
| **Used by:** | N/A (historical case study) | |
| **Related:** | Cascading Failure, Blast Radius, Circuit Breaker, Dependency Management | |

---

### 🔥 The Problem This Solves

**THE LESSON:**
This case study illustrates:
1. Human error is the most common root cause of
   major outages - not hardware failure.
2. Systems that have never been restarted accumulate
   hidden restart dependencies.
3. Cascading failure from a single AWS service can
   affect unrelated AWS services and third-party
   services at massive scale.
4. Status pages that depend on the service they
   report on are useless during that service's outage.
5. Capacity reduction thresholds must be enforced
   by tooling, not by human judgment.

---

### 📘 Textbook Definition

The **Amazon S3 us-east-1 Outage (February 28, 2017)**:
a major AWS service disruption caused by human error
during a routine maintenance procedure. The outage
lasted approximately 4 hours. S3 in us-east-1 serves
a large fraction of all internet traffic (websites,
APIs, static assets, backups, configuration files
for cloud infrastructure).

**AWS's post-mortem** was publicly available in their
service health dashboard and widely analyzed.

**Impact:** S3, EC2 (impacted console), Lambda,
ECS, EMR, Elastic Beanstalk, AWS Config, Cognito,
CloudWatch, and many third-party services.

---

### ⏱️ Understand It in 30 Seconds

```
TIMELINE (SIMPLIFIED):

09:37 AM PST: Maintenance team ran a playbook to
  remove capacity from S3 billing subsystem to debug
  a slow billing issue.
  
  THE ERROR: command specified an incorrect
  "large" input for the number of servers to remove.
  
  INTENDED: remove a SMALL number of servers.
  ACTUAL: removed a LARGE number of servers from
  the S3 Index subsystem AND the S3 Placement
  subsystem simultaneously.

CASCADING FAILURES:
  S3 Index subsystem handles all S3 metadata requests.
  With large capacity removed: overloaded.
  Placement subsystem handles new object writes.
  With large capacity removed: overloaded.

  S3 requests started failing or timing out.

FULL S3 DEGRADATION:
  S3 read and write errors increased.
  AWS Console could not load (used S3 for static assets).
  
THE RESTART PROBLEM:
  S3 Index and Placement subsystems had not been
  restarted in YEARS. On restart, they need to
  rebuild state from storage (warm up caches).
  
  At S3's scale: warm-up takes hours.
  This is what made the outage so long (4 hours).

KEY INSIGHT:
  If AWS had tested full-restart procedures regularly,
  they would have discovered the long restart time
  and either reduced it or built faster recovery.
  They had not. The "never restart" assumption
  became a hidden fragility.

RESOLUTION:
  09:37 AM: incident begins (error command).
  11:37 AM: S3 subsystems start restoring.
  01:17 PM: S3 fully recovered.
  Total: ~3 hours 40 minutes.
```

---

### 🔩 First Principles Explanation

**ROOT CAUSE ANALYSIS:**

```
DIRECT CAUSE:
  Human typed an incorrect large value for the
  number of servers to remove from S3 billing
  subsystem. The command had no upper bound check
  on the input.

CONTRIBUTING CAUSE 1: TOOLING WITHOUT GUARDS:
  The maintenance tool accepted any number as input.
  There was no check: "you are removing more than
  X% of capacity - are you sure?"
  No rate limiting on capacity removal.
  No "safe ceiling" enforced by the tool.
  
  FIX: Tools that modify production capacity should
  enforce minimum safe capacity bounds:
  - Maximum percentage removable in one operation
  - Mandatory confirmation for large changes
  - Rate-limited capacity reduction (stepwise)
  - Automatic rollback if error rate spikes after change

CONTRIBUTING CAUSE 2: LONG RESTART TIME:
  S3 Index and Placement subsystems had not been
  restarted in years. At S3's massive scale, cold
  starts require rebuilding indexes from persistent
  storage - a process that takes hours.
  
  This restart time was unknown until the outage
  forced a restart.
  
  FIX: Regular game day exercises that restart
  subsystems under controlled conditions. Measure
  actual restart time. Reduce restart time.
  Use incremental startup (start serving limited
  traffic while still warming up).

CONTRIBUTING CAUSE 3: DEEP DEPENDENCY ON S3:
  Many AWS services and most major websites store
  static assets, configuration files, Lambda
  function code, and data on S3.
  
  A single S3 us-east-1 failure propagated to:
  - AWS Console (loaded from S3)
  - Lambda (code packages in S3)
  - CloudFormation (templates in S3)
  - EC2 AMIs (snapshots in S3)
  - Third-party websites (CDNs backed by S3)
  
  FIX: Critical services should not have a single
  regional S3 dependency. Use multi-region replication
  or CDN caching for critical assets.

CONTRIBUTING CAUSE 4: STATUS PAGE DEPENDED ON S3:
  The AWS Service Health Dashboard itself was
  backed by S3. During the outage: the status page
  didn't update for the first hour, showing "green"
  while S3 was failing.
  
  USERS AND ENGINEERS: relied on the status page
  to understand if there was a problem. The status
  page said: no problem. This delayed incident
  response and confused customers.
  
  FIX: Status pages must be hosted independently
  of the services they monitor. Use a separate CDN,
  separate cloud provider, or static pre-rendered
  pages distributed in advance.
```

**CASCADE PATTERN: WHY ONE FAILURE SPREAD SO FAR:**

```
DEPENDENCY GRAPH (simplified):

S3 Index subsystem (failed)
  ↓ all S3 metadata reads fail
  ↓
S3 API (all endpoints fail)
  ├── AWS Console (loads static files from S3)
  ├── Lambda (function code fetched from S3)
  ├── CloudFormation (templates from S3)
  ├── CloudFront (backing S3 origins degrade)
  └── Third-party apps (static files, configs, data)

THIS IS THE CASCADING FAILURE PATTERN:
  One component fails → 
  Everything that depends on it fails →
  Everything that depends on THOSE fails.

THE LESSON:
  S3 had no circuit breaker preventing this cascade.
  AWS expected S3 to be reliable enough that no
  circuit breaking was needed.
  After 2017: AWS invested in:
  - S3 subsystem redundancy
  - Reducing restart time
  - Isolating maintenance operations
  - Enforcing capacity change rate limits
```

**WHAT ENGINEERS SHOULD DESIGN DIFFERENTLY:**

```
1. ASSUME YOUR DEPENDENCIES WILL FAIL:
   Even S3 fails (one of the most reliable services).
   Design for: "what happens when S3 is unavailable?"
   
   Options:
   a. Cache S3 objects in CDN (CloudFront) with long TTL.
      If S3 fails: CDN serves stale but functional cache.
   b. Replicate critical config to multiple regions.
      If us-east-1 S3 fails: read from eu-west-1.
   c. Embed critical config in container image.
      If S3 fails: app starts from embedded config.

2. TEST YOUR RESTART PROCEDURES:
   Run game days: "What if subsystem X needs a full
   restart right now?" Measure actual restart time.
   If restart time > SLA: reduce it.
   
   Tools:
   - Netflix Chaos Monkey: random instance termination.
   - AWS Fault Injection Simulator (FIS): controlled
     faults.
   - Chaos Engineering: fire drill under controlled
     conditions.

3. STATUS PAGE INDEPENDENCE:
   Host your status page differently from your product.
   Use Atlassian Statuspage (separate infra), or serve
   status from a static site pre-deployed to multiple CDNs.

4. CAPACITY CHANGE TOOLING:
   Enforce "no more than X% capacity reduction in one op."
   Require human confirmation for changes > 10%.
   Monitor error rate immediately after capacity change.
   Auto-rollback if error rate exceeds threshold.
```

---

### 🧠 Mental Model / Analogy

> The S3 outage is like a hospital where the
> electricity supply has never been tested with
> backup generators. The hospital knows it has
> generators, but has never actually switched to
> them. One day, the main power fails. The generators
> start but take 4 hours to power up all systems.
> During those 4 hours: surgeries are interrupted,
> life support is threatened, and the hospital's
> emergency notification system (also on main power)
> goes dark. The failure revealed hidden assumptions:
> generators exist but have never been tested;
> the notification system has a single power source.
> Regular fire drills (game days) would have revealed
> both problems while lives were not on the line.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What happened:**
A typo in a maintenance command removed too many
S3 servers at once. S3 overloaded. Most of the
internet went down for 4 hours.

**Level 2 - Why one S3 region broke so much:**
S3 is used by an enormous fraction of internet
services for static files, configuration, data,
and Lambda code. When S3 fails, everything built
on S3 fails too. The cascade was wide because
the dependency was wide.

**Level 3 - Why recovery took 4 hours:**
S3's internal subsystems (Index, Placement) had
not been restarted in years. When they needed to
restart, they had to rebuild internal state at
massive scale. This took hours. Untested restart
procedures are hidden fragility.

**Level 4 - The status page failure:**
The AWS status page itself depended on S3. When
S3 failed, the status page couldn't update.
For the first hour, the status page showed "green"
while thousands of services were failing. Engineers
wasted time checking their own systems, not knowing
the root cause was S3.

**Level 5 - Systematic lessons:**
Three design failures made this worse: (1) tooling
that accepted unconstrained input for capacity
reduction, (2) subsystems that had never been
tested for restart time or cold start behavior,
(3) monitoring infrastructure that shared fate with
the monitored service. Each of these is a class
of design mistake, not an S3-specific mistake.
Every large-scale system should audit for all three.

---

### 💻 Code Example

**Resilience Patterns from the S3 Outage Lessons**

```python
# LESSON 1: Do NOT depend on single-region S3 for
# critical application startup

import boto3
import json
import os
from functools import lru_cache

# BAD: Application loads critical config from S3
# at startup. If S3 is down: app cannot start.
def load_config_bad() -> dict:
    s3 = boto3.client("s3", region_name="us-east-1")
    obj = s3.get_object(
        Bucket="my-app-config",
        Key="production/config.json"
    )
    return json.loads(obj["Body"].read())
    # PROBLEM: If S3 us-east-1 is unavailable:
    # application cannot start.
    # Cascading failure: app is unavailable too.


# GOOD: Multi-layer config loading with fallbacks
def load_config_good() -> dict:
    # Layer 1: Environment variable override
    # (set during deployment, survives S3 outages)
    if config_str := os.environ.get("APP_CONFIG_JSON"):
        return json.loads(config_str)

    # Layer 2: Local disk cache (from last successful load)
    local_cache_path = "/var/cache/app/config.json"
    if os.path.exists(local_cache_path):
        cache_age_s = (
            os.time() - os.path.getmtime(local_cache_path)
        )
        if cache_age_s < 3600:  # Use if < 1 hour old
            with open(local_cache_path) as f:
                return json.load(f)

    # Layer 3: Primary S3 region
    try:
        s3 = boto3.client("s3", region_name="us-east-1")
        obj = s3.get_object(
            Bucket="my-app-config",
            Key="production/config.json"
        )
        config = json.loads(obj["Body"].read())
        # Update local cache on success:
        with open(local_cache_path, "w") as f:
            json.dump(config, f)
        return config
    except Exception:
        pass

    # Layer 4: Failover S3 region
    try:
        s3_backup = boto3.client(
            "s3", region_name="eu-west-1"
        )
        obj = s3_backup.get_object(
            Bucket="my-app-config-eu",
            Key="production/config.json"
        )
        return json.loads(obj["Body"].read())
    except Exception:
        pass

    # Layer 5: Embedded default config
    return _get_embedded_defaults()

def _get_embedded_defaults() -> dict:
    # Minimal config embedded in the binary.
    # Allows app to start in degraded mode.
    return {
        "feature_flags": {},
        "database_pool_size": 10,
        "timeout_ms": 5000,
        "_source": "embedded_defaults",
        "_warning": "running with embedded defaults"
    }
```

```python
# LESSON 2: Status page must not depend on the
# monitored service.

# BAD: Status page served from same S3 bucket as app.
# When S3 fails: status page is also unavailable.

# GOOD: Status page strategy using pre-generated static
# files pushed to multiple independent CDN providers.

import subprocess
import requests
from datetime import datetime, timezone

def update_status_page(status: str, message: str):
    """
    Push status page update to multiple independent
    CDN/hosting providers. If one is down: others work.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    html_content = f"""
<!DOCTYPE html>
<html>
<body>
<h1>Service Status: {status}</h1>
<p>{message}</p>
<p>Last updated: {timestamp}</p>
</body>
</html>
"""
    # Push to GitHub Pages (independent of AWS):
    _push_to_github_pages(html_content)

    # Push to Cloudflare Pages (independent of AWS):
    _push_to_cloudflare(html_content)

    # Push to on-prem static server (independent):
    _push_to_on_prem(html_content)

    # At least one will work even if AWS S3 is down.
```

---

### ⚖️ Comparison Table

| Architecture Decision | Before Outage (Implicit) | After Outage (Explicit) |
|---|---|---|
| **Capacity change tooling** | Accepts any input | Enforces max % per op, confirmation above threshold |
| **Subsystem restart testing** | Never tested | Regular game days; restart time measured |
| **Status page dependency** | Hosted on S3 | Hosted independently (separate infra) |
| **Critical config loading** | From single-region S3 | Multi-region + local cache + embedded defaults |
| **Dependency on S3** | Assumed always available | Circuit-broken; graceful degradation on failure |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The outage was caused by a software bug" | The root cause was human error: an incorrect parameter in a maintenance command. The CONTRIBUTING causes were tooling that didn't prevent the error and a lack of restart time testing. Software is rarely the root cause of major outages. |
| "High availability in multiple regions prevents this" | Multi-region deployments help if you actually FAIL OVER to another region. During this outage, many services in us-east-1 simply failed because they had only a single-region dependency on S3 with no failover logic. |
| "AWS should have prevented this mistake" | AWS did prevent future similar mistakes - by adding capacity change guards to their maintenance tooling. The lesson is not "avoid human operators" but "design tooling that makes dangerous operations hard to do accidentally." |
| "This only affects services that store user data in S3" | S3 is used for much more than user data: Lambda function code, EC2 instance metadata, CloudFormation templates, CloudWatch logs delivery, IAM policies. The blast radius was so large because S3 is an infrastructure primitive, not just a storage service. |

---

### 🚨 Failure Modes & Diagnosis

**Your App Depends on S3 for Startup Config**

**Symptom:** S3 becomes unavailable for any reason
(outage, network partition, permission error after
IAM rotation). All new instances of your app fail
to start. Running instances continue (if they cached
config at startup). Rolling deploys fail. Auto-scaling
events create non-functional instances.

**Diagnosis:**
```bash
# Detect S3 dependency at startup:
strace -e trace=network -p <pid> 2>&1 | grep s3

# Or: check startup logs for S3 calls:
grep -E "s3|amazonaws" /var/log/app/startup.log

# Test resilience: mock S3 failure during startup:
# (use tc netem or Toxiproxy to block S3 traffic)
sudo tc qdisc add dev eth0 root netem loss 100%
# Then restart the application and observe behavior.
# Restore after test:
sudo tc qdisc del dev eth0 root

# Check if app handles S3 timeout gracefully:
# Set a very low connect timeout and observe:
AWS_S3_CONNECT_TIMEOUT=1 ./start-app.sh
# If app hangs: no timeout handling.
# If app starts with warnings: good.
```

**Fix:** Implement the multi-layer config loading
pattern (env var > local cache > primary S3 > failover
S3 > embedded defaults). Ensure the app can start
with embedded defaults in degraded mode.

---

### 🔗 Related Keywords

**Prerequisites:** `Cascading Failures` (DST-007),
`Blast Radius Reduction` (DST-008),
`Circuit Breakers` (DST-033)

**Related:** `Distributed Systems Performance Tuning`
(DST-056)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DATE        │ February 28, 2017; 4-hour outage          │
│ ROOT CAUSE  │ Human typo in maintenance command;       │
│             │ removed too many S3 Index servers        │
├─────────────┼───────────────────────────────────────────┤
│ CASCADE     │ S3 down → Console, Lambda, CloudFormation │
│             │ → most internet services                 │
├─────────────┼───────────────────────────────────────────┤
│ LONG OUTAGE │ Subsystems never restarted in years;     │
│ REASON      │ cold start took hours at S3 scale        │
├─────────────┼───────────────────────────────────────────┤
│ META LESSON │ Status page was on S3: showed green     │
│             │ for first hour of outage                 │
├─────────────┼───────────────────────────────────────────┤
│ 3 FIXES     │ 1. Tooling: enforce capacity change %   │
│             │ 2. Game days: test restart time         │
│             │ 3. Status page: independent of service  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The S3 outage illustrates that the most dangerous
failures are not the ones you test for but the ones
you have implicitly assumed will never happen. Every
major system makes assumptions: S3 won't fail, the
database won't need a restart, the status page will
always be up. These assumptions accumulate into hidden
fragility. Chaos engineering exists precisely to
surface hidden assumptions by inducing failures in
controlled conditions. The question is not "will this
service fail?" (it will) but "have we validated that
our system behaves correctly when it does?" Regular
game days, forced restarts in staging, and dependency
audits convert hidden assumptions into known,
measured trade-offs. The engineers who maintain
S3 are excellent. They made a human mistake with
a maintenance tool. The system's fragility was
that no tooling enforced safe operation bounds,
and no game days had revealed the long restart time.
These are organizational and process failures, not
individual failures.

---

### 💡 The Surprising Truth

One of the most widely cited facts about this outage:
the AWS Service Health Dashboard itself showed a
green "Operating normally" status for the first
hour of the S3 outage. This is because the dashboard
was backed by S3. When S3 failed, the dashboard's
own update mechanism (also using S3) also failed.
Engineers across the industry were checking the AWS
status page to determine whether the widespread
failures they were seeing were an AWS problem or
a problem with their own code. The status page said
"everything is fine." This delayed incident response
by an hour for many teams. After this incident,
AWS moved the Service Health Dashboard to an
architecture that does not depend on S3, using
pre-generated static HTML distributed to multiple
CDN providers not backed by S3. The lesson became
a principle now repeated in every SRE training:
"Your monitoring must not depend on the system it
monitors." This principle extends to alerting,
runbooks, and incident management tools.

---

### ✅ Mastery Checklist

1. [IDENTIFY] List three services in your current
   architecture that depend on S3 or equivalent
   object storage. For each: what happens if that
   storage is unavailable for 10 minutes?
2. [DESIGN] A status page for a high-availability
   service. Ensure it works even if the primary
   cloud provider (AWS, GCP, Azure) is down. What
   hosting strategy achieves this?
3. [IMPLEMENT] A config loading function with fallback
   tiers: (1) env var, (2) local cache, (3) primary
   S3, (4) backup region S3, (5) embedded defaults.
   Test that each fallback works independently.
4. [AUDIT] What "untested restart" assumptions exist
   in your system? When was the last time any
   critical subsystem was fully restarted from cold?
   Do you know the restart time?
5. [PREVENT] Design capacity change tooling for
   a distributed system. What safeguards should
   the tooling enforce to prevent a single command
   from removing a dangerous fraction of capacity?
