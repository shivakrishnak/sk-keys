---
layout: default
title: "AWS Well-Architected Review"
parent: "Cloud — AWS"
nav_order: 24
permalink: /cloud-aws/aws-well-architected-review/
id: AWS-024
category: Cloud — AWS
difficulty: ★★★
depends_on: Cloud — AWS, Architecture Review, AWS
used_by: Cloud — AWS
related: AWS Cost Tagging Strategy, Architecture Decision Record (ADR), SRE
tags:
  - aws
  - cloud
  - advanced
  - architecture
  - bestpractice
---

# AWS-024 — AWS Well-Architected Review

⚡ **TL;DR —** A structured AWS framework for evaluating workload architecture across six pillars — identifying risks, prioritising improvements, and building systems that are secure, reliable, efficient, cost-effective, sustainable, and operationally excellent.

|                |                                                                    |
| -------------- | ------------------------------------------------------------------ |
| **Depends on** | Cloud — AWS, Architecture Review, AWS                              |
| **Used by**    | Cloud — AWS                                                        |
| **Related**    | AWS Cost Tagging Strategy, Architecture Decision Record (ADR), SRE |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A team builds a new AWS workload. It works. They launch. Six months later: a DDoS attack takes the service down for 4 hours (security gap), a single AZ failure causes a 2-hour outage (reliability gap), the database has no read replicas (performance gap), and the bill is 40% higher than budgeted because Dev environments run 24/7 (cost gap). Each problem was knowable before launch — but no structured review happened.

**THE BREAKING POINT:** Technical debt in cloud architecture is invisible until it becomes a production incident, a compliance failure, or a runaway bill. Teams optimise for speed to launch — deferring reliability, security, and cost concerns until they become painful emergencies.

**THE INVENTION MOMENT:** AWS codified the lessons from thousands of customer architecture reviews into a reusable framework: if you evaluate your workload against these questions before launch and periodically after, you will find the high-risk gaps before they become incidents.

---

### 📘 Textbook Definition

**The AWS Well-Architected Framework** is a structured set of architectural best practices and questions organised into six **pillars** — Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimisation, and Sustainability. A **Well-Architected Review** is a collaborative, question-driven evaluation of a workload against the framework, resulting in a list of identified **risks** (High/Medium) and an **improvement plan** with prioritised remediation steps. The **AWS Well-Architected Tool** automates the review process in the AWS console.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A six-pillar checklist built from AWS's lessons learned across thousands of production workloads — find your architecture risks before they find you.

**One analogy:**

> The Well-Architected Review is like a pre-flight checklist for a commercial aircraft. Pilots use the same structured checklist before every flight regardless of experience level — because experience alone cannot guarantee nothing is missed. The checklist exists precisely because human memory is unreliable under time pressure. A failed check (identified risk) means a decision: fix it now or accept the documented risk.

**One insight:** The framework doesn't tell you what to build — it tells you what questions to ask and what risks you are accepting if you cannot answer "yes."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every architecture embodies a set of trade-offs. The framework makes those trade-offs explicit and documented.
2. Risks that are identified and accepted are acceptable. Risks that are unknown are dangerous.
3. The six pillars are interdependent — optimising one (cost) often degrades another (reliability). The framework surfaces these tensions.
4. A review is not a one-time event — workloads evolve and must be re-reviewed periodically or after significant changes.

**DERIVED DESIGN:** Each pillar contains design principles and a set of best practice questions with multiple-choice answers. Each answer maps to a set of best practices; unanswered or "not followed" responses generate risk findings. The framework intentionally avoids prescriptive solutions — it identifies gaps; the team decides remediation. This design respects that context varies: a startup's acceptable risk level differs from a bank's.

**THE TRADE-OFFS:**
**Gain:** Structured risk identification, shared vocabulary for architectural discussions, documented risk acceptance, improvement roadmap, alignment with AWS best practices.
**Cost:** A full review takes 1–3 days with a qualified reviewer. Improvement plans create technical backlog. Without follow-through on findings, the review is a checkbox exercise.

---

### 🧪 Thought Experiment

**SETUP:** Your team launches a checkout API serving $10M/month in transactions without a Well-Architected Review.

**WHAT HAPPENS:** In month 3, a burst of transactions causes a Lambda function to hit its reserved concurrency limit. Requests begin failing silently — no dead letter queue. 2% of transactions are lost before the on-call engineer notices. $200K in revenue impacted before the fix.

