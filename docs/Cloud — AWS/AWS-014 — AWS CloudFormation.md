---
layout: default
title: "AWS CloudFormation"
parent: "Cloud — AWS"
nav_order: 14
permalink: /cloud-aws/aws-cloudformation/
number: "AWS-014"
category: Cloud — AWS
difficulty: ★★★
depends_on: AWS, Infrastructure as Code, YAML
used_by: AWS CDK (Cloud Development Kit), Cloud — AWS
related: AWS CDK (Cloud Development Kit), Terraform Overview, SAM
tags:
  - aws
  - cloud
  - advanced
  - devops
  - cicd
---

# AWS-014 — AWS CloudFormation

⚡ **TL;DR —** CloudFormation is AWS's native IaC service — describe your infrastructure as a YAML/JSON template and AWS provisions, updates, and deletes it as an atomic stack with rollback on failure.

| | |
|---|---|
| **Depends on** | AWS, Infrastructure as Code, YAML |
| **Used by** | AWS CDK (Cloud Development Kit), Cloud — AWS |
| **Related** | AWS CDK (Cloud Development Kit), Terraform Overview, SAM |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Provisioning a three-tier application requires clicking through 12 AWS console screens, in the right order (VPC → subnets → security groups → RDS → EC2 → ALB). One wrong setting, and you start over. In production, a junior engineer clicks the wrong option and creates a public-facing database. There is no record of what was created or by whom.

**THE BREAKING POINT:** Manual console provisioning is not repeatable, auditable, or recoverable. Recreating a destroyed environment takes days. Environments drift from each other silently. The "production setup" exists only in someone's memory and a faded Confluence page.

**THE INVENTION MOMENT:** CloudFormation answered: what if a text file described your entire AWS environment, and AWS could create, update, or delete it as a single atomic operation — with automatic rollback if anything went wrong?

---

### 📘 Textbook Definition

**AWS CloudFormation** is a fully managed Infrastructure as Code (IaC) service that enables you to define AWS resources in a YAML or JSON **template**. CloudFormation provisions and manages related resources as a unit called a **stack**, supports atomic updates via **change sets**, detects configuration drift between the deployed stack and the actual resource state, and can deploy the same template across multiple accounts and regions using **StackSets**.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A YAML file that describes your entire AWS infrastructure; CloudFormation creates and manages it as one atomic unit.

**One analogy:**
> CloudFormation is like a construction blueprint. The blueprint describes every room, wall, and pipe in a building. A builder (CloudFormation) follows the blueprint to construct the building (AWS resources). To change the building, you revise the blueprint and the builder updates only what changed — without demolishing the whole structure.

**One insight:** CloudFormation tracks state — it knows what resources it created. An update is a diff against the current state, not a fresh creation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A template is declarative — you describe desired state, not steps to achieve it.
2. A stack is the unit of lifecycle — create, update, and delete together.
3. CloudFormation is idempotent — re-applying the same template produces the same state.
4. Rollback is automatic — if any resource fails to create or update, the entire stack reverts.

**DERIVED DESIGN:** CloudFormation builds a dependency graph from resource references within the template. Resources are provisioned in dependency order (parallel where possible). If a resource fails, CloudFormation reverses provisioning in reverse-dependency order. Logical IDs within a template identify resources; physical IDs are assigned by AWS after creation and tracked in the stack state.

**THE TRADE-OFFS:**
**Gain:** Repeatable environment provisioning, automatic rollback, change visibility (change sets), audit trail, multi-account/region deployment (StackSets).
**Cost:** YAML verbosity for complex architectures, 500-resource stack limit, no loops or conditionals (addressed by CDK/macros), CloudFormation eventual consistency on some resource types.

---

### 🧪 Thought Experiment

**SETUP:** Your production environment has an EC2 Auto Scaling Group, RDS cluster, ALB, 3 security groups, and 10 IAM roles. A disaster recovery exercise requires recreating this in a new region in under 30 minutes.

**WHAT HAPPENS WITHOUT CloudFormation:** The team manually recreates each resource in the AWS console for the new region. After 4 hours, they have 80% of the resources. Two security group rules are missing. The RDS parameter group is wrong. The DR test fails.

**WHAT HAPPENS WITH CloudFormation:** The team runs `aws cloudformation deploy --template-file prod.yaml --region eu-west-1`. In 15 minutes, the identical environment exists in Europe. The security groups, IAM roles, and RDS parameter group match production exactly. DR test passes.

