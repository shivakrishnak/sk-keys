---
version: 2
layout: default
title: "Terraform Drift Detection"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 67
permalink: /ci-cd/terraform-drift-detection/
id: CCD-069
category: CI/CD
difficulty: ★★★
depends_on: Terraform State, Terraform Plan  Apply  Destroy
used_by: CI-CD
related: Terraform State, Policy as Code, Observability & SRE
tags:
  - cicd
  - devops
  - advanced
  - production
---

# CCD-068 - Terraform Drift Detection

⚡ **TL;DR -** Drift detection uses `terraform plan` to identify differences between the current cloud reality and Terraform's declared desired state.

| Field | Value |
|---|---|
| **Depends on** | Terraform State, Terraform Plan  Apply  Destroy |
| **Used by** | CI-CD |
| **Related** | Terraform State, Policy as Code, Observability & SRE |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** An engineer makes an emergency console change at 3 AM to fix an outage. They forget to update the Terraform code. Three months later, `terraform apply` is run as part of a CI/CD deployment. The "fix" is silently reverted. The original outage recurs. Nobody knows why.

**THE BREAKING POINT:** A compliance audit requires evidence that production infrastructure matches the declared configuration. But engineers have been making console changes "just this once" for months. The Terraform code and the real cloud are different in 47 places. Nobody knows which differences are intentional.

**THE INVENTION MOMENT:** A scheduled CI job runs `terraform plan -detailed-exitcode` every hour. Exit code 2 means drift. An alert fires. The team investigates before the drift causes an incident.

---

### 📘 Textbook Definition

**Terraform drift detection** is the practice of using `terraform plan` (with `--refresh-only` or a full plan) to identify *configuration drift* - discrepancies between the infrastructure's actual current state and Terraform's declared desired configuration. Drift occurs when infrastructure is modified outside Terraform (manual console changes, automation scripts, cloud autoscaling). Drift detection CI jobs surface these discrepancies before they cause incidents or compliance violations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Run `terraform plan` on a schedule; exit code 2 means someone changed something outside Terraform.

> Drift detection is like a security camera for your infrastructure: it continuously monitors whether the real world matches your blueprint, and alerts you the moment something diverges.

**One insight:** `terraform plan -refresh-only` shows what *Terraform's state* would need to change to match reality - this is drift that happened *outside* Terraform. A full `terraform plan` shows what *reality* would need to change to match your HCL - this catches both drift and code changes not yet applied.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Drift is any difference between declared state (HCL) and actual state (cloud API).
2. `terraform plan -detailed-exitcode` returns exit code 2 if there are pending changes.
3. `terraform plan -refresh-only` isolates drift from outside-Terraform changes.
4. Remediating drift requires a decision: update HCL to accept the drift, or re-apply to revert it.

**DERIVED DESIGN:** A scheduled pipeline runs `terraform plan`, captures exit code 2, and sends an alert. The alert payload includes the plan output showing exactly which resources drifted and how. The on-call engineer decides: this change was intentional (update HCL) or unauthorized (re-apply).

**THE TRADE-OFFS:**
**Gain:** Early drift visibility; compliance evidence; catch unauthorized changes before they cause incidents.
**Cost:** Scheduled plans add load to provider APIs; false positives from provider attribute normalization; alert fatigue if too frequent.

---

### 🧪 Thought Experiment

**SETUP:** Your Terraform configuration manages an EC2 security group. An on-call engineer adds an inbound rule manually at 3 AM to diagnose an issue. They forget to update the HCL.

