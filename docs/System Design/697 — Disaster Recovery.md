---
layout: default
title: "Disaster Recovery"
parent: "System Design"
nav_order: 697
permalink: /system-design/disaster-recovery/
number: "0697"
category: System Design
difficulty: ★★★
depends_on: Redundancy, RTO/RPO, Backup Strategy
used_by: Business Continuity Planning, Infrastructure Design
related: RTO/RPO, Geo-Replication, Failover
tags:
  - disaster-recovery
  - business-continuity
  - advanced
  - reliability
  - infrastructure
---

# 697 — Disaster Recovery

⚡ TL;DR — Planning and mechanisms to recover from catastrophic failures (data center outage, ransomware, data corruption). Includes RTO/RPO targets, replication strategy, backup procedures, and regular testing.

| #697            | Category: System Design                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Redundancy, RTO/RPO, Backup Strategy                |                 |
| **Used by:**    | Business Continuity Planning, Infrastructure Design |                 |
| **Related:**    | RTO/RPO, Geo-Replication, Failover                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Data center burns down. "What's the recovery plan?" "Uh... restore from backups?" How long? Days. How much data lost? Unknown. Business destroyed.

**THE BREAKING POINT:**
Disasters eventually happen. Without a plan, business impact is catastrophic.

**THE INVENTION MOMENT:**
"Plan for disaster before it happens. Define recovery targets (RTO/RPO). Build infrastructure to meet them. Test regularly."

---

### 📘 Textbook Definition

**Disaster Recovery:** Comprehensive strategy and processes to restore systems and data after catastrophic failure. Includes: backup procedures, redundant infrastructure (geographic separation), documented runbooks, regular testing, RTO/RPO commitments, and post-disaster validation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Plan for worst-case (data center down). Have backups. Test recovery regularly.

**One analogy:**

> House insurance: (1) backup plan (move to hotel), (2) insurance pays (redundancy), (3) replace lost items (restore from backups), (4) test by running drills (recovery testing).

