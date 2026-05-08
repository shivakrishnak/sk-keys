---
layout: default
title: "AWS Control Tower"
parent: "Cloud — AWS"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /cloud-aws/aws-control-tower/
id: AWS-017
category: Cloud — AWS
difficulty: ★★★
depends_on: AWS Organizations, AWS, Governance
used_by: Cloud — AWS
related: AWS Organizations, Landing Zone, Service Control Policies
tags:
  - aws
  - cloud
  - advanced
  - devops
  - architecture
---

# AWS-017 — AWS Control Tower

⚡ **TL;DR —** AWS Control Tower automates the setup of a secure, multi-account AWS environment (Landing Zone) with pre-built governance guardrails applied across all accounts from day one.

| | |
|---|---|
| **Depends on** | AWS Organizations, AWS, Governance |
| **Used by** | Cloud — AWS |
| **Related** | AWS Organizations, Landing Zone, Service Control Policies |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A company provisions 50 AWS accounts manually over two years. Each team sets up their own VPCs, IAM policies, CloudTrail, and Config rules — inconsistently. Some accounts have no MFA enforcement. Others have public S3 buckets. Audit reveals 20 compliance violations spread across 50 accounts. Remediating them requires manually touching every account.

**THE BREAKING POINT:** Cloud governance at scale requires consistency that humans cannot maintain manually. When a security policy changes, propagating it to 50 accounts by hand takes weeks, introduces errors, and leaves a window where non-compliant accounts exist.

**THE INVENTION MOMENT:** AWS built Control Tower to answer: what if every new AWS account started with the same security baseline applied automatically, and changing a policy pushed to all accounts simultaneously?

---

### 📘 Textbook Definition

**AWS Control Tower** is a managed service for setting up and governing a secure, multi-account AWS environment (called a **Landing Zone**). It automates the creation of a well-architected account structure using AWS Organizations, establishes baseline security controls (**guardrails**) enforced via Service Control Policies and AWS Config rules, and provides an **Account Factory** for provisioning new accounts with the governance baseline pre-applied.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A control panel that automates consistent, compliant multi-account AWS setup so every account starts secure.

**One analogy:**
> Control Tower is like a property management company for a large apartment building. The company sets the baseline standards (smoke detectors, fire exits, security locks) for every unit before any tenant moves in. Tenants can personalise their apartments but cannot remove fire safety equipment.

**One insight:** Control Tower is an opinion — it prescribes how a multi-account AWS estate should be structured. If you follow it, governance is automatic; if you fight it, you're doing governance manually.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. AWS accounts are the strongest isolation boundary — each account is a separate billing and permission domain.
2. Governance must be applied at provisioning time — retrofitting security controls to existing accounts is expensive and incomplete.
3. Preventive controls (cannot do X) are stronger than detective controls (alert when X happens).
4. Centralised log aggregation from all accounts is a prerequisite for any meaningful audit.

**DERIVED DESIGN:** Control Tower creates a Management Account that orchestrates child accounts via AWS Organizations. Organizational Units (OUs) group accounts by environment or business function. Service Control Policies applied at OU level prevent accounts from deviating from baseline (preventive guardrails). AWS Config rules within accounts detect drift from desired state (detective guardrails).

**THE TRADE-OFFS:**
**Gain:** Automated baseline, consistent governance across all accounts, Account Factory for self-service provisioning, built-in compliance dashboard.
**Cost:** Control Tower itself is free, but it provisions resources (CloudTrail, Config, S3 log archive, CloudWatch) that incur costs. Governance opinionation can conflict with existing non-standard architectures.

---

### 🧪 Thought Experiment

**SETUP:** Your organisation has 10 AWS accounts. A security policy mandates that no account can disable CloudTrail in any region.

**WHAT HAPPENS WITHOUT Control Tower:** You manually create a Config rule in each account. Over 6 months, 3 new accounts are provisioned by developers. None have the Config rule. CloudTrail is disabled in two of them. The audit tool doesn't cover new accounts automatically.

**WHAT HAPPENS WITH Control Tower:** The "Disallow changes to CloudTrail" guardrail is enabled at the OU level as a Service Control Policy. When the 3 new accounts are provisioned through Account Factory, they inherit the OU's SCP automatically. No developer in any account can disable CloudTrail — the API call is blocked by the SCP before it executes.

**THE INSIGHT:** Governance enforced at provisioning time via SCP is fundamentally different from governance applied retroactively via Config. SCP is preventive (impossible to violate); Config is detective (violation possible, then detected).

