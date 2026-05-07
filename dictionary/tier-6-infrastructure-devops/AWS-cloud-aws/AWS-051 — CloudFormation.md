---
layout: default
title: "CloudFormation"
parent: "Cloud — AWS"
nav_order: 51
permalink: /cloud-aws/cloudformation/
number: "AWS-051"
category: "Cloud — AWS"
difficulty: "★★★"
depends_on:
  ["IAM (Identity and Access Management)", "AWS Global Infrastructure"]
used_by: ["CDK", "AWS Cost Optimization"]
related: ["CDK", "CloudWatch", "IAM (Identity and Access Management)"]
tags: [aws, cloudformation, iac, infrastructure-as-code, stack, template, cloud]
---

# CloudFormation

## ⚡ TL;DR

**CloudFormation** is AWS's native Infrastructure-as-Code service. Define AWS resources in YAML/JSON templates; CloudFormation creates, updates, and deletes resources as a **stack**. Idempotent: re-run the same template = same result. Handles dependency ordering automatically. Drift detection: compares template vs actual resource state. Most teams use **CDK** (synthesizes to CloudFormation) or **Terraform** (multi-cloud IaC) instead of raw CloudFormation templates.

---

## 🔥 Problem This Solves

Manually creating AWS resources via console: not repeatable, not auditable, hard to replicate environments, disaster recovery is guesswork. CloudFormation: define resources as code → deploy to multiple environments consistently → version control → rollback on failure → audit history.

---

## 📘 Textbook Definition

AWS CloudFormation provides a way to model, provision, and manage AWS and third-party application resources by treating infrastructure as code. A CloudFormation template defines resources; a stack is an instance of that template. CloudFormation handles resource ordering, dependency resolution, rollback on failure, and change sets for previewing updates.

---

## ⏱️ 30 Seconds

```yaml
# CloudFormation template structure
AWSTemplateFormatVersion: "2010-09-09"
Description: "My infrastructure"

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Resources: # Required: at least one resource
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "my-bucket-${Environment}"
      VersioningConfiguration:
        Status: Enabled

Outputs:
  BucketName:
    Value: !Ref MyBucket
    Export:
      Name: !Sub "${AWS::StackName}-BucketName"
```

---

## 🔩 First Principles

- **Stack**: collection of AWS resources deployed together from one template; lifecycle managed as unit
- **Change sets**: preview changes before applying (like `terraform plan`)
- **Rollback**: on create/update failure, CloudFormation automatically rolls back to last stable state
- **Stack policies**: IAM-like JSON to protect specific resources from updates (e.g., protect RDS from accidental replacement)
- **Intrinsic functions**: `!Ref`, `!Sub`, `!GetAtt`, `!If`, `!Select`, `!Split`, `!ImportValue` — template logic
- **Nested stacks**: break large templates into smaller reusable templates (anti-pattern at scale; use StackSets for multi-account)

---

## 🧪 Thought Experiment

Three environments (dev/staging/prod). Each needs: VPC, RDS, ECS cluster, ALB. Without CloudFormation: create each manually (error-prone). With CloudFormation: one template with Parameters. Deploy with `Environment=dev` → dev stack. Deploy with `Environment=prod` → prod stack. Same resources, same configuration, different parameter values. Delete dev stack: all 20+ resources deleted in correct order automatically.

---

## 🧠 Mental Model / Analogy

CloudFormation is a **house blueprint and construction team**: you provide the blueprint (template) and CloudFormation builds the house (stack). Want to renovate (update)? Show the updated blueprint; CloudFormation figures out what walls to move (updates only changed resources). Renovation goes wrong? CloudFormation restores the original house (rollback). Buy three identical houses? Deploy the same blueprint three times with different addresses (parameters).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Write template for S3 bucket, EC2 instance, security group. Deploy via console or `aws cloudformation deploy`. View events as resources are created.

**Level 2 — Practitioner**: Parameters with types and constraints. Outputs with Exports for cross-stack references. Change sets: `aws cloudformation create-change-set` → review → execute. Drift detection: identify resources manually changed outside CloudFormation.

**Level 3 — Advanced**: StackSets: deploy same template across multiple accounts and/or regions. CloudFormation hooks: pre/post provision validation (Lambda or GuardDuty). Custom Resources: `AWS::CloudFormation::CustomResource` → invoke Lambda for non-native resources (create DNS record, configure third-party service). Macros: transform templates before deployment (like CDK aspect but in YAML).

**Level 4 — Expert**: CloudFormation Registry: third-party resource providers (HashiCorp Terraform resources, GitHub resources via CloudFormation). Stack termination protection: prevent accidental deletion. RetainOnDelete: set `DeletionPolicy: Retain` to preserve resources when stack is deleted (RDS, S3). Resource import: bring existing resources under CloudFormation management without recreation. SAM (Serverless Application Model): CloudFormation extension with shorthand for Lambda, API Gateway, DynamoDB. cfn-lint: validate templates before deploy. cfn-guard: policy-as-code rules for templates.

---

## ⚙️ How It Works

### Production VPC Template (YAML)

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: "Production VPC with public/private subnets"

