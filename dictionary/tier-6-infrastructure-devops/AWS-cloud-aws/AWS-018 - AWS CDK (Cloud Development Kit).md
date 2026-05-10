---
version: 2
layout: default
title: "AWS CDK (Cloud Development Kit)"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /cloud-aws/aws-cdk/
id: AWS-018
category: Cloud - AWS
difficulty: ★★★
depends_on: AWS CloudFormation, AWS, Infrastructure as Code
used_by: Cloud - AWS, CI-CD
related: AWS CloudFormation, Terraform Overview, Pulumi
tags:
  - aws
  - cloud
  - advanced
  - devops
  - cicd
---

# AWS-018 - AWS CDK (Cloud Development Kit)

⚡ **TL;DR -** AWS CDK lets you define cloud infrastructure using real programming languages (TypeScript, Python, Java) that compile down to CloudFormation templates, with reusable component abstractions called constructs.

|                |                                                 |
| -------------- | ----------------------------------------------- |
| **Depends on** | AWS CloudFormation, AWS, Infrastructure as Code |
| **Used by**    | Cloud - AWS, CI-CD                              |
| **Related**    | AWS CloudFormation, Terraform Overview, Pulumi  |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Defining AWS infrastructure means writing hundreds of lines of JSON/YAML CloudFormation. Creating a load-balanced ECS service requires 8+ CloudFormation resources - ALB, Target Group, Listener, ECS Cluster, Task Definition, Service, IAM roles, Security Groups - each with dozens of properties cross-referencing each other. A mistake in any reference breaks the entire deployment.

**THE BREAKING POINT:** Infrastructure logic cannot be expressed in YAML. You cannot write a `for` loop to create 10 S3 buckets with incrementing names, or an `if` statement to enable encryption only in production. You copy-paste CloudFormation blocks and introduce drift between environments.

**THE INVENTION MOMENT:** AWS built CDK to answer: what if infrastructure definition used the same programming languages, abstractions, and tooling that developers already know - loops, conditionals, functions, unit tests, and package managers?

---

### 📘 Textbook Definition

**AWS CDK (Cloud Development Kit)** is an open-source software development framework for defining cloud infrastructure as code using general-purpose programming languages - TypeScript, JavaScript, Python, Java, C#, and Go. CDK synthesises infrastructure definitions into AWS CloudFormation templates, which are deployed to AWS. CDK introduces the concept of **constructs** - reusable, composable infrastructure components - at three levels of abstraction: L1 (direct CloudFormation mapping), L2 (opinionated defaults), and L3 (complete patterns).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Write AWS infrastructure in TypeScript or Python; CDK converts it to CloudFormation and deploys it.

**One analogy:**

> CDK is like TypeScript being compiled to JavaScript. You write in a high-level language with abstractions, type safety, and IDE support; the compiler (CDK synth) produces the low-level format (CloudFormation JSON) that the runtime (AWS) actually executes.

**One insight:** CDK is a compiler for infrastructure - it produces CloudFormation, but you never have to write or maintain CloudFormation directly.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. CDK apps synthesise to CloudFormation templates - CDK is a layer above CloudFormation, not a replacement.
2. Constructs are the unit of reuse - composable, testable, shareable infrastructure components.
3. The three-level hierarchy (L1/L2/L3) maps directly to abstraction needs: raw parity, sensible defaults, full patterns.
4. `cdk synth` is pure - it produces deterministic output without calling AWS APIs.

**DERIVED DESIGN:** A CDK App contains Stacks, which contain Constructs. At synthesis time, CDK traverses the construct tree and emits a CloudFormation template per Stack. `cdk deploy` then calls the CloudFormation API to create or update the stack. Outputs from one stack can be imported by another (cross-stack references), enabling modular infrastructure composition.

**THE TRADE-OFFS:**
**Gain:** Type safety on infrastructure, loops/conditionals, unit testing, IDE autocompletion, construct reuse across teams, direct CloudFormation escape hatch.
**Cost:** CDK abstractions can hide what CloudFormation is actually being created; debugging requires understanding the generated template; CDK version upgrades can change generated CloudFormation causing unexpected diffs.

