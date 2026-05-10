---
version: 2
layout: default
title: "Terraform Testing (Terratest)"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 72
permalink: /ci-cd/terraform-testing-terratest/
id: CCD-074
category: CI/CD
difficulty: ★★★
depends_on: Terraform Overview, Testing, Go (language)
used_by: CI-CD
related: Terraform Plan  Apply  Destroy, Testing, Kitchen-Terraform
tags:
  - cicd
  - devops
  - advanced
  - testing
---

# CCD-073 - Terraform Testing (Terratest)

⚡ **TL;DR -** Terratest is a Go testing framework for Terraform that deploys real infrastructure in CI, validates it behaves correctly, and destroys it - providing true integration tests for IaC.

| Field | Value |
|---|---|
| **Depends on** | Terraform Overview, Testing, Go (language) |
| **Used by** | CI-CD |
| **Related** | Terraform Plan  Apply  Destroy, Testing, Kitchen-Terraform |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your Terraform module creates a VPC, subnets, NAT gateway, and security groups. The module passes `terraform validate` and `terraform plan`. You publish `v1.0.0`. A team uses it. The NAT gateway route table association has a misconfiguration - instances can't reach the internet. The bug is only discovered after deployment to production.

**THE BREAKING POINT:** `terraform validate` checks syntax. `terraform plan` shows what will be created. Neither validates that the created infrastructure actually *works*. A VPC with a wrong route table is syntactically valid and plans cleanly.

**THE INVENTION MOMENT:** Terratest deploys real infrastructure to a test AWS account, runs assertions against it (can instances reach the internet? does the endpoint return 200?), then destroys it. The module can't be published until it passes real-world behavioral tests.

---

### 📘 Textbook Definition

**Terratest** is an open-source Go library (by Gruntwork) for writing automated tests for Terraform, Packer, Docker, Kubernetes, and other infrastructure code. Terratest tests use Go's standard `testing` package and call Terraform (`terraform.InitAndApply`), then validate infrastructure behavior (HTTP requests, SSH commands, AWS API assertions, DNS resolution), then destroy the infrastructure (`terraform.Destroy`). Tests are organized into unit, integration, and end-to-end tiers by cost and scope.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Terratest deploys real cloud infrastructure, runs Go tests against it, then destroys it - automated integration testing for IaC.

> Terratest is like a staging deploy that runs automatically, checks that everything works with real traffic, and then cleans up - but for infrastructure modules instead of applications.

**One insight:** Terratest tests are expensive (they spin up real AWS resources). Their value is proportional to how critical the module is. A foundational VPC module used by 20 teams is worth a 5-minute integration test. A one-off resource configuration is not.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Terratest tests deploy *real* infrastructure in *real* cloud environments.
2. Tests must clean up after themselves - `defer terraform.Destroy(t, terraformOptions)` is non-negotiable.
3. Tests should be idempotent - running twice should produce the same result.
4. Test execution time directly correlates to cost; short-lived resources minimize cost.

**DERIVED DESIGN:** Terratest wraps the Terraform CLI, captures output, and provides helper functions for common assertions (HTTP endpoint returns 200, port is accessible, AWS resource has expected tags, DNS resolves). Tests use Go's `testing.T` for assertion and failure reporting.

**THE TRADE-OFFS:**
**Gain:** True behavioral validation; catch bugs that `validate`/`plan` miss; confidence to publish modules.
**Cost:** Real AWS costs (infrastructure created per test run); slow (5–30 minutes per test); requires a dedicated test AWS account; Go knowledge required.

---

### 🧪 Thought Experiment

**SETUP:** Your `terraform-aws-alb` module creates an ALB, target groups, and listener rules. Unit tests (`terraform validate`) pass. Plan looks correct.

**WHAT HAPPENS WITHOUT TERRATEST:** You publish `v1.0.0`. A consuming team deploys to production. The ALB's health check path was set to `/health` but the module's default is `/`. The targets are unhealthy. The ALB never sends traffic. The issue would have been caught in 5 minutes by an integration test that makes an HTTP request to the ALB.

**WHAT HAPPENS WITH TERRATEST:** Your test deploys the ALB module to a test account, makes an HTTP request to `http://<alb-dns>/health`, asserts status 200, then destroys. The misconfigured health check path fails the test before v1.0.0 is tagged. The bug never reaches a consuming team.

