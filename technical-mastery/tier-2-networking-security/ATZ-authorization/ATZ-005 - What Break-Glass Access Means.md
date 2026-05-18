---
id: ATZ-005
title: "What Break-Glass Access Means"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-004
used_by: ATZ-023, ATZ-031, ATZ-048
related: ATZ-004, ATZ-011, ATZ-022
tags:
  - security
  - authorization
  - break-glass
  - emergency-access
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 5
permalink: /technical-mastery/authorization/what-break-glass-access-means/
---

⚡ **TL;DR** - Break-glass access is a controlled mechanism for
granting temporary elevated permissions during emergencies when
normal authorization channels are too slow or unavailable. The
name comes from physical "break glass in emergency" fire alarms:
the mechanism is always available, but using it triggers an alarm
and creates an audit trail. Proper break-glass combines instant
access with mandatory logging and post-incident review.

---

### 📊 Entry Metadata

| #005 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-004 Principle of Least Privilege | |
| **Used by:** | ATZ-023, ATZ-031, ATZ-048 | |
| **Related:** | ATZ-004 PoLP, ATZ-011 Superuser, ATZ-022 Delegated Authorization | |

---

### 🔥 The Problem This Solves

**THE TENSION:**

Least privilege says give the minimum access necessary.
But emergencies happen: production is down at 3 AM, the
on-call engineer needs database write access now, the
normal approval process takes 4 hours, and every minute
of downtime costs $50,000.

Break-glass resolves this tension: it grants elevated access
instantly but makes the access auditable and time-bounded.
The "glass break" itself is the alarm - you know someone
used emergency access, why, and what they did with it.

**WORLD WITHOUT IT:**

Without break-glass:
- Engineers have standing elevated access "just in case"
  (violates PoLP, large blast radius)
- Or: emergencies are slow because approvals are manual
  (reliability impact)
- Or: engineers create undocumented workarounds to get
  access during incidents (no audit trail, security gap)

---

### 📘 Textbook Definition

Break-glass access (also called emergency access or privileged
emergency access) is a security pattern that allows authorized
personnel to immediately acquire elevated privileges for a
defined emergency scenario, with automatic logging of all
actions taken, mandatory justification, auto-expiring access,
and mandatory post-incident review. The pattern balances
operational resilience (emergency access is available) with
security accountability (the "break" is always detected
and reviewed).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Emergency access that is always available, always logged,
and always reviewed - so you can fix production fast without
creating a permanent security hole.

**One analogy:**
> A bank's dual-control safe. Any one manager can open it
> in an emergency, but opening it triggers an alarm,
> generates a log entry, and requires a written incident
> report filed before the end of the day. Fast emergency
> access with accountability.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────┐
│          Break-Glass Access Pattern                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  NORMAL OPERATIONS:                                 │
│  Engineer has: read-only production access          │
│                                                     │
│  EMERGENCY:                                         │
│  1. Engineer requests break-glass elevation         │
│     (reason: "production DB latency, P1 incident")  │
│  2. System immediately grants elevated access       │
│     (no human approval needed for speed)            │
│  3. Access auto-expires in T hours (1-4h typical)   │
│  4. ALL actions during access are logged            │
│     (SQL queries, file access, config changes)      │
│  5. Alert sent to security team immediately         │
│  6. Post-incident: engineer files review explaining │
│     what was done and why                           │
│  7. Security team reviews logs vs explanation       │
│                                                     │
│  KEY PROPERTIES:                                    │
│  - Instant (no approval gate)                       │
│  - Time-bounded (auto-expires)                      │
│  - Fully audited (every action logged)              │
│  - Alarmed (security team knows immediately)        │
│  - Reviewed (post-incident mandatory)               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - AWS break-glass with STS assume role**

```python
# Break-glass: assume emergency IAM role with full access
# Normal role: readonly access only
import boto3
import json
from datetime import datetime

def request_break_glass(reason: str, incident_id: str):
    """
    Request break-glass elevated access.
    Logs the request before granting access.
    """
    sts = boto3.client('sts')
    caller = sts.get_caller_identity()

    # Log the break-glass request before assuming role
    cloudtrail = boto3.client('cloudtrail')
    # (CloudTrail records AssumeRole automatically)

    # Tag the session with incident context for audit
    response = sts.assume_role(
        RoleArn="arn:aws:iam::123456789:role/BreakGlassRole",
        RoleSessionName=f"breakglass-{incident_id}",
        DurationSeconds=3600,  # 1-hour auto-expiry
        Tags=[
            {'Key': 'IncidentId', 'Value': incident_id},
            {'Key': 'Reason', 'Value': reason[:100]},
            {'Key': 'RequestedBy', 'Value': caller['UserId']},
            {'Key': 'RequestedAt',
             'Value': datetime.utcnow().isoformat()},
        ]
    )

    # Send immediate alert
    sns = boto3.client('sns')
    sns.publish(
        TopicArn="arn:aws:sns:us-east-1:123:security-alerts",
        Subject=f"BREAK-GLASS: {incident_id} by {caller['UserId']}",
        Message=json.dumps({
            'incident': incident_id,
            'reason': reason,
            'user': caller['UserId'],
            'expires': response['Credentials']['Expiration'].isoformat()
        })
    )
    return response['Credentials']
```

**Example - FAILURE: break-glass without auto-expiry**

```
Scenario:
  Break-glass role has no session duration limit.
  Engineer uses it during P1 incident.
  Incident resolves. Engineer forgets to revoke.
  Role credentials remain valid indefinitely.

  6 months later: engineer leaves company.
  Offboarding revokes their normal access.
  But: break-glass session credentials are still valid
  (credentials are temporary but long-lived if no expiry).

Fix: always set DurationSeconds on AssumeRole calls.
  IAM role should have MaxSessionDuration = 4 hours.
  Break-glass access cannot exceed 4 hours regardless
  of how the STS call is made.

  Also: audit CloudTrail for AssumeRole on BreakGlassRole
  and alert on any session still active after 4 hours.
```

---

### ⚠️ Common Failure Modes

**Break-glass used routinely (normalization of deviance):**

```
Symptom:
  Break-glass access is used 3-4 times per week.
  "It's faster than the normal approval process."

Root cause:
  Normal authorization process is too slow for operations.
  Engineers optimize for speed by normalizing emergency access.

Fix:
  1. Treat frequent break-glass as a signal that normal
     authorization channels are too slow - fix them
  2. Alert on frequency: >2 uses per month = process review
  3. Reduce normal-path friction for common legitimate needs
     (pre-approve common operational roles, reduce wait time)
```

---

*Authorization category: ATZ | Entry: ATZ-005 | v5.0*