**WHAT HAPPENS WITH a pre-launch review:** Reliability Pillar Question: "How do you use fault isolation to protect your workload?" — answer: "We don't use fault isolation for async processing." Finding: Medium Risk. Remediation: add Dead Letter Queues to all SQS-triggered Lambdas. Time to fix: 2 hours. Cost: $0 in data loss.

**THE INSIGHT:** The Well-Architected Review is a structured forcing function that converts implicit architectural assumptions into explicit documented decisions — before those assumptions cause incidents.

---

### 🧠 Mental Model / Analogy

> The Well-Architected Framework is like a full vehicle inspection before a long road trip. It covers six systems: brakes (security), engine reliability (reliability), fuel efficiency (cost), performance (performance), emissions (sustainability), and trip planning (operational excellence). You might find that the brakes are 80% and the tyre pressure is low. You decide: fix the brakes now (high risk), check the tyres at the next stop (medium risk), or accept both and drive carefully (document and accept). The trip happens — but now with eyes open.

- **Vehicle inspection checklist** = Well-Architected Review questions
- **Six vehicle systems** = six pillars of the framework
- **Mechanic's findings** = identified High/Medium risks
- **Fix vs drive cautiously** = remediate vs accept risk
- **Periodic inspection schedule** = annual/milestone re-review

Where this analogy breaks down: a car inspection has objectively correct answers (brakes are either safe or not); Well-Architected answers are contextual — a "no" answer is acceptable if the team understands and documents the trade-off.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Well-Architected Review is a structured health check for your AWS system. AWS gives you a list of questions covering security, reliability, performance, cost, sustainability, and operations. Your answers show where your system might fail or cost too much — before it does.

**Level 2 — How to use it (junior developer):**
Open the AWS Well-Architected Tool in the console. Create a workload. Answer the questions for each pillar. The tool identifies High and Medium risks. Export the findings. Prioritise the High risks for your next sprint. Use the improvement guidance linked to each finding to understand what to fix.

**Level 3 — How it works (mid-level engineer):**
The review is usually conducted as a facilitated workshop with the technical team and an architect. Questions are grouped by Design Principle per pillar. Each question has best-practice choices — you select which ones apply to your workload. The gap between best practice and your current state generates a risk. Risk severity is contextual — the reviewer marks findings as High Risk (immediate action), Medium Risk (scheduled improvement), or addressed. The resulting improvement plan is treated like a product backlog and prioritised by business impact.

**Level 4 — Why it was designed this way (senior/staff):**
The framework's question-driven (rather than prescription-driven) design solves a fundamental problem in architecture guidance: universal prescriptions create compliance theatre. A startup serving 1,000 users/day and a financial institution serving 10M transactions/hour have fundamentally different reliability requirements. By asking "How do you handle partial failure?" rather than prescribing "use circuit breakers," the framework elicits a decision and a rationale rather than a checkbox. The documented risk acceptance model is particularly important — it creates an explicit record that the team evaluated a risk and chose to accept it, which is vastly different from "the team didn't know about it." This distinction matters in post-mortems, audits, and architectural debt discussions.

---

### ⚙️ How It Works (Mechanism)

**The Six Pillars:**

1. **Operational Excellence** — ability to run and monitor systems to deliver business value, continuously improving processes and procedures. Questions: How do you define workload success? How do you know when things go wrong? How do you learn from failures?

2. **Security** — protecting data, systems, and assets. Questions: How do you manage identities? How do you detect security events? How do you protect data at rest and in transit?

3. **Reliability** — workload performs its intended function correctly and consistently. Questions: How do you design for availability? How do you handle component failure? How do you test recovery procedures?

4. **Performance Efficiency** — using computing resources efficiently and adapting to demand. Questions: How do you select the right resource types? How do you monitor performance? How do you trade off consistency and availability?

5. **Cost Optimisation** — avoiding unnecessary costs and reducing spending. Questions: How do you govern resource usage? How do you decompose usage costs? How do you manage demand?

6. **Sustainability** — minimising environmental impact of cloud workloads. Questions: How do you select Regions for sustainability? How do you align consumption with demand? How do you use managed services to reduce footprint?

**Review Process:**

1. Define the workload scope and architecture diagram.
2. Conduct facilitated pillar-by-pillar question walkthrough.
3. Record answers and identify risks in Well-Architected Tool.
4. Generate risk report.
5. Create improvement plan: prioritise High risks, schedule Medium risks.
6. Re-review after major changes or annually.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (workload review):**

