---
version: 1
layout: default
title: "S3 Lifecycle Policies"
parent: "Cloud - AWS"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/cloud-aws/s3-lifecycle-policies/
id: AWS-020
category: "Cloud - AWS"
difficulty: "★★★"
depends_on: ["S3", "S3 Storage Classes"]
used_by: ["AWS Cost Optimization"]
related: ["S3", "S3 Storage Classes", "AWS Cost Optimization"]
tags: [aws, s3, lifecycle, cost-optimization, transitions, expiration, cloud]
---

## ⚡ TL;DR

S3 Lifecycle Policies automate two things: **transition** (move objects to cheaper storage class after N days) and **expiration** (delete objects after N days). Define rules per prefix or tag. Handles versioned buckets: separately manage current versions, noncurrent versions, and delete markers. Essential for S3 cost control.

---

## 🔥 Problem This Solves

S3 storage grows indefinitely without cleanup. Application logs from 2019, old backups, stale cache files, expired artifacts - all accumulate and cost money. Manually cleaning is error-prone. Lifecycle policies are serverless, automatic, auditable rules: "move to IA after 30 days, Glacier after 90 days, delete after 365 days."

---

## 📘 Textbook Definition

An S3 Lifecycle configuration is a set of rules that define actions Amazon S3 applies to objects during their lifetime. Transition actions change the storage class; expiration actions delete objects. Rules can filter by prefix, tag, or object size. For versioned buckets, rules can target current versions, noncurrent versions, and expired object delete markers separately.

---

## ⏱️ 30 Seconds

```yaml
# Lifecycle rule concept:
Rule:
  Filter: prefix=logs/ OR tag=Environment:dev
  Transitions:
    - Days: 30   → STANDARD_IA
    - Days: 90   → GLACIER
    - Days: 365  → DEEP_ARCHIVE
  Expiration:
    - Days: 2555 # 7 years, then delete

  # For versioned buckets, also:
  NoncurrentVersionTransitions:
    - NoncurrentDays: 1 → GLACIER
  NoncurrentVersionExpiration:
    - NoncurrentDays: 30 # delete old versions
  ExpiredObjectDeleteMarker: true # clean up delete markers
```

---

## 🔩 First Principles

- **Lifecycle runs daily**: AWS evaluates rules daily; not real-time
- **Minimum before transition**: Standard → IA requires ≥30 days; Standard → Glacier requires ≥1 day
- **Minimum duration charges**: transitioning to IA doesn't avoid the 30-day minimum charge
- **Versioned buckets complexity**: each version is independently managed; deleted objects become "noncurrent" (not gone)
- **Transition costs**: $0.01 per 1,000 objects transitioned (small but real at scale)
- **Expiration is irreversible**: unless versioning is enabled (expiration adds delete marker)

---

## 🧪 Thought Experiment

CI/CD pipeline stores build artifacts in S3. Artifacts from last 30 builds needed instantly for rollback. Older artifacts needed for compliance for 1 year. Artifacts >1 year: delete. Without lifecycle: bucket grows indefinitely. With lifecycle: active builds → Standard; >30 days → Glacier Instant (instant retrieval, 1/6th cost); >1 year → expire/delete. Zero manual operations, optimal cost.

---

## 🧠 Mental Model / Analogy

Lifecycle policies are like **library book management**: new books on the front shelf (Standard), older books move to back stacks after 30 days (Standard-IA), rarely requested books move to off-site storage after 90 days (Glacier), and books not accessed in 7 years are discarded (expiration). All automated by the librarian (S3 lifecycle engine).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create a lifecycle rule to move all objects to Standard-IA after 30 days and Glacier after 90 days. Add expiration after 365 days for log buckets.

**Level 2 - Practitioner**: Filter by prefix (`logs/`) and tags (`Environment=staging`). Versioned bucket handling: expire noncurrent versions after 30 days to avoid accumulating version costs. Clean up incomplete multipart uploads (common source of hidden costs).

**Level 3 - Advanced**: Orchestrate multi-tier transitions: Standard → IT → Glacier Instant → Glacier Flexible → Deep Archive. Minimum day constraints: can't go Standard → IA → Glacier in fewer than 60 days (30-day minimums compound). Separate rules for different data categories in the same bucket using prefixes.

**Level 4 - Expert**: Cost modeling: lifecycle transition request costs at scale ($0.01/1000 objects × 10 billion objects = $100 per transition event). For high-object-count workloads, batch transitions with S3 Batch Operations instead. CloudTrail + S3 Access Logs → Athena queries to determine actual access frequency before setting lifecycle days. Account for data access patterns: if old logs are regularly queried for compliance investigations, Glacier retrieval fees may exceed Standard-IA storage savings - use access log analysis to tune days.

---

## ⚙️ How It Works

---