**THE INSIGHT:** Infrastructure tests validate *behavior*, not just *structure*. `terraform plan` can tell you an ALB will be created; only a real request can tell you the ALB routes traffic correctly.

---

### 🧠 Mental Model / Analogy

> Terratest is like a smoke test for a physical product: before shipping the product (publishing the module), you assemble a real unit in the factory (deploy to test account), run it through its paces (make HTTP requests, check connectivity), confirm it works, then disassemble the unit (terraform destroy). Only then do you ship the product.

- Module repository → product factory
- Terratest deploy → assemble test unit
- Go assertions → quality control checks
- `defer terraform.Destroy` → disassemble test unit
- Module version tag → product shipping

Where this analogy breaks down: unlike physical products, Terratest can test every code change automatically - not just one unit per factory run. The "factory" (CI/CD pipeline) runs the full test on every PR.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Terratest is a testing tool that creates real cloud resources to check they work correctly, then deletes them. Like a test drive before publishing your Terraform module.

**Level 2 - How to use it (junior developer):** Write Go test files in a `test/` directory. Use `terraform.InitAndApply()` to deploy the module, `aws.GetPublicIpsOfTaggedInstances()` or `http.CheckStatusCode()` to validate, then `defer terraform.Destroy()` to clean up. Run with `go test -v -run TestVPCModule -timeout 30m`.

**Level 3 - How it works (mid-level engineer):** Terratest wraps the Terraform CLI binary. It runs `terraform init`, `terraform apply`, captures output, and runs your Go assertions against the deployed infrastructure. Helper packages (`aws`, `http-helper`, `ssh`) provide pre-built assertions. `defer` ensures destroy runs even if assertions fail.

**Level 4 - Why it was designed this way (senior/staff):** Terratest uses Go because Go's testing framework is mature, concurrency is built-in (parallel tests), and Gruntwork's team was already Go-native. The choice to run real infrastructure (rather than mock) is deliberate: mock-based testing can't catch IAM permission errors, subnet routing issues, or API rate limits that only appear in real deployments.

---

### ⚙️ How It Works (Mechanism)

**Test tiers:**
| Tier | Scope | Cost | Speed | Tools |
|---|---|---|---|---|
| **Unit** | HCL syntax + logic | Free | Seconds | `terraform validate`, `terraform test` |
| **Integration** | Real resources, isolated | $$ | 5–30 min | Terratest (one module) |
| **End-to-End** | Full system, real traffic | $$$ | 30–60 min | Terratest (multiple modules) |

**Test parallelism:**
Each Terratest test deploys to a unique namespace (random suffix on resource names) to avoid collisions. Multiple tests run in parallel using `t.Parallel()`. Each test's state is isolated.

**Retry and timing:**
Infrastructure takes time to become available. Terratest's `retry.DoWithRetry` retries assertions with configurable delays - essential for ALB health checks, DNS propagation, and certificate validation.

---

### 🔄 The Complete Picture - End-to-End Flow

**TERRATEST CI WORKFLOW:**
```
  PR opened: module change
           │
  CI: go test ./test/...
           │
  Test: terraform.InitAndApply    ← YOU ARE HERE
  (deploys to test AWS account)
           │
  defer terraform.Destroy
  (registered; runs on test exit)
           │
  Assertions:
  - HTTP endpoint returns 200
  - EC2 instance is reachable
  - S3 bucket has encryption
  - ALB target is healthy
           │
  All assertions pass → test PASS
  → terraform.Destroy runs (cleanup)
           │
  PR approved → module version tagged
  → Published to registry
```

**FAILURE PATH:** Test assertion fails (e.g., HTTP 503). `defer terraform.Destroy()` still runs - cleanup happens even on failure. CI reports the specific assertion that failed. Engineer investigates and fixes the module.

**WHAT CHANGES AT SCALE:** Test parallelism (`t.Parallel()`) runs many tests simultaneously. Test accounts are isolated from production. `--terragrunt-parallelism` limit prevents API rate limiting. Long tests (>30 min) are split into separate CI stages. Module test costs are tracked and optimized.

---

### 💻 Code Example

