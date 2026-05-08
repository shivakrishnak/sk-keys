---
layout: default
title: "AWS Security Best Practices"
parent: "Cloud — AWS"
nav_order: 61
permalink: /cloud-aws/aws-security-best-practices/
id: AWS-061
category: "Cloud — AWS"
difficulty: "★★★"
depends_on: ["IAM (Identity and Access Management)", "VPC", "CloudWatch"]
used_by: ["Well-Architected Framework"]
related:
  [
    "IAM (Identity and Access Management)",
    "Well-Architected Framework",
    "CloudWatch",
    "EKS",
  ]
tags: [aws, security, iam, encryption, compliance, hardening, cloud]
---

# AWS Security Best Practices

## ⚡ TL;DR

AWS security follows **Defense in Depth**: IAM (least privilege), network controls (VPC, SGs, NACLs), encryption (at rest + in transit), detective controls (CloudTrail, GuardDuty, Security Hub), and incident response. Key practices: never use root user, MFA everywhere, Block Public Access for S3, IMDSv2 only, Security Hub + GuardDuty enabled, secrets in Secrets Manager (never env vars with keys), rotate credentials, enable AWS Config.

---

## 🔥 Problem This Solves

AWS provides powerful capabilities but defaults that are "secure" vary by service. Misconfigured S3 buckets, overly permissive IAM policies, unencrypted databases, missing CloudTrail → breaches, data leaks, compliance failures. Systematic security practices prevent these avoidable incidents.

---

## 📘 Textbook Definition

AWS security best practices encompass the organizational, technical, and procedural controls required to secure workloads on AWS. The AWS Shared Responsibility Model divides security: AWS secures the cloud (physical hardware, hypervisor, global infrastructure); customers secure in the cloud (OS, applications, data, network configuration, IAM).

---

## ⏱️ 30 Seconds

```
Security domains:
  Identity:     MFA, least privilege IAM, no long-lived access keys
  Network:      VPC private subnets, SGs allow-only, VPC Flow Logs
  Compute:      IMDSv2, SSM Session Manager (no SSH), latest AMIs
  Data:         Encryption at rest (KMS), in transit (TLS), S3 BPA
  Logging:      CloudTrail all regions, GuardDuty, Security Hub
  Response:     AWS Config rules, automated remediation

Shared Responsibility Model:
  AWS:      Physical, hypervisor, managed service security
  Customer: IAM, OS, app, data, network config
```

---

## 🔩 First Principles

- **Least privilege**: grant minimum permissions required; deny by default; use permission boundaries
- **Defense in depth**: multiple independent security layers; breach of one doesn't compromise all
- **Immutable infrastructure**: don't patch in place; replace instances (eliminates SSH access need)
- **Encryption by default**: enable by default, not as an afterthought; AWS KMS key rotation
- **Centralized logging**: CloudTrail + VPC Flow Logs → centralized S3 + GuardDuty analysis
- **Zero trust**: never trust network location alone; always authenticate + authorize + encrypt

---

## 🧪 Thought Experiment

Attacker compromises a Lambda function via code injection. What's the blast radius? With security best practices: Lambda has least-privilege IRSA role (only DynamoDB:GetItem on specific table) → can't access S3 → can't access other services → can't create IAM keys → GuardDuty detects anomalous API calls → alert fires. Without best practices: Lambda on EC2 instance profile with `AdministratorAccess` → full account compromise. Defense in depth limits the damage.

---

## 🧠 Mental Model / Analogy

AWS security is **layers of a bank vault**: outer fence (VPC/SGs = network perimeter), security guard (IAM = identity verification), locked vault room (encryption at rest), video cameras (CloudTrail/GuardDuty = detective controls), alarm system (Security Hub = automated monitoring), emergency protocol (incident response plan). Each layer is independently secured; a breach of the fence doesn't open the vault.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Enable MFA on root and all IAM users. Enable CloudTrail in all regions. Block public access on all S3 buckets. Never use root for day-to-day tasks. Create IAM users with minimal permissions.

**Level 2 — Practitioner**: GuardDuty: enable in all regions (ML-based threat detection). Security Hub: centralized security findings. AWS Config: audit configuration drift. Secrets Manager: no hardcoded secrets. IMDSv2: enforce instance metadata token requirement. VPC Flow Logs: capture all network traffic.