```
Architecture team + AWS Solutions Architect
     |
     | 1. Define workload (name, env, lens)
     v
Well-Architected Tool (WAT)
     | 2. Answer questions per pillar
     |    Operational Excellence: 10 questions
     |    Security: 11 questions
     |    Reliability: 11 questions
     |    Performance Efficiency: 8 questions
     |    Cost Optimisation: 9 questions
     |    Sustainability: 6 questions
     |                        ← YOU ARE HERE
     | 3. Tool generates risk summary
     v
Risk Report: 3 High, 8 Medium, 22 Low
     |
     | 4. Prioritise High risks for sprint backlog
     | 5. Accept + document Medium risks
     v
Improvement Plan (Jira/Confluence)
     |
     | 6. Implement fixes over 2-4 sprints
     v
Re-review in 12 months or after major change
```

**FAILURE PATH:**

- Review conducted as checkbox exercise without honest answers → findings are underreported; real risks remain hidden
- Findings not translated into actionable tickets → improvement plan sits in a document; architecture doesn't improve
- Review done once at launch but never repeated → workload evolves; risks introduced post-launch go undetected

**WHAT CHANGES AT SCALE:**
At 50+ workloads, use the AWS Well-Architected Tool API to automate review creation, milestone tracking, and risk aggregation across workloads. Use AWS Trusted Advisor (automated checks) as a continuous lightweight substitute between formal reviews. Integrate WAT findings with Jira/ServiceNow via the WAT API for automated ticket creation.

---

### 💻 Code Example

**AWS CLI — Well-Architected Tool workload management:**

```bash
# Create a workload in the WAT
aws wellarchitected create-workload \
  --workload-name "CheckoutAPI-Prod" \
  --description "Payment checkout service" \
  --environment PRODUCTION \
  --review-owner "platform-team@company.com" \
  --aws-regions us-east-1 eu-west-1 \
  --lenses \
    wellarchitected \
    serverless \
  --query 'WorkloadId'

# List questions for the Security pillar
aws wellarchitected list-answers \
  --workload-id <workload-id> \
  --lens-alias wellarchitected \
  --pillar-id security \
  --query 'AnswerSummaries[*].[QuestionTitle,Risk]'

# Update an answer for a question
aws wellarchitected update-answer \
  --workload-id <workload-id> \
  --lens-alias wellarchitected \
  --question-id sec_securely_operate \
  --selected-choices \
    SEC_SECURELY_OPERATE_MULTI_ACCOUNTS \
    SEC_SECURELY_OPERATE_IDENTITY_PROVIDER

# Get risk summary
aws wellarchitected get-lens-review \
  --workload-id <workload-id> \
  --lens-alias wellarchitected \
  --query \
    'LensReview.RiskCounts'

# Export full report
aws wellarchitected get-lens-review-report \
  --workload-id <workload-id> \
  --lens-alias wellarchitected \
  --query 'LensReviewReport.Base64String' \
  --output text | base64 -d > review-report.pdf

# Create a milestone (point-in-time snapshot)
aws wellarchitected create-milestone \
  --workload-id <workload-id> \
  --milestone-name "Q1-2024-Review"
```

**AWS CDK — Trusted Advisor checks (automated continuous review):**

```typescript
import * as support from "aws-cdk-lib/aws-support";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";

// EventBridge rule for Trusted Advisor findings
const rule = new events.Rule(this, "TrustedAdvisorRule", {
  eventPattern: {
    source: ["aws.trustedadvisor"],
    detailType: ["Trusted Advisor Check Item Refreshed"],
    detail: {
      status: ["ERROR", "WARN"],
      "check-name": [
        "Security Groups - Unrestricted Access",
        "MFA on Root Account",
        "Low Utilization Amazon EC2 Instances",
      ],
    },
  },
});

rule.addTarget(new targets.SnsTopicV2(alertTopic));
```

**Six Pillars — key questions per pillar (reference):**