### Comprehensive Lifecycle Policy (Terraform)

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "app_logs" {
  bucket = aws_s3_bucket.app.id

  # Rule 1: Application logs - multi-tier archive
  rule {
    id     = "application-logs-lifecycle"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    # Transition current objects through storage tiers
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER_IR"  # Glacier Instant Retrieval
    }
    transition {
      days          = 365
      storage_class = "GLACIER"     # Glacier Flexible
    }
    transition {
      days          = 730
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete after 7 years (compliance requirement)
    expiration {
      days = 2555
    }
  }

  # Rule 2: Cleanup old versions (versioned bucket)
  rule {
    id     = "cleanup-noncurrent-versions"
    status = "Enabled"

    filter {
      prefix = ""  # all objects
    }

    # Transition old versions to Glacier quickly
    noncurrent_version_transition {
      noncurrent_days = 1
      storage_class   = "GLACIER"
    }

    # Delete old versions after 30 days
    noncurrent_version_expiration {
      noncurrent_days                 = 30
      newer_noncurrent_versions       = 5  # keep last 5 versions
    }

    # Clean up expired delete markers
    expiration {
      expired_object_delete_marker = true
    }
  }

  # Rule 3: Dev environment - aggressive cleanup by tag
  rule {
    id     = "dev-environment-cleanup"
    status = "Enabled"

    filter {
      and {
        tags = {
          "Environment" = "dev"
          "Temporary"   = "true"
        }
      }
    }

    expiration {
      days = 7  # delete dev temp files after 7 days
    }
  }

  # Rule 4: Incomplete multipart uploads - CRITICAL for cost
  rule {
    id     = "abort-incomplete-multipart-uploads"
    status = "Enabled"

    filter {
      prefix = ""  # all
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
      # abort uploads not completed in 7 days
    }
  }

  # Rule 5: Build artifacts
  rule {
    id     = "build-artifacts"
    status = "Enabled"

    filter {
      prefix = "artifacts/"
    }

    transition {
      days          = 30
      storage_class = "GLACIER_IR"
    }

    expiration {
      days = 365  # artifacts expire after 1 year
    }
  }
}
```

---

### Verifying Lifecycle with Cost Estimate

```bash
# List lifecycle rules on a bucket
aws s3api get-bucket-lifecycle-configuration \
  --bucket my-app-bucket

# Manually check what would transition today (S3 doesn't preview)
# Use Storage Lens or Inventory to estimate

# Generate S3 Inventory (daily/weekly CSV of objects + metadata)
aws s3api put-bucket-inventory-configuration \
  --bucket my-app-bucket \
  --id "cost-analysis" \
  --inventory-configuration '{
    "Destination": {
      "S3BucketDestination": {
        "Bucket": "arn:aws:s3:::my-inventory-bucket",
        "Format": "CSV"
      }
    },
    "IsEnabled": true,
    "Id": "cost-analysis",
    "IncludedObjectVersions": "All",
    "Schedule": {"Frequency": "Daily"},
    "OptionalFields": ["StorageClass", "LastModifiedDate", "Size"]
  }'
```

---

## ⚖️ Comparison Table: Lifecycle Action Types

| Action                         | Type                | Effect                                                  |
| ------------------------------ | ------------------- | ------------------------------------------------------- |
| Transition                     | Current version     | Moves to cheaper storage class                          |
| Expiration                     | Current version     | Adds delete marker (versioned) or deletes (unversioned) |
| NoncurrentVersionTransition    | Old versions        | Moves noncurrent versions to cheaper class              |
| NoncurrentVersionExpiration    | Old versions        | Permanently deletes noncurrent versions                 |
| AbortIncompleteMultipartUpload | In-progress uploads | Cancels and cleans up incomplete uploads                |

---

## ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                             |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| "Expiration immediately deletes versioned objects"    | In versioned buckets, expiration adds a delete marker; object persists as noncurrent version        |
| "Lifecycle runs instantly when condition is met"      | Lifecycle runs once per day; delay is up to 24 hours                                                |
| "I can skip Standard-IA and go straight to Glacier"   | Allowed! You can transition Standard → Glacier directly (no IA requirement)                         |
| "Multipart uploads don't cost money if not completed" | Incomplete multipart uploads accrue storage charges; always set AbortIncompleteMultipartUpload rule |

---

## 🔗 Related Keywords

- [S3](/cloud-aws/s3/) - object storage fundamentals
- [S3 Storage Classes](/cloud-aws/s3-storage-classes/) - storage tiers overview
- [AWS Cost Optimization](/cloud-aws/aws-cost-optimization/) - S3 as major cost driver

---

## 📌 Quick Reference Card

```bash
# Put lifecycle configuration
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json

# Get current lifecycle config
aws s3api get-bucket-lifecycle-configuration \
  --bucket my-bucket

# Delete lifecycle config
aws s3api delete-bucket-lifecycle \
  --bucket my-bucket

# Quick lifecycle JSON for logs (save as lifecycle.json):
cat > lifecycle.json << 'EOF'
{
  "Rules": [{
    "ID": "logs-lifecycle",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 90, "StorageClass": "GLACIER"}
    ],
    "Expiration": {"Days": 365},
    "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
  }]
}
EOF
```

---

## 🧠 Think About This

The single highest-impact lifecycle rule that most teams miss: **AbortIncompleteMultipartUpload**. Large file uploads use S3 multipart: break into parts, upload in parallel, complete. If the upload fails or the client crashes, the parts remain in S3 and accrue storage charges indefinitely - they're invisible in the bucket listing but cost money. A 10GB failed upload leaves 10GB of orphaned parts. Multiply by thousands of CI/CD pipelines, and this becomes significant. Setting `AbortIncompleteMultipartUpload: DaysAfterInitiation: 7` is free and immediately reclaims this storage. Check your current exposure: `aws s3api list-multipart-uploads --bucket your-bucket`. You'll often find forgotten uploads that have been accumulating charges for months.