---

### 🧠 Mental Model / Analogy

> Control Tower is like a franchise model for AWS accounts. The franchisor (Management Account) sets mandatory standards (guardrails) that every franchise location (member account) must follow. New franchise locations (Account Factory) are opened with all standards pre-installed. Franchise owners can decorate their stores but cannot remove the mandatory safety equipment.

- **Franchisor** = Control Tower Management Account
- **Franchise standards** = guardrails (SCPs + Config rules)
- **Franchise locations** = individual AWS member accounts
- **Opening a new location** = Account Factory provisioning
- **Mandatory safety equipment** = preventive guardrails via SCP

Where this analogy breaks down: a real franchise can close non-compliant locations; Control Tower can only alert on violations (detective guardrails) unless a preventive SCP blocks the action entirely.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When a company uses many AWS accounts, Control Tower is the system that makes sure every account follows the same security rules automatically — without relying on each team to set things up correctly from scratch.

**Level 2 — How to use it (junior developer):**
Enable Control Tower in your Management Account. It creates a Landing Zone: a Logging account (centralised CloudTrail and Config logs) and an Audit account (read-only access for security review). Enable guardrails on OUs (e.g., "Disallow public S3 buckets in Sandbox OU"). Use Account Factory to provision new accounts that inherit all baseline controls.

**Level 3 — How it works (mid-level engineer):**
Control Tower orchestrates: AWS Organizations (OU structure), SSO/IAM Identity Center (centralised access), CloudTrail (all-region logging to centralised S3), AWS Config (aggregated rule compliance), and Service Control Policies (preventive guardrails). Guardrails are either `Mandatory` (always enabled, cannot be disabled), `Strongly Recommended` (enabled by default), or `Elective` (off by default). Preventive guardrails use SCPs to deny specific IAM actions at the organisation level. Detective guardrails use AWS Config rules to evaluate and report on resource state.

**Level 4 — Why it was designed this way (senior/staff):**
The two-guardrail model (preventive SCP + detective Config) maps to two different threat models. SCPs address malicious or accidental actions by account administrators — they make non-compliant actions impossible at the IAM policy evaluation layer, before any service API executes. Config rules address drift in resource configuration — they cannot prevent an action but create an audit record and can trigger automated remediation via SSM Automation. The design acknowledges that some governance requirements can be fully automated (preventive) while others require human judgment on detected findings (detective).

---

### ⚙️ How It Works (Mechanism)

1. **Landing Zone setup** — Control Tower creates Management Account, Log Archive Account, Audit Account, and a Root OU with Security and Sandbox OUs.
2. **Centralised logging** — CloudTrail trails in all member accounts write to the Log Archive Account S3 bucket. Config recorders aggregate to the Audit Account.
3. **Guardrails** — SCPs applied at OU level for preventive controls. AWS Config rules deployed to all accounts for detective controls.
4. **Account Factory** — uses AWS Service Catalog to provision new accounts with customisable baseline (VPC, IAM roles, tags, pre-applied guardrails). Backed by Account Factory for Terraform (AFT) for code-driven provisioning.
5. **IAM Identity Center** — centralised SSO for all accounts. Users log in once and access any permitted account via temporary role assumption.
6. **Control Tower Dashboard** — shows compliance status across all accounts: guardrail violations, non-compliant resources, account inventory.
7. **Drift detection** — if a change is made outside Control Tower (e.g., manually deleting an SCP), Control Tower detects and reports the drift, enabling remediation.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (new account provisioning):**
```
Platform Engineer
     |
     | Account Factory request (name, OU, email)
     v
Control Tower (Management Account)
     | [creates AWS Organizations account]
     | [applies OU-level SCPs]           ← YOU ARE HERE
     | [enables IAM Identity Center SSO]
     | [deploys Config rules]
     | [enables CloudTrail all-region]
     | [creates VPC baseline if configured]
     v
New Account (ready, compliant, governed)
     |
     | Developer receives SSO access
     v
Developer builds workloads in compliant account
```

**FAILURE PATH:**
- Account Factory fails mid-provisioning → account exists in partial state; requires manual remediation or deletion
- SCP blocks legitimate action → developer cannot perform valid operation; SCP must be revised at OU level
- Landing Zone drift → manual changes to Security OU SCPs break Control Tower's expected state

**WHAT CHANGES AT SCALE:**
At 200+ accounts, use Account Factory for Terraform (AFT) to define account provisioning as code (Git PR → account creation). Customisations are applied via AFT pipelines, not the console. This enables code review on governance changes.