```go
// test/vpc_test.go
package test

import (
    "testing"
    "fmt"
    "time"

    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/gruntwork-io/terratest/modules/random"
    "github.com/gruntwork-io/terratest/modules/retry"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestVPCModule(t *testing.T) {
    t.Parallel()  // Run tests in parallel

    // Unique suffix to avoid naming collisions
    uniqueID := random.UniqueId()
    awsRegion := "us-east-1"

    // Configure Terraform options
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "environment": fmt.Sprintf("test-%s", uniqueID),
            "cidr_block":  "10.99.0.0/16",
            "aws_region":  awsRegion,
        },
        // Run in parallel with other tests
        MaxRetries:         3,
        TimeBetweenRetries: 10 * time.Second,
    }

    // ALWAYS destroy after test - even on failure
    defer terraform.Destroy(t, terraformOptions)

    // Deploy the module
    terraform.InitAndApply(t, terraformOptions)

    // --- ASSERTIONS ---

    // Test 1: VPC was created with correct CIDR
    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    require.NotEmpty(t, vpcID)

    vpc := aws.GetVpcById(t, vpcID, awsRegion)
    assert.Equal(t, "10.99.0.0/16", aws.GetCidrOfVpc(t, vpc))

    // Test 2: Private subnets exist
    subnetIDs := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
    assert.Equal(t, 2, len(subnetIDs))

    // Test 3: Flow logs enabled
    flowLogs := aws.GetVpcFlowLogs(t, vpcID, awsRegion)
    assert.True(t, len(flowLogs) > 0, "Flow logs should be enabled")

    // Test 4: NAT gateway accessible (idempotency)
    // Apply again; should show no changes
    exitCode := terraform.PlanExitCode(t, terraformOptions)
    assert.Equal(t, 0, exitCode, "Second plan should show no changes")
}

// Integration test: EC2 instance can reach internet via NAT
func TestNATGatewayConnectivity(t *testing.T) {
    t.Parallel()

    uniqueID := random.UniqueId()
    awsRegion := "us-east-1"

    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/with-nat",
        Vars: map[string]interface{}{
            "environment": fmt.Sprintf("test-nat-%s", uniqueID),
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    instanceID := terraform.Output(t, terraformOptions, "instance_id")

    // Test: instance can reach internet (via SSM run command)
    result := retry.DoWithRetry(t, "wait for internet connectivity",
        10, 30*time.Second,
        func() (string, error) {
            out, err := aws.RunCommandOnInstanceE(t,
                awsRegion, instanceID,
                "curl -s -o /dev/null -w '%{http_code}' https://api.ipify.org")
            if err != nil || out != "200" {
                return "", fmt.Errorf("expected 200, got: %s", out)
            }
            return out, nil
        },
    )

    assert.Equal(t, "200", result, "Instance should reach internet via NAT")
}
```

```bash
# Run all tests with 30-minute timeout
go test -v -timeout 30m ./test/...

# Run specific test
go test -v -run TestVPCModule -timeout 20m ./test/

# Run in parallel with multiple tests
go test -v -parallel 4 -timeout 60m ./test/...

# Run with verbose Terraform output
TF_LOG=INFO go test -v -run TestVPCModule -timeout 30m ./test/
```

---

### ⚖️ Comparison Table

| Tool | Test Level | Language | Real Infra | Cost | Speed |
|---|---|---|---|---|---|
| **Terratest** | Integration/E2E | Go | ✅ Real | $$$ | Slow (mins) |
| **terraform test** | Unit | HCL | Mock or real | $ | Fast (secs) |
| **Kitchen-Terraform** | Integration | Ruby | ✅ Real | $$$ | Slow |
| **Checkov** | Static analysis | Python | ❌ | Free | Fast |
| **tfsec** | Static analysis | Go | ❌ | Free | Fast |
| **Conftest/OPA** | Policy | Rego | ❌ | Free | Fast |
| **Best for** | Behavioral testing | Plan validation | Security scanning | Compliance |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Terratest tests Terraform syntax" | `terraform validate` tests syntax. Terratest deploys real infrastructure and tests behavior. They're complementary. |
| "`defer terraform.Destroy` always cleans up" | If the CI runner is killed (OOM, timeout) before defer runs, resources leak. Implement a nightly cleanup job for test accounts. |
| "Terratest is only for modules" | Terratest can test any Terraform configuration, including root modules and end-to-end system deployments. |
| "Terratest tests are fast" | Integration tests spin up real infrastructure. VPC tests take 5–10 minutes; EKS cluster tests take 20–30 minutes. |
| "One test per module is enough" | Test the happy path (default config), edge cases (max/min values), and idempotency (second plan shows no changes) at minimum. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Test Account Resource Leakage**
- **Symptom:** Test AWS account accumulates orphaned resources; costs spike; plan failures due to quota limits
- **Root Cause:** Test crashed before `defer terraform.Destroy` ran; CI runner was OOM-killed
- **Diagnostic:**
```bash
# List all test-tagged resources in test account
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=test
```
- **Fix:** Implement `aws-nuke` or a dedicated cleanup Lambda that destroys resources older than 2 hours with test prefix tags.
- **Prevention:** Set CI job resource quotas; use AWS Budgets alerts on test accounts; implement automatic cleanup.

