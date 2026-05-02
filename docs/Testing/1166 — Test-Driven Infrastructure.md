---
layout: default
title: "Test-Driven Infrastructure"
parent: "Testing"
nav_order: 1166
permalink: /testing/test-driven-infrastructure/
number: "1166"
category: Testing
difficulty: ★★★
depends_on: TDD, Infrastructure as Code, Terraform, Cloud
used_by: DevOps Engineers, Platform Engineers, SREs
related: TDD, CI-CD, Terraform, Terratest, InSpec, Test Environments
tags:
  - testing
  - infrastructure
  - iac
  - devops
  - tdd
---

# 1166 — Test-Driven Infrastructure

⚡ TL;DR — Test-Driven Infrastructure (TDI) applies TDD principles to infrastructure code: write tests for infrastructure behavior first, then write the Terraform/Ansible/CloudFormation code to make them pass — ensuring infrastructure is both correct and continuously validated.

| #1166           | Category: Testing                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | TDD, Infrastructure as Code, Terraform, Cloud               |                 |
| **Used by:**    | DevOps Engineers, Platform Engineers, SREs                  |                 |
| **Related:**    | TDD, CI-CD, Terraform, Terratest, InSpec, Test Environments |                 |

---

### 🔥 The Problem This Solves

INFRASTRUCTURE HAS NO TESTS:
Application code has unit tests, integration tests, CI pipelines. Infrastructure code (Terraform, Ansible, shell scripts)? Mostly: "apply it and hope." A Terraform change that opens security group 0.0.0.0/0 to port 22 (SSH to everyone) gets merged because nobody tested the security posture. An Ansible playbook that was working a year ago no longer works because a package version changed. Infrastructure drift: actual cloud state diverges from IaC definition — no tests to detect it.

---

### 📘 Textbook Definition

**Test-Driven Infrastructure (TDI)** is the practice of applying automated testing to infrastructure code, potentially in a TDD style. Infrastructure tests verify: (1) **unit tests** — static analysis of IaC files (security misconfigurations, naming conventions); (2) **integration tests** — deploy real infrastructure in a test environment and verify its properties (is the S3 bucket private? Is the RDS instance in a private subnet? Does the load balancer respond?); (3) **compliance tests** — verify infrastructure meets security and compliance policies (no public RDS, all EBS volumes encrypted, no SSH open to 0.0.0.0/0). Tools include: **Terratest** (Go, integration tests for Terraform), **InSpec/Chef** (compliance testing), **tfsec/Checkov** (static analysis), **AWS Config Rules** (continuous compliance).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Test infrastructure the same way you test application code — unit, integration, compliance tests.

**One analogy:**

> Testing infrastructure is like **home inspection**: before a building is occupied, inspectors verify: electrical wiring is correct, plumbing holds pressure, fire exits are accessible, load-bearing walls are intact. Without inspection, the building might look fine but fail under load. Infrastructure testing is the automated inspector — running after every IaC change.

---

### 🔩 First Principles Explanation

TESTING PYRAMID FOR INFRASTRUCTURE:

```
          /\
         /  \   COMPLIANCE TESTS (InSpec, AWS Config)
        /    \  → "Are all S3 buckets encrypted?"
       /------\  → Slow, runs against real cloud
      /        \ INTEGRATION TESTS (Terratest)
     /          \ → Deploy real infra, verify properties
    /            \ → Minutes to hours per test
   /--------------\ UNIT/STATIC TESTS (tfsec, Checkov, terraform validate)
  /                \ → Security misconfiguration detection
 /                  \ → Fast, no cloud required, runs in seconds
/____________________\

UNIT-LEVEL (static analysis — no cloud):
  terraform validate        → syntax check
  terraform fmt --check     → formatting check
  tfsec .                   → security misconfiguration scan
  checkov -d .              → broad misconfiguration scan

  Example tfsec finding:
  CRITICAL: Security group allows unrestricted access to SSH
  → aws_security_group.web with ingress 0.0.0.0/0 port 22

INTEGRATION-LEVEL (Terratest — real cloud):
  func TestS3BucketIsPrivate(t *testing.T) {
    opts := &terraform.Options{TerraformDir: "../modules/s3"}
    defer terraform.Destroy(t, opts)           // cleanup always runs
    terraform.InitAndApply(t, opts)            // deploy real S3 bucket

    bucketName := terraform.Output(t, opts, "bucket_name")

    // Verify bucket is private (not public)
    s3Client := aws.NewS3Client(t, "us-east-1")
    publicAccessBlock := aws.GetS3BucketPublicAccessBlock(t, s3Client, bucketName)
    assert.True(t, *publicAccessBlock.BlockPublicAcls)
    assert.True(t, *publicAccessBlock.BlockPublicPolicy)
  }

COMPLIANCE-LEVEL (InSpec):
  # Check all EC2 instances are in private subnets
  describe aws_ec2_instances do
    its('instance_ids') { should_not be_empty }
  end

  aws_ec2_instances.instance_ids.each do |instance_id|
    describe aws_ec2_instance(instance_id) do
      it { should_not have_public_ip_address }
    end
  end
```