---

### 💻 Code Example

**AWS CLI — check guardrail compliance:**
```bash
# List all enabled guardrails
aws controltower list-enabled-controls \
  --target-identifier \
    arn:aws:organizations::123:ou/o-abc/ou-abc-123

# Check Landing Zone status
aws controltower get-landing-zone \
  --landing-zone-identifier \
    arn:aws:controltower:us-east-1::landingzone/LZID

# List all accounts in the Landing Zone
aws controltower list-managed-accounts \
  --query 'managedAccounts[*].[name,status]' \
  --output table
```

**Account Factory for Terraform (AFT) — account request:**
```hcl
# account-request.tf
module "prod_account" {
  source = "./modules/aft-account-request"

  control_tower_parameters = {
    AccountEmail = "prod-team@company.com"
    AccountName  = "prod-payments"
    ManagedOrganizationalUnit = "Production"
    SSOUserEmail     = "platform-admin@company.com"
    SSOUserFirstName = "Platform"
    SSOUserLastName  = "Admin"
  }

  account_tags = {
    Environment  = "production"
    CostCenter   = "payments-team"
    DataClass    = "restricted"
  }

  change_management_parameters = {
    change_requested_by = "platform-team"
    change_reason       = "New payments workload"
  }
}
```

**Service Control Policy — deny public S3 buckets:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicS3ACL",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketAcl",
        "s3:PutObjectAcl"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": [
            "public-read",
            "public-read-write",
            "authenticated-read"
          ]
        }
      }
    }
  ]
}
```

---

### ⚖️ Comparison Table

| Feature | Control Tower | Manual AWS Organizations | Terraform + SCPs | Landing Zone Accelerator |
|---|---|---|---|---|
| **Setup complexity** | Low (wizard-driven) | High (manual) | High (code required) | Medium (template) |
| **Guardrail library** | 400+ built-in | None | Manual | Pre-built |
| **Account Factory** | Yes (Service Catalog) | No | Yes (AFT) | Yes |
| **Dashboard** | Yes (compliance view) | No | No (external) | Yes |
| **Customisation** | Limited (CfCT) | Full | Full | Full |
| **Terraform native** | Via AFT | N/A | Native | Via AFT |
| **Best for** | Standard enterprise setup | Full custom governance | Code-first orgs | Government/finance |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Control Tower replaces AWS Organizations" | Control Tower builds on top of AWS Organizations; Organizations is the underlying service managing the OU/account hierarchy. You cannot use Control Tower without Organizations. |
| "All guardrails are preventive (blocking)" | Guardrails are either preventive (SCP-based, blocking) or detective (Config-based, alerting). Most elective guardrails are detective — they report violations but don't block them. |
| "Control Tower is only for new accounts" | You can enrol existing accounts into Control Tower governance, though it requires applying SCPs and Config rules to existing accounts — a more complex process than new provisioning. |
| "Changing a guardrail takes effect immediately in all accounts" | SCP changes apply immediately at the OU level. Detective guardrails (Config) must be re-deployed to member accounts, which can take time depending on the update mechanism. |
| "Control Tower is free" | The Control Tower service is free. However, it provisions CloudTrail, Config, S3 (log archive), and CloudWatch in all accounts — these underlying services incur charges. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Account Factory provisioning fails mid-creation**
**Symptom:** Account Factory request hangs in `UNDER_CHANGE` state; account is created in Organizations but lacks baseline resources.
**Root Cause:** CloudFormation StackSet deployment in the new account failed (permission error, quota, region unavailability).
**Diagnostic:**
```bash
# Check Control Tower status
aws controltower get-landing-zone-operation \
  --operation-identifier <op-id>

# Check StackSet operations
aws cloudformation list-stack-set-operations \
  --stack-set-name \
    AWSControlTowerBP-BASELINE-CONFIG \
  --call-as DELEGATED_ADMIN
```
**Fix:** Identify the failed StackSet instance. Fix the root cause (IAM role, quota). Re-run provisioning via Account Factory or manually complete the StackSet deployment.
**Prevention:** Test Account Factory in a non-production OU first. Set up EventBridge rules to alert on provisioning failures within minutes.

**Mode 2: SCP blocking legitimate operations**
**Symptom:** Developer in a governed account cannot create an S3 bucket; receives `AccessDeniedException: Explicit Deny`.
**Root Cause:** A preventive guardrail SCP on the parent OU denies the action based on condition (region restriction, tagging requirement, etc.).
**Diagnostic:**
```bash
# Get the SCPs attached to the account's OU
aws organizations list-policies-for-target \
  --target-id ou-abc-123 \
  --filter SERVICE_CONTROL_POLICY \
  --query 'Policies[*].[Name,Id]'

