---
layout: default
title: "Toil"
parent: "DevOps & SDLC"
nav_order: 460
permalink: /devops-sdlc/toil/
---
# 460 — Toil

`#devops` `#sdlc` `#intermediate` `#sre` `#reliability`

⚡ TL;DR — Manual, repetitive, automatable operational work that scales linearly with service growth and provides no lasting value.

| #460 | Category: DevOps & SDLC | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SRE, Error Budget, Automation | |
| **Used by:** | SRE, Error Budget, Operational Excellence | |

---

### 📘 Textbook Definition

Toil (in SRE) is the kind of work tied to running a production service that is manual, repetitive, automatable, tactical, devoid of enduring value, and scales linearly with service growth. Google's SRE book establishes that toil should constitute less than 50% of an SRE's time — the rest must be engineering work that improves the service and reduces future toil.

---

### 🟢 Simple Definition (Easy)

Toil is **the repetitive manual work that keeps services running but doesn't make them better**. Restarting a service, manually approving tickets, copying data between systems — the same tasks over and over, forever, just to keep the lights on.

---

### 🔵 Simple Definition (Elaborated)

Toil is insidious because it feels productive — things are getting done. But toil grows with the service: double the users, double the manual ticket processing. It consumes engineering time that could be spent writing automation that eliminates the toil permanently. Google's SRE practice mandates a hard cap: if an engineer spends more than 50% of their time on toil, the organization must invest in automation.

---

### 🔩 First Principles Explanation

**The core problem:**
Operational tasks that start as "occasional" become daily rituals. Teams accept them as "just how things work." Meanwhile, the automation that would eliminate these tasks never gets written because the team is always busy doing the toil.

**The insight:**
> "Every hour spent on toil is an hour not spent making the system better, safer, and less toil-ful. Toil compounds — it grows with traffic without bound unless automated."

```
Toil characteristics (Google SRE definition):
  ✓ Manual           - requires a human to act
  ✓ Repetitive       - done over and over
  ✓ Automatable      - a machine could do it
  ✓ Tactical         - interrupt-driven, not proactive
  ✓ No enduring value - doing it once adds no lasting improvement
  ✓ Scales linearly  - grows proportionally to service load

Non-toil work (engineering work):
  ✓ Writing automation that eliminates toil permanently
  ✓ Improving system architecture to prevent incidents
  ✓ Building better monitoring and alerting
  ✓ Postmortem analysis and systemic improvements
```

---

### ❓ Why Does This Exist (Why Before What)

Without the concept of toil, operations teams normalize manual work as "just ops". This leads to burnout, high on-call burden, slow scaling (can't onboard more users without hiring more ops), and talent loss (engineers don't want to do manual work indefinitely).

---

### 🧠 Mental Model / Analogy

> Toil is like bailing water from a leaking boat. You bail and bail — it feels like progress. But you're never fixing the leak. An engineer who recognizes toil thinks: "How do I fix the hole, not just bail faster?" The SRE answer: automate the bailing and use the freed time to patch the hull.

---

### ⚙️ How It Works (Mechanism)

```
Toil identification framework:

  For each operational task, ask:
  1. Is it done repeatedly (daily/weekly/on-each-deploy)?
  2. Would it take roughly the same time if traffic doubled?
  3. Would a runbook or script handle it without human judgment?
  4. Does completing it just return things to baseline (no improvement)?

  YES to all four → it's toil → write automation to eliminate it

Common toil examples:
  - Manually restarting crashed pods/services
  - Processing approval tickets for routine operations
  - Copying data between systems on schedule
  - Updating config files before each deploy
  - Manually scaling infrastructure when traffic spikes
  - Responding to noisy, non-actionable alerts

Automation approaches:
  - Self-healing scripts (auto-restart on crash detection)
  - Automated scaling (HPA, autoscaling groups)
  - Pipeline automation (replace manual approval with CI gates)
  - Runbook automation (convert runbooks to scripts/operators)
```

---

### 🔄 How It Connects (Mini-Map)