```
OPERATIONAL EXCELLENCE
  OPS 1: How do you determine workload priorities?
  OPS 5: How do you reduce defects & enable remediation?
  OPS 8: How do you understand workload health?

SECURITY
  SEC 1: How do you manage identities for humans/machines?
  SEC 3: How do you detect and investigate security events?
  SEC 8: How do you protect data at rest?

RELIABILITY
  REL 5: How do you design to mitigate disruptions?
  REL 9: How do you test reliability?
  REL 10: How do you plan for DR?

PERFORMANCE EFFICIENCY
  PERF 1: How do you select the best performing architecture?
  PERF 5: How do you use trade-offs to improve performance?

COST OPTIMISATION
  COST 3: How do you monitor and decommission resources?
  COST 6: How do you plan and manage expenditure?

SUSTAINABILITY
  SUS 2: How do you align cloud resources with demand?
  SUS 5: How do you use software patterns for sustainability?
```

---

### ⚖️ Comparison Table

| Feature       | Well-Architected Review      | Architecture Review Board | Threat Modelling              | FinOps Review           |
| ------------- | ---------------------------- | ------------------------- | ----------------------------- | ----------------------- |
| **Scope**     | 6 pillars, holistic          | Organisation-specific     | Security/attack vectors       | Cost only               |
| **Format**    | Question-driven              | Document/presentation     | Structured attack enumeration | Bill analysis           |
| **Output**    | Risk list + improvement plan | Approval/rejection        | Threat mitigations            | Savings opportunities   |
| **Frequency** | Annually / major change      | At design time            | Per feature/service           | Monthly/quarterly       |
| **Tool**      | AWS Well-Architected Tool    | Internal governance       | Threat Dragon, STRIDE         | Cost Explorer, Budgets  |
| **Best for**  | AWS workload holistic health | Governance gate           | Security-critical systems     | Cost optimisation focus |

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                                                                                                                     |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "A Well-Architected Review means your architecture is compliant" | The review identifies risks and trade-offs. A workload can pass a review with accepted High risks. It is a risk awareness tool, not a compliance certification.                                                             |
| "You need an AWS Solutions Architect to do the review"           | Any engineer trained in the framework can conduct a review. AWS partners and internal architects add expertise, but the tool is self-service.                                                                               |
| "The review is only for new workloads"                           | Reviews are most valuable as periodic health checks on existing workloads. Architecture drift, team changes, and new AWS services create new risks over time.                                                               |
| "Addressing every finding is mandatory"                          | Findings are prioritised and some are explicitly accepted with documented rationale. The goal is to make risk acceptance a conscious decision, not to achieve zero findings.                                                |
| "The six pillars are independent"                                | The pillars are deeply interdependent. Increasing reliability (multi-AZ, redundancy) increases cost. Increasing performance (larger instances) decreases cost efficiency. The framework surfaces these tensions explicitly. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Review findings not acted upon — checkbox exercise**
**Symptom:** Well-Architected Review was completed 12 months ago. The same 3 High Risks from the review remain open. No improvements implemented.
**Root Cause:** Review findings were not translated into engineering backlog items with owners and deadlines. Engineering prioritised feature delivery over infrastructure improvements.
**Diagnostic:**

```bash
# Check current risk status vs last milestone
aws wellarchitected list-milestones \
  --workload-id <workload-id> \
  --query 'MilestoneSummaries[*].[MilestoneName,
    RiskCounts]'

# Compare current risks to first milestone
aws wellarchitected get-answer \
  --workload-id <workload-id> \
  --lens-alias wellarchitected \
  --milestone-number 1 \
  --question-id <high-risk-question-id> \
  --query 'Answer.Risk'
```

**Fix:** Treat Well-Architected improvement items as first-class backlog items. Assign owners. Set 30/60/90-day targets for High Risk items. Report progress in engineering all-hands.
**Prevention:** Integrate WAT findings into Jira via the WAT API automatically after each review. Assign High Risk items to engineering team leads with due dates in the ticket.

**Mode 2: Workload evolved significantly but review not repeated**
**Symptom:** Original WAT review was for a monolith. The architecture was migrated to microservices 8 months ago. The WAT review still shows the monolith's answers. New risks from the migration (inter-service authentication, distributed tracing, saga patterns) are undetected.
**Root Cause:** No trigger was set to initiate a re-review after the major architectural change.
**Diagnostic:**

```bash
# Check when the last review/milestone was created
aws wellarchitected list-milestones \
  --workload-id <workload-id> \
  --query 'MilestoneSummaries[0].[MilestoneName,
    RecordedAt]'
```

**Fix:** Initiate a new WAT review reflecting the current microservices architecture. Archive the old answers and start fresh or update answers per pillar.
**Prevention:** Define review triggers in the workload RACI: annual review (calendar), after major architectural change (tech lead decision), after significant production incident (post-mortem step), or before a new compliance audit.