**One insight:**
Untested disaster recovery plan doesn't exist. Only tested plans work.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Disasters are inevitable (not "if" but "when")
2. Recovery takes time and resources
3. Business must accept some downtime/data loss (RTO/RPO)
4. Recovery procedures must be tested regularly (or they don't work)

**COMPONENTS OF DR:**

1. **RTO/RPO**: Define acceptable downtime and data loss
2. **Replication/Backup**: Mechanisms to preserve data
3. **Redundant Infrastructure**: Systems geographically separated
4. **Runbooks**: Step-by-step recovery procedures
5. **Automation**: Minimize manual recovery steps
6. **Testing**: Regular drills to verify recovery works

**THE TRADE-OFFS:**
**Gain:** Business continuity. Regulatory compliance. Customer confidence. Reduced disaster impact.

**Cost:** Infrastructure (geographic redundancy). Operations (monitoring, backups, testing). Overhead (runbooks, training).

---

### 🧪 Thought Experiment

**SETUP:**
Payment company. Primary DC in us-east. Backup DC in us-west.

**Scenario: Data Center Fire (us-east destroyed)**

**Company A (No DR Plan):**

- Disaster 14:00 - DC fire, all systems down
- 14:05 - Team realizes scale of damage
- 14:30 - Find old backup (1 week old, offline)
- 15:00 - Restore from backup
- 16:00 - Get first system back online (read-only)
- 18:00 - Full recovery (4 hours downtime, 1 week of data lost)
- Result: SLA breached, customers switched to competitors

**Company B (With DR Plan: RTO=1h, RPO=1min):**

- Disaster 14:00 - DC fire
- 14:01 - Automated failover triggered (geo-replication detected primary down)
- 14:05 - All traffic routed to us-west DC
- 14:10 - Verification complete (RTO = 10 min, within SLA)
- Result: Minimal impact, customers barely noticed

**THE INSIGHT:**
DR prep costs money upfront but saves business when disaster hits.

---

### 🧠 Mental Model / Analogy

> Airline schedules: (1) Normal flight (primary DC). (2) If weather bad, divert to alternate airport (failover to backup DC). (3) Pilots trained for emergencies (runbooks). (4) Monthly simulations (testing). (5) Emergency supplies on-board (backups).

- "Primary flight path" → primary DC
- "Alternate airport" → backup DC
- "Weather emergency" → disaster
- "Trained pilots" → documented procedures
- "Monthly simulations" → DR drills
- "Emergency supplies" → backups

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Plan for worst-case (entire DC fails). Have backup DC ready. Ability to recover systems in hours (not days). Test it regularly so it actually works.

**Level 2 — How to use it (junior developer):**
Backup database daily to remote location. Replicate to secondary DC continuously. Test recovery once per quarter: "Pretend primary DC is dead, can we recover in our RTO target?"

**Level 3 — How it works (mid-level engineer):**
Define RTO/RPO targets from business requirements. Implement replication/backup to meet targets. Create automated failover (reduce manual steps). Document recovery runbooks (exact steps to restore each system). Implement monitoring to detect disasters quickly. Schedule quarterly DR drills: full recovery simulation, measure actual RTO/RPO, identify gaps.

**Level 4 — Why it was designed this way (senior/staff):**
Disaster recovery evolved from business continuity requirements (banks, hospitals). Regulations (GDPR, SOX, HIPAA) mandate DR plans and testing. Modern DR combines: (1) RTO/RPO SLAs (business requirements), (2) Multi-region replication (geographic redundancy), (3) Infrastructure-as-Code (spin up DC quickly), (4) Automated failover (reduce recovery time), (5) Regular testing (catch hidden bugs). Key insight: actual RTO often worse than theoretical (untested), so testing critical.

---

### ⚙️ How It Works (Mechanism)

Disaster recovery execution:

```
PHASE 1: PREPARATION (Continuous)
─────────────────────────────────
- Define RTO/RPO targets (business requirement)
- Implement replication/backup strategy
- Set up secondary DC or cloud region
- Document recovery runbooks
- Configure monitoring and alerting

PHASE 2: DETECTION (When Disaster Strikes)
──────────────────────────────────────────
Disaster occurs: Data center power failure
  ↓
Monitoring system detects:
  - Primary DC unreachable
  - Health check failures
  - Network timeouts
  ↓
Alert sent to on-call team
  (Ideally within 1-5 minutes)

PHASE 3: INITIAL RESPONSE (First 15-30 Minutes)
────────────────────────────────────────────────
On-call engineer:
  1. Confirms disaster (not just network blip)
  2. Initiates DR procedures
  3. Brings up secondary DC (may be automated)
  4. Reroutes traffic to secondary

PHASE 4: RECOVERY (Next 30 min - 2 hours)
──────────────────────────────────────────
Secondary DC activation:
  - Spin up application servers (if cold boot)
  - Promote database replicas to primary (if active-passive)
  - Update DNS records
  - Verify data integrity
  - Run smoke tests

At RTO mark (e.g., 1 hour):
  - Service should be fully operational on secondary DC
  - Users may experience slight latency (secondary region)
  - Data loss up to RPO mark (e.g., 5 minutes)

PHASE 5: STABILIZATION (1-4 Hours Post-Recovery)
─────────────────────────────────────────────────
- Monitor secondary DC closely (run at 1.5x normal capacity)
- Implement gradual traffic increase (avoid cascades)
- Communicate with customers (transparency)
- Begin investigation: what went wrong?
- Prepare for secondary DC failback (when primary recovered)

PHASE 6: FAILBACK (When Primary Recovered, Weeks Later)
────────────────────────────────────────────────────────
Primary DC repairs:
  - Hardware replaced
  - Networking verified
  - Systems brought up

Data sync:
  - If secondary had transactions during disaster, sync back to primary
  - Ensure consistency

Failback to primary:
  - Gradual traffic migration back
  - Verify primary stability
  - Resume normal ops
```

**Timeline Example (RTO=1h, RPO=5min):**

```
14:00:00 - Primary DC loses power (disaster start)
14:05:00 - Monitoring detects failure
14:06:00 - On-call engineer paged
14:10:00 - Failover initiated
14:12:00 - Secondary DC taking traffic
14:30:00 - Verification complete
14:31:00 - Actual RTO = 31 minutes (within 1-hour target)
14:35:00 - Investigate: Last replicated transaction was 14:30, so 5 min data loss
          - But all transactions from 14:00-14:30 lost (in flight when power failed)
          - Total data loss: 30 minutes (EXCEEDS 5-min RPO target!)
          - Post-mortem: replication lag was 30 min, not 5 min as assumed
```

---

### 💻 Code Example

**Example 1 — Backup and Restore Script:**

```bash
#!/bin/bash
# Daily backup to remote location

BACKUP_DIR="/backups"
REMOTE_BUCKET="s3://company-backups-dr"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting database backup..."

# 1. Dump database
pg_dump -U postgres -d production > "$BACKUP_DIR/db_$TIMESTAMP.sql"

# 2. Compress
gzip "$BACKUP_DIR/db_$TIMESTAMP.sql"

# 3. Upload to S3 (remote, geographically separated)
aws s3 cp "$BACKUP_DIR/db_$TIMESTAMP.sql.gz" "$REMOTE_BUCKET/" \
  --region us-west-2

# 4. Verify upload
if aws s3 ls "$REMOTE_BUCKET/db_$TIMESTAMP.sql.gz"; then
    echo "✓ Backup successful: $REMOTE_BUCKET/db_$TIMESTAMP.sql.gz"
    # Cleanup local copy after remote confirmed
    rm "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
else
    echo "✗ Backup upload failed!"
    exit 1
fi

# 5. Test restore (monthly)
if [ $(date +%d) -eq 01 ]; then  # First of month
    echo "Running monthly restore test..."
    # Download, decompress, restore to test environment
    aws s3 cp "$REMOTE_BUCKET/db_$TIMESTAMP.sql.gz" /tmp/
    gunzip /tmp/db_$TIMESTAMP.sql.gz
    psql -U postgres -d test_db < /tmp/db_$TIMESTAMP.sql
    echo "✓ Restore test successful"
fi
```

**Example 2 — Automated Failover to Secondary DC:**

```python
import boto3
import time

class DisasterRecovery:
    def __init__(self):
        self.route53 = boto3.client('route53')
        self.primary_dc_ip = "10.0.1.5"
        self.secondary_dc_ip = "10.0.2.5"
        self.domain = "db.company.internal"
        self.zone_id = "Z1234567890ABC"

    def detect_primary_failure(self):
        """Monitor primary DC health"""
        try:
            response = boto3.client('ec2').describe_instances(
                Filters=[{'Name': 'tag:Name', 'Values': ['primary-db']}]
            )
            if response['Reservations'][0]['Instances'][0]['State']['Name'] != 'running':
                return True  # Primary failed
        except:
            return True  # Assume down if can't check
        return False

    def failover_to_secondary(self):
        """Promote secondary and update DNS"""
        print("[DR] Initiating failover to secondary DC...")

        # 1. Update DNS to point to secondary
        self.route53.change_resource_record_sets(
            HostedZoneId=self.zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': self.domain,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': self.secondary_dc_ip}]
                    }
                }]
            }
        )

        # 2. Promote secondary database (if applicable)
        # ssh secondary_host "pg_ctl promote ..."

        # 3. Notify team
        print("[DR] Failover complete. Applications connecting to secondary DC")
        print("[DR] Alerting team...")
        # send_alert("Disaster Recovery: Failed over to secondary DC")

        return True

    def monitor_and_failover(self):
        """Continuous monitoring, trigger failover if needed"""
        while True:
            if self.detect_primary_failure():
                print("[DR] Primary DC failure detected!")
                self.failover_to_secondary()
                break  # Failover complete
            time.sleep(10)

# Usage
dr = DisasterRecovery()
dr.monitor_and_failover()
```

**Example 3 — DR Testing / Simulation:**

```bash
#!/bin/bash
# Quarterly DR drill script

echo "=== QUARTERLY DISASTER RECOVERY DRILL ==="
echo "Start Time: $(date)"

# 1. Snapshot current state (for comparison)
curl -s http://primary-dc/api/status | jq . > /tmp/primary_status_before.json

# 2. Simulate primary DC failure (network isolation)
echo "Isolating primary DC from network..."
sudo iptables -A OUTPUT -d 10.0.1.0/24 -j DROP
sudo iptables -A INPUT -s 10.0.1.0/24 -j DROP

# 3. Measure time to detection
start_time=$(date +%s)
while curl -s http://primary-dc/health >/dev/null 2>&1; do
    sleep 1
done
detection_time=$(($(date +%s) - start_time))
echo "Detection time: ${detection_time}s"

# 4. Failover
echo "Triggering failover to secondary DC..."
start_failover=$(date +%s)

# Wait for DNS/LB to update (may take time)
while ! curl -s http://secondary-dc/api/status >/dev/null 2>&1; do
    sleep 1
done

failover_time=$(($(date +%s) - start_failover))
echo "Failover time: ${failover_time}s"

# 5. Verify data integrity
echo "Verifying data integrity..."
curl -s http://secondary-dc/api/status | jq . > /tmp/secondary_status_after.json
diff /tmp/primary_status_before.json /tmp/secondary_status_after.json || {
    echo "⚠️  WARNING: Data mismatch detected!"
}

# 6. Restore network (end drill)
echo "Restoring primary DC network access..."
sudo iptables -D OUTPUT -d 10.0.1.0/24 -j DROP
sudo iptables -D INPUT -s 10.0.1.0/24 -j DROP

# 7. Failback
echo "Failback to primary DC..."
# Assuming primary recovered automatically
# May require manual intervention

total_time=$((detection_time + failover_time))
echo ""
echo "=== DRILL COMPLETE ==="
echo "Total Recovery Time: ${total_time}s (Target RTO: 3600s)"
if [ $total_time -le 3600 ]; then
    echo "✓ RTO TARGET MET"
else
    echo "✗ RTO TARGET EXCEEDED - investigate gaps"
fi
```

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                         |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| "Backups exist, so DR works"         | No. Backups are one part. DR also requires: tested procedures, monitoring, RTO/RPO targets, regular drills.     |
| "We don't need to test DR regularly" | Wrong. Untested DR procedures break when actually needed (configuration drift, dependencies changed).           |
| "RTO = 24 hours is acceptable"       | Depends on business. For critical systems (payment, healthcare), 24h is too long. For non-critical, acceptable. |
| "We can recover manually"            | Slow and error-prone. Manual recovery takes hours/days. Automated recovery takes minutes.                       |
| "Secondary DC is optional"           | For true DR, secondary in different geographic region is required (survive data center disaster).               |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Untested Recovery Procedure Fails During Real Disaster**

**Symptom:**
Primary DC down. Attempt failover. Steps in runbook don't work (dependencies changed, passwords expired, configurations stale).

**Prevention:**
Quarterly DR drills. Test full recovery, not just components. Automate recovery steps where possible.

---

**Failure Mode 2: Data Loss Exceeds RPO**

**Symptom:**
Expected RPO = 5 min. Actual data loss = 2 hours (replication lag was much higher than monitored).

**Prevention:**
Monitor replication lag continuously. Alert if approaching RPO threshold. Test replication under load.

---

### 🔗 Related Keywords

**Prerequisites:**

- `RTO/RPO`, `Redundancy`, `Backup Strategies`

**Builds On This:**

- `Geo-Replication`, `Multi-Region Architecture`, `Chaos Engineering`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Plan + infrastructure + testing to    │
│              │ recover from catastrophic failures    │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Disasters happen; without plan,       │
│ SOLVES       │ business destroyed                    │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Untested DR plan doesn't work; only   │
│              │ tested plans survive real disasters   │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Plan for worst, test regularly,      │
│              │ recover quickly."                     │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your RTO = 1 hour, RPO = 5 minutes. Primary DC fails. Secondary DC takes 45 min to become operational. You're within RTO. But failover testing shows actual time is 1.5 hours. Why the gap?

**Q2.** Post-disaster investigation: backups exist, but 2 days worth are corrupted (ransomware). How far back can you reliably restore?