**THE INSIGHT:** CloudFormation transforms infrastructure from tribal knowledge into executable documentation. The template is both the spec and the implementation.

---

### 🧠 Mental Model / Analogy

> CloudFormation is like a recipe book for your cloud kitchen. The recipe (template) lists every ingredient (resource) and the steps (dependencies). The chef (CloudFormation) follows the recipe to prepare the dish (stack). If an ingredient is unavailable (resource fails), the chef returns the kitchen to its original state (rollback). You can scale the recipe up (StackSets across regions) without rewriting it.

- **Recipe** = CloudFormation template (YAML/JSON)
- **Ingredients** = AWS resources (EC2, RDS, S3)
- **Chef** = CloudFormation service
- **Dish** = deployed stack
- **Returns to original state** = automatic rollback
- **Scaling the recipe** = StackSets

Where this analogy breaks down: a chef can improvise; CloudFormation strictly follows the template and fails predictably if a resource definition is incorrect.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CloudFormation is a way to write down your AWS setup in a text file, then have AWS automatically build it for you — the same way every time, and automatically undo the changes if something goes wrong.

**Level 2 — How to use it (junior developer):**
Write a YAML template with a `Resources:` section listing each AWS resource and its properties. Deploy with `aws cloudformation deploy`. View resources in the CloudFormation console. To update, modify the template and redeploy. To delete all resources, delete the stack.

**Level 3 — How it works (mid-level engineer):**
CloudFormation parses the template, builds a dependency graph using `Ref` and `!Sub` inter-resource references, and calls AWS service APIs in dependency order. On update, it creates a change set — a plan showing which resources will be added, modified, or replaced. Replacement happens when a property change requires resource recreation (e.g., changing an RDS `engine` property). Rollback triggers are CloudWatch alarms that revert the stack if they fire within a configurable monitoring window post-deployment.

**Level 4 — Why it was designed this way (senior/staff):**
The logical ID / physical ID separation is a fundamental design choice with deep implications. Logical IDs are template-scoped identifiers that persist across the stack lifecycle. When you rename a logical ID, CloudFormation treats it as a delete + create — potentially causing data loss for stateful resources. This is why you cannot safely rename an RDS resource in a template without using `DeletionPolicy: Retain`. The design prioritises state tracking accuracy over schema flexibility — a conservative choice that prevents silent data destruction but requires discipline in template evolution.

---

### ⚙️ How It Works (Mechanism)

1. **Template** — YAML or JSON document with sections: `Parameters`, `Mappings`, `Conditions`, `Resources` (required), `Outputs`.
2. **Stack** — a collection of AWS resources managed as a unit. One template → one or more stacks.
3. **Change set** — a preview of what `cloudformation:UpdateStack` will do before executing. Create → review → execute.
4. **Stack policy** — prevents accidental updates to specific resources (e.g., production RDS).
5. **Drift detection** — compares actual resource configuration to the template's expected state. Reports drifted properties.
6. **StackSets** — deploy one template to multiple accounts and/or regions simultaneously using a delegated admin account.
7. **Rollback triggers** — CloudWatch alarms monitored during deployment; if they breach, the stack rolls back automatically.
8. **Custom resources** — invoke Lambda functions for operations CloudFormation doesn't natively support (e.g., populating a DynamoDB table, calling a third-party API).
9. **DeletionPolicy** — control what happens to a resource when the stack is deleted: `Delete` (default), `Retain`, or `Snapshot`.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer modifies template.yaml
     |
     | aws cloudformation create-change-set
     v
CloudFormation
  [parse template]
  [build dependency graph]
  [diff against current stack state]
  [create change set: 3 Add, 1 Modify, 0 Remove]
     |           ← YOU ARE HERE
     | execute-change-set
     v
CloudFormation calls AWS service APIs
  [parallel: VPC, IAM role, S3 bucket]
  [sequential: subnet (needs VPC), EC2 (needs subnet)]
     |
     | All succeed → stack UPDATE_COMPLETE
     | Any fail   → rollback in reverse order
     v