---

### 🧪 Thought Experiment

**SETUP:** You need to create the same VPC + ECS service + RDS cluster architecture in three environments: dev, staging, and production. The only difference is instance sizes and whether Multi-AZ is enabled.

**WHAT HAPPENS WITHOUT CDK:** You copy the CloudFormation template three times. Environment differences require three different YAML files. A security group rule change must be applied to all three manually. Over 6 months, the files drift from each other in subtle ways.

**WHAT HAPPENS WITH CDK:** You define `class AppStack extends Stack` with `instanceSize` and `multiAz` parameters. Instantiate it three times: `new AppStack(app, 'dev', {instanceSize: 't3.small', multiAz: false})`. A security group rule change is made once in the class and synthesises correctly to all three environments. Unit tests verify the production stack has Multi-AZ enabled.

**THE INSIGHT:** CDK makes infrastructure refactorable. You can apply software engineering practices - abstraction, composition, testing, and DRY - to infrastructure definition.

---

### 🧠 Mental Model / Analogy

> CDK constructs are like LEGO bricks at different scales. L1 constructs are individual LEGO studs - primitive shapes matching CloudFormation resources exactly. L2 constructs are pre-built LEGO sub-assemblies (a wheel-and-axle unit) with sensible defaults. L3 constructs are complete LEGO kits (a car chassis with wheels, body, and engine) - a full architectural pattern in one component.

- **L1 (CfnBucket)** = a raw CloudFormation S3::Bucket resource, every property explicit
- **L2 (s3.Bucket)** = S3 bucket with intelligent defaults (versioning options, encryption helper methods)
- **L3 (patterns.ApplicationLoadBalancedFargateService)** = full load-balanced ECS service in one construct
- **CDK App** = the completed LEGO model assembled from constructs

Where this analogy breaks down: LEGO bricks snap together physically; CDK constructs compose through parent-child relationships in a tree that determines CloudFormation resource naming and IAM permission grants.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
CDK is a tool that lets developers write cloud infrastructure setup using Python or TypeScript code instead of YAML config files - the same way they write application code, with autocomplete and error checking.

**Level 2 - How to use it (junior developer):**
Run `cdk init app --language typescript`. Define resources in a `Stack` class. Run `cdk synth` to see the generated CloudFormation. Run `cdk deploy` to create resources in AWS. Use `cdk diff` before deploying to see what will change.

**Level 3 - How it works (mid-level engineer):**
CDK apps are Node.js (or Python/JVM) programs that instantiate a construct tree. At `cdk synth`, the tree is traversed to emit CloudFormation templates into the `cdk.out/` directory. Assets (Lambda code, Docker images) are packaged and uploaded to a CDK bootstrap S3 bucket and ECR repo. `cdk deploy` calls `cloudformation:CreateChangeSet` and then `cloudformation:ExecuteChangeSet`. Cross-stack references use CloudFormation exports/imports under the hood.

**Level 4 - Why it was designed this way (senior/staff):**
The L1/L2/L3 hierarchy solves a core extensibility problem in infrastructure frameworks: you cannot anticipate every use case with high-level abstractions, but forcing users to drop to raw CloudFormation breaks the abstraction entirely. CDK's "escape hatch" pattern - every L2/L3 construct exposes the underlying `cfnResource` property - means you never have to abandon the CDK construct hierarchy to access a CloudFormation property that CDK hasn't surfaced. This is the same design pattern as `useRef` in React: structured access to the underlying primitive when abstractions are insufficient.

---

### ⚙️ How It Works (Mechanism)