**Mode 3: Review identifies critical risk but no owner assigned**
**Symptom:** WAT review found a High Risk in Reliability: "No DR strategy defined." The risk has been in the report for 6 months. No one owns it.
**Root Cause:** Findings were shared in a document but not assigned to an individual with a deadline. Collective ownership = no ownership.
**Diagnostic:**

```bash
# Export all high-risk findings with questions
aws wellarchitected list-answers \
  --workload-id <workload-id> \
  --lens-alias wellarchitected \
  --risk HIGH \
  --query \
    'AnswerSummaries[*].[QuestionTitle,PillarId,Risk]'
```

**Fix:** For each High Risk finding, create a Jira epic with a named owner, an explicit SLA for first review (2 weeks), and an improvement timeline. Track in engineering OKRs.
**Prevention:** Automate ticket creation from WAT findings using EventBridge + Lambda + Jira API integration. Set a policy: no High Risk finding exists unassigned for more than 5 business days.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Cloud — AWS (category) — understanding the AWS service landscape is prerequisite to meaningfully answering Well-Architected questions about specific services.
- Architecture Review — understanding how to evaluate and communicate architectural trade-offs prepares for the facilitated review format.
- AWS core services — the review questions reference EC2, RDS, Lambda, CloudWatch, IAM, VPC; familiarity with these services is required to answer questions meaningfully.

**Builds On This (learn these next):**

- AWS Cost Tagging Strategy — the Cost Optimisation pillar outcome; implement tagging as a direct result of COST findings.
- AWS Control Tower — the Security and Operational Excellence pillar outcomes; multi-account governance is a common improvement action.
- SRE — Reliability pillar findings align with SRE practices (SLOs, error budgets, chaos engineering); SRE knowledge deepens reliability improvements.

**Alternatives / Comparisons:**

- AWS Trusted Advisor — automated, continuous AWS checks for cost, security, performance, and reliability. Lighter-weight and always-running vs a periodic facilitated review.
- Google Cloud Architecture Framework — Google's equivalent; same six-pillar structure with GCP-specific guidance. Shows the pattern is industry-wide, not AWS-proprietary.
- Microsoft Azure Well-Architected Framework — Microsoft's equivalent; identical structure (reliability, security, cost, performance, operational excellence). The five-pillar Azure model omits Sustainability as a separate pillar.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Six-pillar framework for evaluating|
|                  | AWS architecture risks and trade-offs|
| PROBLEM IT SOLVES| Unknown architectural risks become |
|                  | production incidents; tech debt is  |
|                  | invisible until it's expensive      |
| KEY INSIGHT      | Known + accepted risk is safe;     |
|                  | unknown risk is dangerous           |
| USE WHEN         | Before launch, annually, after major|
|                  | architectural change, pre-audit     |
| AVOID WHEN       | As a pure checkbox for compliance  |
|                  | without genuine follow-through      |
| TRADE-OFF        | 1-3 day review investment vs       |
|                  | finding risks before they find you  |
| ONE-LINER        | wellarchitected:GetLensReview      |
| NEXT EXPLORE     | Trusted Advisor, WAT Lenses, SRE   |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** The Well-Architected Framework's six pillars are interdependent — optimising for cost (smaller instances, single-AZ) directly degrades reliability (higher MTTR, lower availability). When a business owner pushes for cost optimisation that conflicts with reliability requirements, what structured process — rooted in the Well-Architected Framework — do you use to make the trade-off decision explicit, documented, and owned by the right stakeholder?

2. **(First Principles)** The framework explicitly allows teams to accept High Risk findings with documented rationale. A critic argues this creates an escape hatch that makes the review meaningless — teams just accept everything rather than fixing it. Defend the "documented risk acceptance" design choice: what is the security and governance benefit of explicitly documenting an accepted risk, compared to a framework that mandates remediation of all findings?

3. **(Scale)** An AWS Partner conducts Well-Architected Reviews for their customers. After 50 reviews across different workloads, they identify a pattern: 90% of workloads have the same 5 High Risk findings (no MFA on root, public S3 buckets, no CloudTrail in all regions, no backup policy, single-AZ databases). What automated preventive controls — at the AWS account or organisation level — would eliminate these findings before they appear in a review, and why haven't most organisations implemented them already?