Stack state updated (logical → physical ID mapping)
```

**FAILURE PATH:**
- Resource creation fails → automatic rollback to previous state
- Rollback fails (resource in bad state) → stack enters `UPDATE_ROLLBACK_FAILED`; requires manual intervention with `continue-update-rollback`
- Stack policy blocks update → `InsufficientCapabilitiesException`

**WHAT CHANGES AT SCALE:**
Nested stacks decompose large templates (>500 resources) into parent-child relationships. StackSets with AWS Organizations integration deploy automatically to new accounts. Service-managed StackSets can target entire OUs without listing individual accounts.

---

### 💻 Code Example

**Basic CloudFormation template (S3 + SNS notification):**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: App storage with event notification

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  AppBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: !If [IsProd, Retain, Delete]
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
      VersioningConfiguration:
        Status: !If [IsProd, Enabled, Suspended]
      NotificationConfiguration:
        TopicConfigurations:
          - Event: s3:ObjectCreated:*
            Topic: !Ref UploadTopic

  UploadTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub '${AWS::StackName}-uploads'

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref AppBucket
      PolicyDocument:
        Statement:
          - Effect: Deny
            Principal: '*'
            Action: s3:*
            Resource:
              - !GetAtt AppBucket.Arn
              - !Sub '${AppBucket.Arn}/*'
            Condition:
              Bool:
                aws:SecureTransport: false

Outputs:
  BucketName:
    Value: !Ref AppBucket
    Export:
      Name: !Sub '${AWS::StackName}-bucket'
  TopicArn:
    Value: !Ref UploadTopic
```

**AWS CLI — change set workflow:**
```bash
# Deploy with change set review
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name my-app-dev \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-execute-changeset

# Review the change set
aws cloudformation describe-change-set \
  --stack-name my-app-dev \
  --change-set-name \
    deploymentchangeset-$(date +%s) \
  --query 'Changes[*].ResourceChange'

# Execute after review
aws cloudformation execute-change-set \
  --stack-name my-app-dev \
  --change-set-name <changeset-name>

# Detect drift
aws cloudformation detect-stack-drift \
  --stack-name my-app-dev

aws cloudformation describe-stack-resource-drifts \
  --stack-name my-app-dev \
  --stack-resource-drift-status MODIFIED DELETED
```

---

### ⚖️ Comparison Table

| Feature | CloudFormation | AWS CDK | Terraform | AWS SAM |
|---|---|---|---|---|
| **Language** | YAML/JSON | TS/Python/Java/C#/Go | HCL | YAML (CFN superset) |
| **State storage** | AWS-managed | AWS-managed (via CFN) | Local/remote tfstate | AWS-managed |
| **Rollback** | Automatic | Via CloudFormation | Manual (destroy+apply) | Via CloudFormation |
| **Multi-cloud** | No | No | Yes | No |
| **Loops/logic** | Limited (Conditions) | Full language support | `count`, `for_each` | Limited |
| **Drift detection** | Yes (native) | Via CloudFormation | `terraform plan` | Via CloudFormation |
| **Best for** | AWS-native, direct control | Developer-owned IaC | Multi-cloud | Serverless apps |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Deleting a stack deletes all resources" | Resources with `DeletionPolicy: Retain` survive stack deletion. Production databases should always use `Retain` to prevent accidental deletion. |
| "Renaming a resource in a template is safe" | Changing a logical ID causes CloudFormation to delete the old resource and create a new one. For stateful resources (RDS, EFS), this causes data loss without `Retain`. |
| "Change sets show every impact" | Change sets show direct resource changes. They don't show cascading effects (e.g., replacing an EC2 security group may briefly drop connections). |
| "CloudFormation is slow because it's inferior to Terraform" | CloudFormation deploys resources in parallel where the dependency graph allows. Perceived slowness is often due to specific resource types (IAM propagation, RDS creation) not CloudFormation itself. |
| "You can have unlimited resources in a stack" | Stacks are limited to 500 resources. Nested stacks partially work around this but each nested stack also counts toward parent limits. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Stack stuck in UPDATE_ROLLBACK_FAILED**
**Symptom:** Stack update failed and rollback also failed; stack is in `UPDATE_ROLLBACK_FAILED` state; no further updates possible.
**Root Cause:** A resource that CloudFormation tried to restore during rollback is in an unrecoverable state (e.g., security group still has dependencies, DynamoDB table has stream consumers).
**Diagnostic:**
```bash
aws cloudformation describe-stack-events \
  --stack-name my-app \
  --query \
    'StackEvents[?ResourceStatus==`UPDATE_FAILED` \
    || ResourceStatus==`ROLLBACK_FAILED`]' \
  --output table
```
**Fix:** Use `continue-update-rollback` with `--resources-to-skip` to skip the problematic resource. Then manually restore its desired state outside CloudFormation.
**Prevention:** Test updates via change sets in staging. Use `DeletionPolicy: Retain` on stateful resources to reduce rollback complexity.