Parameters:
  ProjectName:
    Type: String
    Default: myapp
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
  VpcCidr:
    Type: String
    Default: "10.0.0.0/16"

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-${Environment}-vpc"

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  VPCGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Cidr [!Ref VpcCidr, 4, 8]]
      AvailabilityZone: !Select [0, !GetAZs ""]
      MapPublicIpOnLaunch: true

  PublicSubnetB:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [1, !Cidr [!Ref VpcCidr, 4, 8]]
      AvailabilityZone: !Select [1, !GetAZs ""]
      MapPublicIpOnLaunch: true

  # NAT Gateway for private subnets
  NatEIP:
    Type: AWS::EC2::EIP
    DependsOn: VPCGatewayAttachment
    Properties:
      Domain: vpc

  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatEIP.AllocationId
      SubnetId: !Ref PublicSubnetA

  PrivateSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [2, !Cidr [!Ref VpcCidr, 4, 8]]
      AvailabilityZone: !Select [0, !GetAZs ""]

  # Route tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: VPCGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: "0.0.0.0/0"
      GatewayId: !Ref InternetGateway

  PublicSubnetARouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnetA
      RouteTableId: !Ref PublicRouteTable

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}-VpcId"

  PublicSubnetIds:
    Value: !Join [",", [!Ref PublicSubnetA, !Ref PublicSubnetB]]
    Export:
      Name: !Sub "${AWS::StackName}-PublicSubnetIds"

  NatGatewayId:
    Value: !Ref NatGateway
    Export:
      Name: !Sub "${AWS::StackName}-NatGatewayId"
```

### Deployment Commands

```bash
# Deploy stack (create or update)
aws cloudformation deploy \
  --template-file vpc.yml \
  --stack-name production-vpc \
  --parameter-overrides \
    ProjectName=myapp \
    Environment=prod \
    VpcCidr=10.0.0.0/16 \
  --capabilities CAPABILITY_NAMED_IAM

# Preview changes before applying
aws cloudformation create-change-set \
  --stack-name production-vpc \
  --template-body file://vpc.yml \
  --change-set-name my-changes \
  --parameters ParameterKey=Environment,ParameterValue=prod

aws cloudformation describe-change-set \
  --stack-name production-vpc \
  --change-set-name my-changes \
  --query 'Changes[].ResourceChange.{Action:Action,Resource:ResourceType,Id:LogicalResourceId}'

aws cloudformation execute-change-set \
  --stack-name production-vpc \
  --change-set-name my-changes

# Check stack status
aws cloudformation describe-stacks \
  --stack-name production-vpc \
  --query 'Stacks[0].{Status:StackStatus,Reason:StackStatusReason}'

# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name production-vpc \
  --query 'Stacks[0].Outputs'

# Detect drift
aws cloudformation detect-stack-drift --stack-name production-vpc

aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id <detection-id>
```

---

## ⚖️ Comparison Table: CloudFormation vs Terraform vs CDK

|                    | CloudFormation      | Terraform                | CDK                     |
| ------------------ | ------------------- | ------------------------ | ----------------------- |
| **Language**       | YAML/JSON           | HCL                      | TypeScript/Python/Java  |
| **Multi-cloud**    | ❌ (AWS only)       | ✅                       | ❌ (AWS only)           |
| **State**          | Managed by AWS      | Local/remote state file  | Via CloudFormation      |
| **Type safety**    | None                | Partial                  | Full                    |
| **Abstraction**    | Low (raw resources) | Low-medium               | High (L2/L3 constructs) |
| **Ecosystem**      | AWS registry        | Large provider ecosystem | CDK Constructs Hub      |
| **Learning curve** | Medium              | Medium                   | High                    |

---

## ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                      |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| "CloudFormation YAML is verbose but equivalent to Terraform" | CloudFormation lacks plan before apply safety (use Change Sets); less expressive than HCL                                    |
| "Rollback always works"                                      | Some resource types can't roll back (Lambda code artifacts, some DB schema changes); test in staging                         |
| "Nested stacks solve all scale problems"                     | Nested stacks add complexity; prefer StackSets for multi-account and separate sibling stacks for separate lifecycle concerns |
| "CDK vs CloudFormation is a choice"                          | CDK synthesizes to CloudFormation; using CDK = using CloudFormation under the hood                                           |

---

## 🔗 Related Keywords

- [CDK](/cloud-aws/cdk/) — programmatic IaC that compiles to CloudFormation
- [IAM (Identity and Access Management)](/cloud-aws/iam-identity-and-access-management/) — CloudFormation needs IAM permissions to create resources

---

## 📌 Quick Reference Card

```bash
# Validate template
aws cloudformation validate-template \
  --template-body file://template.yml

# List stacks
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query 'StackSummaries[].{Name:StackName,Status:StackStatus}'

# Describe stack resources
aws cloudformation list-stack-resources \
  --stack-name my-stack \
  --query 'StackResourceSummaries[].{Type:ResourceType,Id:LogicalResourceId,Status:ResourceStatus}'

# Delete stack
aws cloudformation delete-stack --stack-name my-stack

# Enable termination protection
aws cloudformation update-termination-protection \
  --stack-name production-vpc \
  --enable-termination-protection
```

---

## 🧠 Think About This

The most painful CloudFormation failure mode is a stuck stack during rollback. When a stack update fails, CloudFormation attempts to roll back. If the rollback also fails (e.g., a resource in ROLLBACK_FAILED state), the stack is stuck and you can't update or delete it normally. This happens most often with custom resources, RDS instances with data, or when a resource was manually modified outside CloudFormation. Prevention: (1) Use Change Sets to preview before applying. (2) Test in a staging stack first. (3) Set DeletionPolicy=Retain on stateful resources (RDS, S3) so rollback doesn't try to delete them. (4) If stuck in ROLLBACK_FAILED: use `continue-update-rollback` with `--resources-to-skip` to mark the problematic resource as skipped, allowing the stack to return to a stable state.