# Get the SCP content
aws organizations describe-policy \
  --policy-id p-abc123 \
  --query 'Policy.Content' \
  --output text | python3 -m json.tool
```
**Fix:** Review the SCP condition. If the block is a false positive (e.g., region restriction on a new approved region), update the SCP at the OU level.
**Prevention:** Document all SCPs and their conditions in a runbook. Include SCP impact analysis in the change management process before enabling new guardrails.

**Mode 3: Landing Zone drift detected**
**Symptom:** Control Tower dashboard shows "Drift detected" for an account; compliance shows `DRIFTED`.
**Root Cause:** Someone manually modified an SCP, deleted a Control Tower-managed CloudTrail trail, or changed an IAM role outside of Control Tower.
**Diagnostic:**
```bash
# Get Landing Zone drift details
aws controltower list-landing-zone-operations \
  --filter Status=FAILED \
  --query 'landingZoneOperations[*]'

# Check CloudTrail for the change
aws cloudtrail lookup-events \
  --lookup-attributes \
    AttributeKey=EventName,\
AttributeValue=DeleteTrail
```
**Fix:** Repair the Landing Zone through the Control Tower console "Repair Landing Zone" action. This re-applies the expected baseline configuration.
**Prevention:** Apply SCPs that prevent modification of Control Tower-managed resources. Enable CloudWatch alarms on CloudTrail for Control Tower API events.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- AWS Organizations — Control Tower is built on Organizations; understand OUs, accounts, and SCP inheritance before using Control Tower.
- AWS IAM — SCPs modify IAM policy evaluation; IAM fundamentals are required to understand why preventive guardrails work.
- AWS CloudFormation — Control Tower uses StackSets to deploy baseline resources; CloudFormation knowledge helps troubleshoot provisioning failures.

**Builds On This (learn these next):**
- AWS CDK — use CDK with Customizations for Control Tower (CfCT) to define Landing Zone customisations as code.
- AWS Config — detective guardrails are Config rules; understanding Config aggregation and rule evaluation is essential for compliance reporting.
- CI/CD Pipelines — integrate Account Factory for Terraform (AFT) with a Git-based pipeline for code-reviewed account provisioning.

**Alternatives / Comparisons:**
- Landing Zone Accelerator — AWS solution for highly regulated industries (government, financial services) with pre-built compliance packages for NIST, PCI, HIPAA.
- Terraform Landing Zones — community and HashiCorp patterns for code-first multi-account governance without using Control Tower.
- AWS Organizations alone — fine-grained manual control without the opinionated structure; suitable for teams with existing governance automation.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Multi-account Landing Zone         |
|                  | automation with governance guardrails|
| PROBLEM IT SOLVES| Inconsistent account setup,        |
|                  | manual governance propagation       |
| KEY INSIGHT      | Preventive guardrails (SCP) make   |
|                  | violations impossible, not just     |
|                  | detectable                          |
| USE WHEN         | Scaling to multiple accounts,      |
|                  | regulated industries, consistent     |
|                  | security baseline required          |
| AVOID WHEN       | Single-account setups; highly       |
|                  | custom governance (use AFT/CfCT)    |
| TRADE-OFF        | Opinionated structure vs full      |
|                  | manual control over OU/SCP design   |
| ONE-LINER        | controltower:EnableControl         |
| NEXT EXPLORE     | AFT, Service Control Policies      |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** Preventive guardrails (SCPs) make non-compliant actions impossible, while detective guardrails (Config rules) only report violations after they occur. Given this difference, what category of governance requirement is fundamentally unsuitable for a preventive guardrail, and must always rely on detective controls?

2. **(Scale)** An organisation grows from 50 to 500 AWS accounts in 18 months. Account Factory through the Control Tower console becomes a bottleneck — the platform team processes 5–10 account requests per week manually. What architectural change (hint: AFT) enables account provisioning to scale to 50+/week with code review and automated testing?

3. **(Design Trade-off)** Control Tower's guardrail library contains 400+ built-in controls. Enabling too many guardrails blocks legitimate developer workflows; enabling too few leaves compliance gaps. What framework would you use to decide which guardrails are mandatory (all OUs), which are environment-specific (Production OU only), and which are elective?