TERRAFORM UNIT TESTS (terraform test - native, v1.6+):

```hcl
# tests/s3_bucket.tftest.hcl
run "s3_bucket_is_private" {
  command = plan  # or apply

  assert {
    condition     = aws_s3_bucket_public_access_block.this.block_public_acls == true
    error_message = "S3 bucket must block public ACLs"
  }

  assert {
    condition     = aws_s3_bucket_server_side_encryption_configuration.this != null
    error_message = "S3 bucket must be encrypted"
  }
}
```

---

### 🧪 Thought Experiment

THE SECURITY GROUP DRIFT:

```
Week 1: Terraform code correctly restricts SSH to VPN CIDR (10.0.0.0/8)
Week 2: Ops engineer manually adds 0.0.0.0/0 SSH rule for "temporary debugging"
Week 3: "Temporary" rule never removed. Terraform state drifts from real infra.
Week 6: Security audit finds: SSH open to internet on 50 production servers.
         Audit failed: GDPR violation + potential SOC 2 finding.

With TDI (InSpec daily compliance scan):
  Week 2, Day 2: Compliance scan runs
  → FAIL: "EC2 security groups: SSH open to 0.0.0.0/0 detected"
  → Alert: Slack/PagerDuty notification
  → Immediate investigation + remediation
  → Security incident prevented
```

---

### 🧠 Mental Model / Analogy

> Infrastructure tests are **circuit breakers for deployment pipelines**: when infrastructure code changes, tests run. If a security misconfiguration is introduced, the circuit breaks (pipeline fails), preventing bad infrastructure from reaching production. Compliance tests are **continuous monitoring** — running daily to catch manual drift before it becomes a security incident.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Run `terraform validate` + `tfsec` on every PR. They catch syntax errors and obvious security misconfigurations in seconds without touching the cloud.

**Level 2:** Add Terratest integration tests: deploy actual infrastructure in a test AWS account, verify properties (bucket is private, VPC CIDR is correct, RDS is in private subnet), then destroy. These run as part of CI but slower (5-30 minutes).

**Level 3:** Compliance-as-code with InSpec: write human-readable compliance controls (`it { should_not have_public_ip_address }`). Run daily against all environments. Alert on failures. This catches manual drift that IaC can't prevent. Integrate with `terraform plan` output testing: write tests against the planned changes (not the applied state) to validate intent before apply.

**Level 4:** Full TDI workflow: write InSpec/Terratest compliance test first → it fails (infrastructure doesn't meet requirement) → write Terraform code to satisfy it → test passes. Treat every security requirement and architecture constraint as a test. Infrastructure ADRs implemented as compliance tests — the test IS the documentation of intent. Policy-as-Code at enterprise scale: Open Policy Agent (OPA) with Terraform → Conftest validates Terraform plans against Rego policies before any apply.

---

### 💻 Code Example

```hcl
# Terraform — S3 module
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

```go
// Terratest — Go integration test
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/stretchr/testify/assert"
)

func TestS3BucketSecurity(t *testing.T) {
    t.Parallel()

    opts := &terraform.Options{
        TerraformDir: "../modules/s3",
        Vars: map[string]interface{}{
            "bucket_name": "test-bucket-" + strings.ToLower(random.UniqueId()),
        },
    }

    defer terraform.Destroy(t, opts)  // always cleanup
    terraform.InitAndApply(t, opts)

    bucketName := terraform.Output(t, opts, "bucket_name")

    // Verify public access is blocked
    actualPublicAccessBlock := aws.GetS3BucketPublicAccessBlock(t, "us-east-1", bucketName)
    assert.True(t, aws.BoolValue(actualPublicAccessBlock.BlockPublicAcls))
    assert.True(t, aws.BoolValue(actualPublicAccessBlock.BlockPublicPolicy))
}
```

```bash
# Static analysis in CI pipeline
- name: Static security analysis
  run: |
    tfsec . --format=json --out=tfsec-results.json
    checkov -d . --framework=terraform --output=junitxml > checkov-results.xml
    terraform validate