1. **App → Stack → Construct tree** - CDK App instantiates Stacks; Stacks contain Construct instances; each Construct may contain nested Constructs.
2. **Synthesis (`cdk synth`)** - CDK calls `prepare()` on each node (resolving tokens/lazy values), then `synthesize()` to emit CloudFormation JSON to `cdk.out/`.
3. **Assets** - Lambda function code, Dockerfile builds, and S3 assets are identified, fingerprinted, and staged in `cdk.out/`. `cdk deploy` uploads them to the CDK bootstrap bucket before creating the stack.
4. **Bootstrap** - CDK requires a one-time bootstrap per account/region (`cdk bootstrap`) that creates an S3 bucket and ECR repo for assets and an IAM role for deployment.
5. **Deploy** - CDK calls CloudFormation `CreateChangeSet` → `DescribeChangeSet` → `ExecuteChangeSet`. Rolls back automatically on failure.
6. **CDK Pipelines** - a CDK construct for self-mutating CI/CD pipelines. The pipeline itself is defined in CDK, and it automatically updates itself on code change before deploying application stacks.
7. **Aspects** - cross-cutting concerns (e.g., "apply tag to every resource in this stack") applied via the `Aspects` API without modifying each construct individually.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Developer writes TypeScript CDK code
     |
     | cdk synth
     v
CDK App executes (Node.js process)
  [construct tree built]
  [tokens resolved]          ← YOU ARE HERE
  [assets fingerprinted]
     |
     | cdk.out/ directory
     | - MyStack.template.json
     | - asset.abc123/ (Lambda code)
     v
cdk deploy
  [assets uploaded to bootstrap S3/ECR]
  [CloudFormation CreateChangeSet]
  [CloudFormation ExecuteChangeSet]
     |
     v
AWS Resources provisioned/updated
```

**FAILURE PATH:**

- `cdk synth` fails → TypeScript compile error or invalid CDK construct usage; fix in code
- CloudFormation rollback → a resource failed to create; check CloudFormation events for root cause
- Bootstrap missing → `cdk deploy` fails with "Need to perform AWS calls for account"; run `cdk bootstrap` first

**WHAT CHANGES AT SCALE:**
With 50+ stacks, use CDK Pipelines for automated deployment. Organise stacks into Stages (logical groups). Use construct libraries (private npm packages) to share L2/L3 constructs across teams - the same way application teams share libraries.

---

### 💻 Code Example

**BAD - L1 construct (verbose, no defaults):**

```typescript
// L1: every property must be explicit
import { CfnBucket } from "aws-cdk-lib/aws-s3";

new CfnBucket(this, "RawBucket", {
  bucketEncryption: {
    serverSideEncryptionConfiguration: [
      {
        serverSideEncryptionByDefault: {
          sseAlgorithm: "aws:kms",
        },
      },
    ],
  },
  versioningConfiguration: {
    status: "Enabled",
  },
  publicAccessBlockConfiguration: {
    blockPublicAcls: true,
    blockPublicPolicy: true,
    ignorePublicAcls: true,
    restrictPublicBuckets: true,
  },
});
```

**GOOD - L2 construct (opinionated, type-safe):**

```typescript
import * as s3 from "aws-cdk-lib/aws-s3";
import * as kms from "aws-cdk-lib/aws-kms";
import { RemovalPolicy } from "aws-cdk-lib";

const key = new kms.Key(this, "BucketKey", {
  enableKeyRotation: true,
});

const bucket = new s3.Bucket(this, "AppBucket", {
  encryption: s3.BucketEncryption.KMS,
  encryptionKey: key,
  versioned: true,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  removalPolicy: RemovalPolicy.RETAIN,
  enforceSSL: true,
});

// Escape hatch: access underlying CloudFormation
// resource to set a property CDK hasn't surfaced
const cfnBucket = bucket.node.defaultChild as s3.CfnBucket;
cfnBucket.addPropertyOverride("ObjectLockEnabled", true);
```

**L3 construct - full ECS Fargate service:**

```typescript
import * as patterns from "aws-cdk-lib/aws-ecs-patterns";
import * as ecs from "aws-cdk-lib/aws-ecs";