**Mode 2: Test Naming Collision**
- **Symptom:** `Error: S3 bucket already exists` when running tests in parallel
- **Root Cause:** Tests use deterministic names instead of random unique IDs
- **Diagnostic:** Check test code for hardcoded resource names.
- **Fix - BAD:**
```go
// BAD: hardcoded name
bucketName := "test-bucket"
```
- **Fix - GOOD:**
```go
// GOOD: unique per test run
bucketName := fmt.Sprintf("test-bucket-%s", random.UniqueId())
```
- **Prevention:** All test resource names must include `random.UniqueId()`. Code review checklist item.

**Mode 3: Flaky Assertions Due to Timing**
- **Symptom:** Test passes locally but fails in CI; ALB health checks occasionally fail
- **Root Cause:** Assertions run before resources are fully available (ALB not yet healthy, DNS not propagated)
- **Diagnostic:**
```go
// Check: are you retrying with sufficient backoff?
http_helper.HttpGetWithRetryWithCustomValidation(
  t, url, nil, 30, 10*time.Second,
  func(statusCode int, body string) bool {
    return statusCode == 200
  },
)
```
- **Fix:** Wrap all timing-sensitive assertions in `retry.DoWithRetry` with appropriate max retries and sleep duration.
- **Prevention:** Add 20–30% buffer to all timing-sensitive retries; test in CI with CI-representative network conditions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Overview, Testing, Go (language), Terraform Plan / Apply / Destroy

**Builds On This (learn these next):** CI-CD, Terraform Reusable Module Pattern

**Alternatives / Comparisons:** Kitchen-Terraform (Ruby), `terraform test` (built-in, HCL), Checkov (static analysis), tfsec

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Go framework for real-infra testing  │
│ PROBLEM       │ validate/plan don't test behavior    │
│ KEY INSIGHT   │ defer terraform.Destroy = always     │
│               │ clean up; use random.UniqueId()      │
│ USE WHEN      │ Shared modules; critical infra       │
│ AVOID WHEN    │ One-off configs; cost-constrained    │
│ TRADE-OFF     │ Behavioral confidence vs cost/speed  │
│ ONE-LINER     │ go test -v -timeout 30m ./test/...   │
│ NEXT EXPLORE  │ terraform test, CI-CD, tfsec         │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A Terratest integration test deploys a full VPC, EKS cluster, and application load balancer. The test passes but takes 45 minutes in CI. PR wait times are unacceptable. What test architecture (test tiers, parallelism, mock-first approach) would you design to reduce CI feedback time to under 10 minutes while preserving behavioral confidence?

2. **(Production)** A Terratest test deploys an RDS instance with a random suffix in the test account. The test fails due to an IAM permission error - but the RDS instance was already created before the failure. The `defer terraform.Destroy()` doesn't run because the CI runner was OOM-killed. The RDS instance runs for 3 days, accumulating cost. Design the complete cleanup strategy for a team with 200 Terratest tests running across 5 CI workers.

3. **(Design Trade-off)** HashiCorp's native `terraform test` (TF 1.6+) is built into Terraform and supports both mock providers (free, fast) and real providers (costly, slow). Terratest requires Go knowledge and real infrastructure. For a platform team maintaining 30 Terraform modules, what factors determine which testing approach (or combination) to adopt, and how does the team's Go expertise affect this decision?