```

---

### ⚖️ Comparison Table

| Tool                     | Level            | Cloud Access      | Speed           | Coverage          |
| ------------------------ | ---------------- | ----------------- | --------------- | ----------------- |
| terraform validate       | Unit             | No                | Seconds         | Syntax only       |
| tfsec / Checkov          | Unit             | No                | Seconds         | Security patterns |
| Terraform test (.tftest) | Unit/Integration | Optional          | Seconds-minutes | Custom assertions |
| Terratest                | Integration      | Yes (real deploy) | Minutes-hours   | Full behavior     |
| InSpec                   | Compliance       | Yes (live infra)  | Minutes         | Ongoing drift     |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                          |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| "Terraform plan shows what will change — no tests needed" | Plan shows intent but not correctness; tests verify properties of actual deployed infrastructure                                 |
| "Static analysis is enough"                               | tfsec catches known patterns; Terratest verifies actual cloud behavior (permissions, network connectivity, service availability) |
| "Compliance tests only for regulated industries"          | Security hygiene (no SSH to 0.0.0.0/0, all buckets private) applies everywhere                                                   |

---

### 🚨 Failure Modes & Diagnosis

**1. Terratest Doesn't Destroy on Failure**
Cause: Test fails before `defer terraform.Destroy()` runs — or panic occurs.
**Fix:** Always use `defer` for destroy. Use Terratest's `defer terraform.Destroy` immediately after `InitAndApply`. Implement cloud resource janitor (delete all test-tagged resources older than 2 hours).

**2. Integration Tests Too Slow for PR Pipeline**
Cause: Full Terratest suite deploys real infrastructure (VPC, RDS, EKS) → 30+ minutes.
**Fix:** Fast path in PR: unit-only (tfsec + validate); Terratest runs on merge to main only. Cache Terraform providers between runs.

---

### 🔗 Related Keywords

- **Prerequisites:** TDD, Infrastructure as Code, Terraform
- **Related:** Terratest, InSpec, tfsec, Checkov, Open Policy Agent, Conftest, AWS Config, GitOps

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Automated tests for infrastructure code  │
├──────────────┼───────────────────────────────────────────┤
│ LAYERS       │ Static (tfsec) → Integration (Terratest) │
│              │ → Compliance (InSpec)                    │
├──────────────┼───────────────────────────────────────────┤
│ FAST CHECK   │ tfsec + checkov + terraform validate     │
│              │ → runs in seconds, no cloud needed       │
├──────────────┼───────────────────────────────────────────┤
│ DEEP CHECK   │ Terratest: deploy real infra, verify,    │
│              │ destroy — catches real behavioral issues  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Infrastructure has bugs too — test it   │
│              │  like application code"                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Terratest deploys real cloud infrastructure (AWS, GCP, Azure) in tests. Describe the cost management strategy: (1) test account isolation — Terratest tests should run in a dedicated test AWS account (not production), using AWS Organizations with SCPs that prevent expensive resource types (GPU instances, large RDS multi-AZ) from being created, (2) resource tagging — every Terratest resource tagged with `test=true`, `created_by=terratest`, `created_at=timestamp`, enabling the cloud janitor to automatically delete resources older than 2 hours, (3) test duration optimization — parallelize tests with `t.Parallel()`, cache Terraform provider downloads between runs, and use VPC with pre-created dependencies (reduce per-test VPC creation overhead), and (4) cost estimation — using `infracost` CLI to estimate the cost of infrastructure before deploying it (run in CI on `terraform plan` output).

**Q2.** Open Policy Agent (OPA) with Conftest enables Policy-as-Code for Terraform. Describe: (1) how Conftest reads `terraform plan -out=plan.tfplan; terraform show -json plan.tfplan` output and evaluates Rego policies against the planned changes (not the current state), (2) writing a Rego policy that prevents any security group rule that allows `0.0.0.0/0` or `::/0` ingress on any port, (3) how this integrates into a CI pipeline (terraform plan → json → conftest verify → proceed or fail), (4) the advantage over tfsec (custom business policies: "all resources must have cost-center tags", "RDS instances must use approved instance families") that generic tools don't know about, and (5) governance at enterprise scale: policies stored in a central git repo, all team Terraform pipelines pull and enforce the same policies.