const service = new patterns.ApplicationLoadBalancedFargateService(
  this,
  "ApiService",
  {
    cluster: new ecs.Cluster(this, "Cluster", { vpc }),
    cpu: 512,
    memoryLimitMiB: 1024,
    desiredCount: 2,
    taskImageOptions: {
      image: ecs.ContainerImage.fromRegistry("nginx:latest"),
      containerPort: 80,
    },
    publicLoadBalancer: true,
  },
);
// One L3 construct creates: ALB, Target Group,
// Listener, ECS Cluster, Task Def, Service, IAM,
// Security Groups - ~15 CloudFormation resources
```

**CDK CLI workflow:**

```bash
# Bootstrap account/region (one-time)
cdk bootstrap aws://123456789/us-east-1

# Preview changes before deploy
cdk diff MyStack

# Deploy specific stack
cdk deploy MyStack --require-approval never

# Synthesise to CloudFormation (no deploy)
cdk synth MyStack

# Destroy a stack
cdk destroy MyStack

# Show all stacks in the app
cdk list

# Run CDK unit tests (Jest)
npm test
```

---

### ⚖️ Comparison Table

| Feature              | AWS CDK                | CloudFormation (raw)   | Terraform        | Pulumi            |
| -------------------- | ---------------------- | ---------------------- | ---------------- | ----------------- |
| **Language**         | TS/Python/Java/C#/Go   | YAML/JSON              | HCL              | TS/Python/Go/C#   |
| **Output format**    | CloudFormation         | CloudFormation         | Terraform state  | Pulumi state      |
| **AWS-specific**     | Yes                    | Yes                    | No (multi-cloud) | No (multi-cloud)  |
| **Type safety**      | Yes (TypeScript)       | No                     | Limited          | Yes               |
| **Unit testing**     | Yes (CDK assertions)   | No                     | `terraform test` | Yes               |
| **Reuse**            | Constructs (npm)       | Nested stacks, macros  | Modules          | ComponentResource |
| **Learning curve**   | Medium                 | Low (YAML)             | Medium (HCL)     | Low (TypeScript)  |
| **State management** | CloudFormation managed | CloudFormation managed | Self-managed     | Pulumi service    |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                       |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CDK replaces CloudFormation"               | CDK compiles to CloudFormation. CloudFormation is still the deployment engine. CDK stacks are CloudFormation stacks.                                                                          |
| "cdk deploy is instant"                     | CDK deploy creates a CloudFormation change set and executes it. Large stacks with many resources take the same time as equivalent CloudFormation deployments.                                 |
| "L3 constructs are always the right choice" | L3 constructs embed strong opinions. If your requirements differ (custom ALB listener rules, specific Fargate task placement), L2 constructs give more control with less boilerplate than L1. |
| "CDK is only for TypeScript"                | CDK supports TypeScript, JavaScript, Python, Java, C#, and Go with equivalent feature sets. TypeScript gets the best IDE experience but Python is widely used.                                |
| "cdk diff shows all changes"                | CDK diff shows CloudFormation logical changes, not all execution effects. Auto Scaling events, Lambda invocations, and side-effects of CloudFormation custom resources are not shown.         |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: CDK upgrade breaks generated CloudFormation**
**Symptom:** After `npm update aws-cdk-lib`, `cdk diff` shows unexpected resource replacements (e.g., Lambda function being deleted and recreated). No code change was made.
**Root Cause:** CDK version change altered how logical IDs, asset hashing, or CloudFormation resource names are generated.
**Diagnostic:**

```bash
# Compare synthesised output before and after update
cdk synth --output cdk.out.before
npm update aws-cdk-lib
cdk synth --output cdk.out.after
diff cdk.out.before/MyStack.template.json \
     cdk.out.after/MyStack.template.json