**Level 3 — Advanced**: SCPs (Service Control Policies): organization-level guardrails (deny specific services, enforce region restrictions, require encryption). Permission Boundaries: prevent privilege escalation. IAM Access Analyzer: identify external access to resources. Macie: automatically discover and protect sensitive data in S3. Inspector: automated vulnerability assessment for EC2 and ECR images.

**Level 4 — Expert**: AWS Organizations security baseline: SCP to deny disabling GuardDuty/CloudTrail, deny creating root access keys, deny creating public S3 buckets, enforce MFA, restrict to allowed regions. Security Hub Standards: CIS AWS Foundations Benchmark, AWS Foundational Security Best Practices, PCI DSS. Automated remediation: Security Hub findings → EventBridge → Lambda → auto-remediate (e.g., auto-close open S3 bucket). Customer-managed KMS with key rotation + access policies + CloudTrail for key usage audit. Detective: investigation into security findings with ML-based graph analysis of CloudTrail + VPC Flow Logs.

---

## ⚙️ How It Works

### Security Baseline (Terraform)

```hcl
# 1. CloudTrail - all regions, all events
resource "aws_cloudtrail" "main" {
  name                          = "main-trail"
  s3_bucket_name               = aws_s3_bucket.audit_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true  # all regions
  enable_log_file_validation    = true  # detect tampering

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3"]  # all S3 objects
    }
    data_resource {
      type   = "AWS::Lambda::Function"
      values = ["arn:aws:lambda"]  # all Lambda invocations
    }
  }

  kms_key_id = aws_kms_key.cloudtrail.arn
}

# 2. GuardDuty - threat detection
resource "aws_guardduty_detector" "main" {
  enable                       = true
  finding_publishing_frequency = "FIFTEEN_MINUTES"

  datasources {
    s3_logs        { enable = true }
    kubernetes {
      audit_logs   { enable = true }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes { enable = true }
      }
    }
  }
}

# 3. Security Hub - aggregate findings
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0"
}

resource "aws_securityhub_standards_subscription" "aws_fsbp" {
  standards_arn = "arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0"
}

# 4. AWS Config - configuration compliance
resource "aws_config_configuration_recorder" "main" {
  name     = "main"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

# Config rules for security
resource "aws_config_config_rule" "s3_public_access" {
  name = "s3-bucket-public-access-prohibited"
  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_LEVEL_PUBLIC_ACCESS_PROHIBITED"
  }
}

resource "aws_config_config_rule" "ebs_encryption" {
  name = "ec2-ebs-encryption-by-default"
  source {
    owner             = "AWS"
    source_identifier = "EC2_EBS_ENCRYPTION_BY_DEFAULT"
  }
}

resource "aws_config_config_rule" "root_mfa" {
  name = "root-account-mfa-enabled"
  source {
    owner             = "AWS"
    source_identifier = "ROOT_ACCOUNT_MFA_ENABLED"
  }
}

# 5. S3 Block Public Access (account-level)
resource "aws_s3_account_public_access_block" "main" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 6. EBS encryption by default
resource "aws_ebs_encryption_by_default" "main" {
  enabled = true
}

# 7. IMDSv2 enforcement (no IMDSv1)
resource "aws_ec2_instance_metadata_defaults" "main" {
  http_tokens                 = "required"  # enforce IMDSv2
  http_put_response_hop_limit = 2           # allow containers to reach IMDS
}
```

### Secrets Management (No Hardcoded Secrets)

```java
// BAD: hardcoded in env var or properties
// spring.datasource.password=${DB_PASSWORD}  // env var in Task Def = visible in AWS console

// GOOD: Secrets Manager injection
@Configuration
public class DatabaseConfig {

    @Value("${DB_PASSWORD}")  // injected from Secrets Manager via ECS secrets config
    private String dbPassword;

    // Or direct API call:
    public String getSecret(String secretArn) {
        SecretsManagerClient client = SecretsManagerClient.create();
        GetSecretValueResponse response = client.getSecretValue(
            GetSecretValueRequest.builder().secretId(secretArn).build()
        );
        return response.secretString();
    }
}
```