**Mode 2: Drift causing deployment failure**
**Symptom:** `aws cloudformation deploy` fails because an out-of-band change to a resource conflicts with the template update.
**Root Cause:** Someone manually changed a resource (e.g., modified a security group rule via console) after the last stack deployment. The template update assumes the old state.
**Diagnostic:**
```bash
aws cloudformation detect-stack-drift \
  --stack-name my-app
# Wait ~30 seconds
aws cloudformation describe-stack-resource-drifts \
  --stack-name my-app \
  --stack-resource-drift-status MODIFIED
```
**Fix:** Reconcile the drift: either update the template to match the manual change or revert the manual change to match the template.
**Prevention:** Never manually modify CloudFormation-managed resources. Use SCPs or IAM policies to block direct console changes on production stacks.

**Mode 3: CAPABILITY_NAMED_IAM required**
**Symptom:** `aws cloudformation deploy` fails immediately with `InsufficientCapabilitiesException: Requires capabilities: [CAPABILITY_NAMED_IAM]`.
**Root Cause:** Template creates or modifies IAM resources with custom names. CloudFormation requires explicit acknowledgment to prevent accidental privilege escalation.
**Diagnostic:**
```bash
# Check which resources require the capability
grep -n "AWS::IAM" template.yaml
grep -n "AWS::IAM::" template.yaml | grep -v "Ref\|GetAtt"
```
**Fix:** Add `--capabilities CAPABILITY_NAMED_IAM` to the deploy command after reviewing the IAM resources being created.
**Prevention:** Add the `--capabilities` flag to all deployment scripts that include IAM resources. Document which capabilities each template requires.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Infrastructure as Code — understand declarative vs imperative IaC, idempotence, and state management before CloudFormation makes sense.
- AWS IAM — CloudFormation creates IAM roles; understanding what permissions are being granted is essential for security review.
- YAML — CloudFormation templates are YAML documents; YAML indentation and anchoring syntax must be understood.

**Builds On This (learn these next):**
- AWS CDK — generates CloudFormation templates from TypeScript/Python code; CDK mastery requires CloudFormation understanding for debugging.
- AWS SAM — CloudFormation extension for serverless applications; understand CloudFormation first as SAM compiles to it.
- AWS Control Tower — uses CloudFormation StackSets to deploy governance baselines to all accounts in an organisation.

**Alternatives / Comparisons:**
- Terraform — HCL-based IaC; self-managed state; better for multi-cloud; does not use CloudFormation under the hood.
- AWS CDK — developer-friendly layer above CloudFormation; appropriate when infrastructure logic needs loops and conditionals.
- AWS SAM — CloudFormation superset optimised for Lambda, API Gateway, and DynamoDB serverless patterns.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | AWS-native IaC: YAML/JSON template |
|                  | creates/updates resources as a stack|
| PROBLEM IT SOLVES| Manual provisioning, environment   |
|                  | drift, no rollback on failure       |
| KEY INSIGHT      | Template is both spec and state;   |
|                  | logical ID tracks physical resource |
| USE WHEN         | AWS-only infra, native integration,|
|                  | StackSets for multi-account deploy  |
| AVOID WHEN       | Complex logic (use CDK); multi-     |
|                  | cloud (use Terraform); >500 resources|
| TRADE-OFF        | YAML verbosity vs full AWS-native  |
|                  | rollback and state management       |
| ONE-LINER        | cloudformation:CreateChangeSet     |
| NEXT EXPLORE     | AWS CDK, StackSets, Change Sets    |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Root Cause)** CloudFormation prevents you from renaming a logical ID without deleting and recreating the resource. This means renaming an RDS `DBInstance` in a template causes a database deletion. What design practice at template authoring time prevents this from ever becoming a problem in production stacks?

2. **(System Interaction)** StackSets deploy a template to 200 accounts across 3 regions. A security team needs to update a security group rule in the baseline template. The StackSet update will modify running workloads in 600 stack instances. What deployment strategy (failure tolerance, operation preferences) minimises risk while completing the rollout within a maintenance window?

3. **(Design Trade-off)** CloudFormation uses AWS-managed state (you cannot access the state file directly), while Terraform uses an explicit state file you control. What are the security and operational implications of each model, and under what organisational scenario does the lack of direct state access in CloudFormation become a significant limitation?