**WHAT HAPPENS WITHOUT DRIFT DETECTION:** Three weeks later, a routine `terraform apply` removes the security group rule (it's not in HCL). The application that relied on that rule stops working. Incident. Post-mortem reveals the console change from three weeks ago. A simple scheduled plan would have caught this the next morning.

**WHAT HAPPENS WITH DRIFT DETECTION:** The next scheduled drift check (8 AM) shows: `~ aws_security_group.app: ingress rule added outside Terraform`. On-call engineer is paged. They decide: keep the rule → update HCL + PR. Revert → `terraform apply`.

**THE INSIGHT:** Drift detection turns an invisible, accumulating problem into a visible, immediate one. The earlier you detect drift, the cheaper it is to resolve.

---

### 🧠 Mental Model / Analogy

> Drift detection is like a daily inventory check in a warehouse: the manifest (HCL) says what should be on the shelves (cloud resources). The daily check (scheduled plan) compares the manifest to the actual shelves. Any discrepancy triggers an investigation before the inventory error compounds.

- Warehouse manifest → HCL configuration
- Actual shelves → real cloud resources
- Daily inventory check → scheduled `terraform plan`
- Discrepancy alert → CI notification (exit code 2)
- Inventory reconciliation → apply or HCL update

Where this analogy breaks down: unlike warehouse inventory, cloud resources can change value (security group rules added/removed) without the resource itself disappearing - drift is often an attribute-level change, not a resource-level one.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Drift detection checks whether your cloud infrastructure still matches your Terraform code. If someone changed something in the console, drift detection finds it.

**Level 2 - How to use it (junior developer):** Run `terraform plan -detailed-exitcode` in a scheduled CI job. If exit code is 2, send an alert. The plan output shows exactly what drifted. Review whether the drift is intentional or unauthorized.

**Level 3 - How it works (mid-level engineer):** `terraform plan` performs a refresh (calls provider ReadResource for every state entry) to get the current cloud state. It then diffs the refreshed state against the desired HCL configuration. `-refresh-only` generates a plan that, if applied, would update state to match reality without changing resources. `-detailed-exitcode` enables CI exit code semantics.

**Level 4 - Why it was designed this way (senior/staff):** Drift detection uses the same mechanism as normal plan - there's no special "drift scan" mode. This is intentional: the same tool that deploys infrastructure also monitors it. The `-refresh-only` flag is critical for large organizations where you want to observe drift without automatically reverting it - the remediation decision requires human judgment.

---

### ⚙️ How It Works (Mechanism)

**Exit codes for `-detailed-exitcode`:**
| Code | Meaning |
|---|---|
| `0` | No changes; infrastructure matches configuration |
| `1` | Error during plan |
| `2` | Changes present (drift or undeployed HCL changes) |

**Drift vs pending changes:**
- **Drift:** Resource attribute changed outside Terraform (`-refresh-only` shows it)
- **Pending:** HCL change not yet applied (standard plan shows it)
- **Both:** Use `terraform plan -refresh-only` + separate full plan to distinguish

---

### 🔄 The Complete Picture - End-to-End Flow

**SCHEDULED DRIFT DETECTION FLOW:**
```
  Scheduled CI job (hourly/daily)
           │
  terraform init -backend-config=...
           │
  terraform plan \               ← YOU ARE HERE
    -refresh-only \
    -detailed-exitcode \
    -out=drift.tfplan
           │
  Exit code 0: No drift → pass
  Exit code 2: Drift detected
           │
  Alert: Slack/PagerDuty
  Attach plan output showing diffs
           │
  On-call engineer reviews
           │
  Decision A: Drift is intentional
  → Update HCL → PR → apply
           │
  Decision B: Drift is unauthorized
  → terraform apply -refresh-only
    (update state to match reality)
  → then full terraform apply
    (revert unauthorized change)
```

**FAILURE PATH:** Drift detection job runs but the scheduled drift is so large (30+ resources) that no one investigates. Alert fatigue sets in. The drift grows silently for months. Don't let drift accumulate - resolve alerts same day.

**WHAT CHANGES AT SCALE:** Terraform Cloud and Enterprise have built-in drift detection with workspace-level notifications. Third-party tools (Driftctl, Infracost) provide richer drift reports. For multi-account AWS, the drift job must assume-role into each account.

---

### 💻 Code Example

```bash
#!/bin/bash
# drift-check.sh - scheduled drift detection script

set -e

# Initialize with backend
terraform init \
  -backend-config="bucket=${TF_STATE_BUCKET}" \
  -backend-config="key=${TF_STATE_KEY}" \
  -input=false

# Run refresh-only plan to detect out-of-band changes
terraform plan \
  -refresh-only \
  -detailed-exitcode \
  -out=drift.tfplan \
  -input=false \
  -no-color 2>&1 | tee plan_output.txt

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ No drift detected"
  exit 0
elif [ $EXIT_CODE -eq 2 ]; then
  echo "⚠️ DRIFT DETECTED - see plan output"
  cat plan_output.txt
  # Send alert to Slack
  curl -X POST "${SLACK_WEBHOOK}" \
    -H 'Content-type: application/json' \
    --data "{\"text\":\"🚨 Terraform drift detected in ${TF_ENV}!\nSee CI job for details.\"}"
  exit 2
else
  echo "❌ Terraform plan error"
  exit 1
fi
```

```yaml
# GitHub Actions: scheduled drift detection
name: Terraform Drift Detection

on:
  schedule:
    - cron: '0 */6 * * *'  # every 6 hours

jobs:
  drift-check:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111111:role/terraform-drift
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.7"

      - name: Terraform Init
        run: terraform init

      - name: Drift Check
        id: drift
        run: |
          terraform plan -refresh-only \
            -detailed-exitcode \
            -no-color 2>&1 | tee plan_output.txt
          echo "exit_code=$?" >> $GITHUB_OUTPUT
        continue-on-error: true

      - name: Alert on Drift
        if: steps.drift.outputs.exit_code == '2'
        run: |
          echo "Drift detected! Sending alert..."
          # Add Slack/PagerDuty notification here
```

---

### ⚖️ Comparison Table

| Approach | Scheduled Plan | AWS Config Rules | Driftctl | Terraform Cloud |
|---|---|---|---|---|
| **Terraform-native** | ✅ | ❌ | Partial | ✅ |
| **Detects all drift** | ✅ | Resource types only | ✅ | ✅ |
| **Remediation link** | ✅ (apply) | Manual | Partial | ✅ |
| **Cost** | CI cost only | AWS Config cost | Open source | Per workspace |
| **Setup effort** | Low | Medium | Low | Low (SaaS) |
| **Best for** | Self-hosted Terraform | AWS-specific drift | Drift reporting | Terraform Cloud users |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Drift detection automatically fixes drift" | It only detects drift. Remediation requires a human decision: update HCL or re-apply. |
| "`terraform plan` always shows drift" | Full plan shows both HCL changes and drift together. Use `-refresh-only` to isolate drift from pending HCL changes. |
| "Daily drift checks are sufficient for security" | Security-sensitive resources (security groups, IAM) need more frequent checks. High-risk resources warrant 15-minute polling. |
| "Drift means something is wrong" | Autoscaling changes instance counts, tagging pipelines add tags. Not all drift is unauthorized. Drift requires investigation, not automatic revert. |
| "Drift is only about manual console changes" | Cloud services modify resources autonomously: auto-scaling, managed certificate renewal, automated patching. All create drift. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Perpetual Drift from Provider Normalization**
- **Symptom:** Drift detection always shows changes to the same attributes (e.g. tag ordering, whitespace in policies) even when no one touched them
- **Root Cause:** Provider normalizes attribute values differently than HCL representation
- **Diagnostic:**
```bash
terraform plan -refresh-only 2>&1 | grep "~" | head -20
```
- **Fix:** Update HCL to match the normalized form the provider stores. Alternatively, use `lifecycle { ignore_changes = [tags] }` for volatile attributes.
- **Prevention:** Run plan after every apply and review unexpected attribute normalization.

**Mode 2: Alert Fatigue from Autoscaling**
- **Symptom:** Drift alerts fire every 30 minutes because ASG desired_capacity changes constantly
- **Root Cause:** Autoscaling modifies the resource, creating drift vs the HCL `desired_capacity`
- **Diagnostic:** Confirm the drift is only in scaling attributes.
- **Fix:** Add `lifecycle { ignore_changes = [desired_capacity] }` to ASG resources.
- **Prevention:** Explicitly ignore autoscaler-managed attributes; keep drift checks focused on security-relevant attributes.

**Mode 3: Drift Detection Misses Cross-Resource Changes**
- **Symptom:** Drift check passes, but an IAM policy attached to a role was modified directly
- **Root Cause:** The changed resource is not managed by Terraform - it's a separate resource not in the state
- **Diagnostic:**
```bash
# Drift detection only covers Terraform-managed resources
terraform state list | grep iam
# Resources not in state are invisible to drift detection
```
- **Fix:** Import the resource into Terraform management; expand state coverage.
- **Prevention:** Use SCPs to block direct IAM modifications; enforce all changes through Terraform.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform State, Terraform Plan / Apply / Destroy, Terraform Overview

**Builds On This (learn these next):** Policy as Code, Observability & SRE, CI-CD

**Alternatives / Comparisons:** AWS Config drift detection, Driftctl, Terraform Cloud health checks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Scheduled plan to detect out-of-band │
│               │ infrastructure changes               │
│ PROBLEM       │ Console changes silently break IaC   │
│ KEY INSIGHT   │ -refresh-only isolates drift from    │
│               │ pending HCL changes                  │
│ USE WHEN      │ Production environments; compliance  │
│ AVOID WHEN    │ Resources legitimately auto-change   │
│ TRADE-OFF     │ Alert accuracy vs API call frequency │
│ ONE-LINER     │ plan -refresh-only -detailed-exitcode│
│ NEXT EXPLORE  │ Policy as Code, Sentinel             │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** An AWS Auto Scaling Group managed by Terraform constantly triggers drift alerts because the ASG's `desired_capacity` changes as traffic fluctuates. The `lifecycle { ignore_changes }` pattern suppresses the alert. What are the conditions under which ignoring changes to a resource attribute is safe vs dangerous, and how do you decide which attributes to include in `ignore_changes`?

2. **(Production)** Your drift detection runs every hour and correctly detects that a security group rule was added manually. The on-call engineer decides to revert by running `terraform apply`. However, the manual rule was added to fix an active production issue that the Terraform code hasn't been updated to handle. What process should govern the decision between "update HCL to accept drift" and "revert via apply," and who has authority to make that call?

3. **(Root Cause)** Drift detection shows that 15 EC2 instances have an extra tag (`LastPatched`) that doesn't exist in the Terraform HCL. Investigation reveals an automated patching system adds this tag. How should this be handled in Terraform to prevent false drift alerts while ensuring the patching tag remains auditable?