### SCP Security Guardrails (AWS Organizations)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyDisableGuardDuty",
      "Effect": "Deny",
      "Action": [
        "guardduty:DeleteDetector",
        "guardduty:DisassociateFromMasterAccount"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyDisableCloudTrail",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:DeleteTrail",
        "cloudtrail:StopLogging",
        "cloudtrail:UpdateTrail"
      ],
      "Resource": "*",
      "Condition": {
        "ArnNotLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:role/SecurityAuditRole"
        }
      }
    },
    {
      "Sid": "DenyPublicS3",
      "Effect": "Deny",
      "Action": ["s3:PutBucketPublicAccessBlock"],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "s3:PublicAccessBlockEnabled": "false"
        }
      }
    },
    {
      "Sid": "RestrictRegions",
      "Effect": "Deny",
      "NotAction": ["sts:*", "iam:*", "cloudfront:*", "route53:*", "support:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2", "eu-west-1"]
        }
      }
    }
  ]
}
```

---

## ⚖️ Comparison Table: Security Services

| Service          | Purpose                       | Category   |
| ---------------- | ----------------------------- | ---------- |
| **IAM**          | Identity, access control      | Preventive |
| **SCPs**         | Organization-level guardrails | Preventive |
| **VPC/SGs**      | Network isolation             | Preventive |
| **KMS**          | Encryption key management     | Preventive |
| **CloudTrail**   | API audit logging             | Detective  |
| **GuardDuty**    | Threat detection (ML)         | Detective  |
| **Security Hub** | Centralized findings          | Detective  |
| **AWS Config**   | Configuration compliance      | Detective  |
| **Macie**        | S3 sensitive data discovery   | Detective  |
| **Inspector**    | Vulnerability scanning        | Detective  |
| **WAF**          | Web application firewall      | Preventive |
| **Shield**       | DDoS protection               | Preventive |

---

## ⚠️ Common Misconceptions

| Misconception                    | Reality                                                                                                         |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| "AWS handles security for me"    | Shared responsibility: you secure everything you manage (IAM, app, OS, data)                                    |
| "VPC is secure by default"       | VPC provides network isolation; IAM, encryption, and monitoring are separate layers                             |
| "Encryption means I'm compliant" | Encryption is one control; compliance requires access control, logging, policies                                |
| "GuardDuty replaces antivirus"   | GuardDuty detects AWS API-level threats; malware scanning is separate (GuardDuty Malware Protection, Inspector) |

---

## 🔗 Related Keywords

- [IAM (Identity and Access Management)](/cloud-aws/iam-identity-and-access-management/) — foundation of AWS security
- [Well-Architected Framework](/cloud-aws/well-architected-framework/) — security as one of six pillars
- [CloudWatch](/cloud-aws/cloudwatch/) — logging foundation for security monitoring

---

## 📌 Quick Reference Card

```bash
# Check if root MFA is enabled
aws iam get-account-summary \
  --query 'SummaryMap.AccountMFAEnabled'

# List IAM users without MFA
aws iam generate-credential-report
aws iam get-credential-report \
  --query 'Content' --output text | base64 -d | \
  awk -F, '$4=="false" {print $1, "- No MFA"}'

# Check CloudTrail status
aws cloudtrail describe-trails --include-shadow-trails

# Get GuardDuty findings
aws guardduty list-findings \
  --detector-id <detector-id> \
  --finding-criteria '{"Criterion":{"severity":{"Gte":7}}}'

# Check S3 buckets with public access
aws s3api list-buckets --query 'Buckets[].Name' --output text | \
  xargs -I {} aws s3api get-bucket-public-access-block --bucket {} 2>&1

# Get Security Hub findings count by severity
aws securityhub get-findings \
  --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}]}' \
  --query 'length(Findings)'
```

---

## 🧠 Think About This

The most consequential AWS security control is IAM least privilege, but the hardest part is getting there from overly permissive policies. Most teams start by attaching `AdministratorAccess` to get things working, then never tighten it. The fix: use IAM Access Analyzer to automatically generate least-privilege policies based on CloudTrail activity. Enable in IAM console → Access Analyzer → generate policy based on 90 days of CloudTrail → produces a JSON policy with only the actions your code actually called. This turns least-privilege from a manual audit into an automated workflow. Run this for every Lambda function, ECS task, and EC2 instance role. Combine with IAM permission boundaries to prevent privilege escalation: even if a developer creates a new role, it can't exceed the boundary, containing the blast radius of a compromised developer credential.