```

**Fix:** Use `overrideLogicalId` on the construct to pin the logical ID, preventing CDK from renaming resources on upgrade.
**Prevention:** Lock CDK versions with exact pinning in `package.json`. Test `cdk diff` in staging before upgrading production.

**Mode 2: Cross-stack reference circular dependency**
**Symptom:** `cdk synth` fails with "Circular dependency between stacks: StackA depends on StackB depends on StackA."
**Root Cause:** Stack A exports a value consumed by Stack B, and Stack B exports a value consumed by Stack A.
**Diagnostic:**

```bash
cdk synth 2>&1 | grep -i circular
# Review which stacks import from each other
cdk list --long
```

**Fix:** Break the cycle by extracting the shared resource into a third stack, or pass the value as a constructor parameter rather than a cross-stack reference.
**Prevention:** Design stack boundaries before coding. Shared resources (VPC, KMS keys) belong in a foundation stack with no application dependencies.

**Mode 3: Stack rollback leaves resources in inconsistent state**
**Symptom:** `cdk deploy` fails mid-deployment; CloudFormation rollback fails for a resource that cannot be rolled back (e.g., a DynamoDB table that was partially written to).
**Root Cause:** CloudFormation update rollback encountered a non-recoverable resource state.
**Diagnostic:**

```bash
# Check CloudFormation stack status
aws cloudformation describe-stack-events \
  --stack-name MyStack \
  --query \
    'StackEvents[?ResourceStatus==`UPDATE_FAILED`]' \
  --output table
```

**Fix:** Use `aws cloudformation continue-update-rollback` with `--resources-to-skip` for non-rollbackable resources. Then manually restore the skipped resource's desired state.
**Prevention:** Use change sets (`cdk diff`) and test in staging first. Enable termination protection on production stacks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- AWS CloudFormation - CDK synthesises to CloudFormation; understanding stacks, resources, change sets, and logical IDs is essential for debugging CDK deployments.
- Infrastructure as Code - understand the IaC paradigm (declarative vs imperative, idempotence, state management) before choosing CDK.
- AWS IAM - CDK L2 constructs frequently generate IAM roles automatically using grant methods; understanding what they create is essential for security review.

**Builds On This (learn these next):**

- CDK Pipelines - deploy CDK apps via self-mutating CI/CD pipelines defined in CDK itself.
- AWS CloudFormation - review generated CloudFormation templates to understand what CDK creates under the hood.
- AWS Control Tower - use CDK with Customizations for Control Tower (CfCT) to manage Landing Zone customisations as code.

**Alternatives / Comparisons:**

- AWS CloudFormation - the underlying engine; use directly when CDK abstraction adds more confusion than it removes for simple, one-off templates.
- Terraform - multi-cloud IaC with HCL; state managed externally; better for organisations using Azure/GCP alongside AWS.
- Pulumi - CDK equivalent using TypeScript/Python against a Pulumi state backend; not tied to CloudFormation.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | IaC framework generating          |
|                  | CloudFormation from TS/Python/Java  |
| PROBLEM IT SOLVES| YAML repetition, no loops/logic,  |
|                  | untestable infrastructure code      |
| KEY INSIGHT      | Construct hierarchy: L1=raw CFN,   |
|                  | L2=defaults, L3=full patterns       |
| USE WHEN         | AWS-only infra, developer-owned    |
|                  | infrastructure, reusable constructs |
| AVOID WHEN       | Multi-cloud (use Terraform);       |
|                  | simple one-off stacks (use CFN)     |
| TRADE-OFF        | Abstraction power vs hidden CFN    |
|                  | complexity on upgrades              |
| ONE-LINER        | cdk synth && cdk deploy           |
| NEXT EXPLORE     | CDK Pipelines, CloudFormation      |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** CDK L3 constructs (like `ApplicationLoadBalancedFargateService`) create 15+ CloudFormation resources in a single line. This accelerates initial setup but makes the generated resources opaque. What governance mechanism would you put in place so a security team can review what resources CDK is creating - without requiring them to read CloudFormation JSON?

2. **(First Principles)** CDK synthesises to CloudFormation, which means it inherits all of CloudFormation's limitations: stack size limits (500 resources), circular dependency restrictions, and deployment atomicity per-stack. Given these constraints, how do you design a CDK application with 300 microservices to avoid hitting stack limits while keeping deployment granularity appropriate?

3. **(Scale)** A platform team publishes a private npm package containing L2/L3 CDK constructs for their organisation's standard patterns (VPC, ECS services, RDS). 50 product teams consume this package. When a security vulnerability requires an update to the VPC construct, what rollout strategy ensures all 50 teams adopt the update within a week without breaking their individual deployments?