```
[Toil identified]
       ↓
[Measure: hours/week spent]
       ↓ > 50% threshold
[Engineering sprint: automate it]
       ↓
[Automation deployed]
       ↓
[Toil reduced] --> [Error budget preserved] --> [Engineer time freed]
       ↓
[Use freed time to prevent next toil source]
```

---

### 💻 Code Example

```python
# TOIL: manual daily database cleanup script run by a human
# Someone runs this every morning by hand
def manual_cleanup():
    conn = get_db_connection()
    conn.execute("DELETE FROM sessions WHERE expires_at < NOW()")
    conn.execute("DELETE FROM temp_files WHERE created_at < NOW() - INTERVAL '7 days'")
    conn.commit()
    print("Manual cleanup done")
# This is toil: manual, repetitive, automatable, no lasting value

# ELIMINATING TOIL: convert to automated scheduled job
# kubernetes/cronjob-cleanup.yaml
```

```yaml
# Automated CronJob — eliminates the manual cleanup toil
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-cleanup
spec:
  schedule: "0 2 * * *"    # 2 AM every day, automatically
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: myapp-cleanup:latest
            command: ["python", "cleanup.py"]
          restartPolicy: OnFailure
# No human intervention needed — toil eliminated permanently
```

```bash
# TOIL: manual pod restart when OOM-killed (someone pages you at 2am)
kubectl delete pod myapp-xyz-abc -n production

# ELIMINATING TOIL: configure proper memory limits + liveness probes
# So Kubernetes auto-restarts unhealthy pods without paging anyone
# AND fix the memory leak that causes the OOM so restarts stop happening
```

---

### 🔁 Flow / Lifecycle

```
1. Identify: log all operational tasks for 2 weeks
        ↓
2. Classify: is each task toil? (manual, repetitive, automatable)
        ↓
3. Measure: total hours per week on toil
        ↓
4. Prioritise: highest-impact toil (time cost × frequency)
        ↓
5. Engineer: write automation to eliminate the top toil
        ↓
6. Deploy: schedule, self-heal, or pipeline automation
        ↓
7. Verify: toil hours drop; track over time
        ↓
8. Repeat for next toil source
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| All operational work is toil | Incident response with novel problems, postmortems = not toil |
| Toil is inevitable | Most toil CAN be automated; accepting it is a choice |
| Paying toil down is optional | > 50% toil triggers mandatory SRE remediation (per Google) |
| Automation always eliminates toil on first try | Some automation creates new toil (maintaining scripts); design carefully |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Toil Becomes Invisible**
Teams normalize toil to the point where they don't track it.
Fix: require engineers to log time by category (toil vs engineering); review monthly.

**Pitfall 2: Automating Toil That Should Be Fixed Instead**
Auto-restarting a service that crashes daily — automation hides the real problem.
Fix: automation buys time; use that time to fix the root cause, not just manage the symptom.

**Pitfall 3: Alert Fatigue as Toil**
Responding to dozens of non-actionable alerts daily — a classic toil source.
Fix: audit alerts; delete non-actionable ones; reduce signal-to-noise ruthlessly.

---

### 🔗 Related Keywords

- **SRE** — the practice that defines and measures toil
- **Error Budget** — toil consumes error budget if it leads to incidents; eliminating toil frees engineers to protect the budget
- **Automation** — the solution to toil; converts repetitive work to self-running systems
- **Alert Fatigue** — a common form of toil from noisy, non-actionable alerts
- **Blameless Postmortem** — the process that identifies systemic toil sources after incidents

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Manual, repetitive, automatable work that     │
│              │ scales with traffic — must be eliminated      │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Auditing operational work; building SRE       │
│              │ roadmap; justifying automation investment     │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — all toil should be reduced; > 50%      │
│              │ is an organizational red flag                 │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "If you do it twice, automate it.             │
│              │  If you don't, it will eat you alive at scale"│
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ SRE --> Error Budget --> Automation --> IaC   │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between toil and "valuable operational work" — where is the line?  
**Q2.** Why is automating a daily restart script insufficient if the root cause (frequent crashes) is not addressed?  
**Q3.** How does toil relate to the error budget — can toil consume error budget even without incidents?

