---
layout: default
title: "S3 Storage Classes"
parent: "Cloud — AWS"
nav_order: 37
permalink: /cloud-aws/s3-storage-classes/
number: "AWS-037"
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["S3"]
used_by: ["S3 Lifecycle Policies", "AWS Cost Optimization"]
related: ["S3", "S3 Lifecycle Policies", "AWS Cost Optimization"]
tags: [aws, s3, storage-classes, glacier, intelligent-tiering, cost, cloud]
---

# S3 Storage Classes

## ⚡ TL;DR

S3 has 7+ storage classes trading **cost vs retrieval speed**: **Standard** ($0.023/GB, instant), **Intelligent-Tiering** (auto-moves based on access, no retrieval fee), **Standard-IA** ($0.0125/GB, instant but retrieval fee), **One Zone-IA** (one AZ, cheap), **Glacier Instant** (archive, instant), **Glacier Flexible** (archive, 1-12hr), **Glacier Deep Archive** ($0.00099/GB, 12hr retrieval). Use Lifecycle Policies to automate transitions.

---

## 🔥 Problem This Solves

S3 Standard is 99.9% uptime, instant access, maximum durability — but expensive for data rarely accessed. Log files from 3 years ago? Compliance archives? Old backups? These should cost 10-50x less. Storage classes provide the same durability at lower cost by trading retrieval speed and minimum storage duration.

---

## 📘 Textbook Definition

S3 storage classes are different configurations for S3 objects that trade access frequency, retrieval latency, and availability for reduced storage cost. Each class has its own pricing for storage, retrieval, and minimum storage duration charges. Selection is per-object and can be changed via lifecycle policies or explicitly on upload.

---

## ⏱️ 30 Seconds

```
Storage Class          | Storage Cost  | Retrieval | Min Duration
-----------------------|---------------|-----------|-------------
Standard               | $0.023/GB     | Instant   | None
Intelligent-Tiering    | $0.023→0.002  | Instant   | None
Standard-IA            | $0.0125/GB    | Instant   | 30 days
One Zone-IA            | $0.01/GB      | Instant   | 30 days
Glacier Instant        | $0.004/GB     | Instant   | 90 days
Glacier Flexible       | $0.0036/GB    | 1-12hr    | 90 days
Glacier Deep Archive   | $0.00099/GB   | 12-48hr   | 180 days

* Prices approximate us-east-1
* Retrieval fees apply to IA and Glacier classes
```

---

## 🔩 First Principles

- **Minimum storage duration**: charged for minimum even if deleted earlier (Standard-IA: 30 days)
- **Retrieval fee**: IA and Glacier charge per GB retrieved (in addition to storage)
- **Durability**: all classes = 11 9s EXCEPT One Zone-IA = 11 9s in one AZ (loses data if AZ fails)
- **Availability SLA**: Standard 99.99%; Standard-IA 99.9%; Glacier 99.9%
- **Intelligent-Tiering monitoring fee**: $0.0025 per 1000 objects >128KB (not free)

---

## 🧪 Thought Experiment

You have 100TB of CloudTrail audit logs for compliance. 95% is never accessed. 4% accessed in investigations (same month). 1% accessed in audits (any time). Cost in Standard: 100TB × $0.023 = $2,300/month forever. With Intelligent-Tiering: frequently accessed portion stays in Standard tier ($0.023); rest moves to Infrequent tier ($0.0125) after 30 days, Archive tier ($0.002) after 90 days. After 1 year: ~$300/month — 87% reduction.

---

## 🧠 Mental Model / Analogy

S3 storage classes are like **filing cabinets at different locations**:

- Standard = your desk (instant access, most expensive per unit)
- Standard-IA = filing room down the hall (few minutes to retrieve, cheaper)
- Glacier Flexible = offsite storage warehouse (hours to retrieve, very cheap)
- Deep Archive = underground vault in another city (days to retrieve, cheapest)

Same documents (11 9s durability), different accessibility.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Use Standard for active data. Use Intelligent-Tiering if access pattern is unknown. Use Glacier Deep Archive for backups you need to keep but rarely access.

**Level 2 — Practitioner**: Lifecycle policies automate transitions: Standard → Standard-IA after 30 days → Glacier after 90 days. Intelligent-Tiering: set it and forget it for variable-access data. Watch out for per-retrieval fees and minimum storage duration charges.

**Level 3 — Advanced**: Glacier Instant Retrieval: replaces Glacier for data needing immediate access quarterly (vs IA for monthly). Compare: Standard-IA at $0.0125 + $0.01/GB retrieval vs Glacier Instant at $0.004 + $0.03/GB retrieval — breakeven at retrieval frequency ~monthly. Multipart upload costs: transitions charged per-transition ($0.01 per 1000 lifecycle transitions).

**Level 4 — Expert**: S3 Intelligent-Tiering archive tiers: async access tier (90 days without access → $0.002/GB; automatic; 3-5hr retrieval). Deep archive tier (180 days → $0.00099/GB; 12hr retrieval). Zero retrieval fee for Intelligent-Tiering (unlike manual Glacier). Small objects: objects <128KB not monitored by Intelligent-Tiering monitoring. Objects under 128KB: skip IT for these. Cost modeling: use S3 Storage Lens + AWS Cost Explorer with granular S3 metrics to identify per-prefix cost savings opportunities.

---

## ⚙️ How It Works

### Storage Class Decision Tree

```
Data type:
  Accessed daily/weekly?       → S3 Standard
  Access pattern unknown?      → S3 Intelligent-Tiering
  Accessed monthly, no SLA?    → Standard-IA
  Non-critical, single AZ OK?  → One Zone-IA (15% cheaper than Standard-IA)
  Quarterly access, instant?   → Glacier Instant Retrieval
  Annual access, hours OK?     → Glacier Flexible
  Compliance only, days OK?    → Glacier Deep Archive

Minimum storage charges:
  Deleting Standard-IA object after 15 days?
  → Still charged for 30 days (minimum)
  → Don't use IA for objects that change frequently
```

### Setting Storage Class on Upload

```java
// Upload to Standard-IA
s3Client.putObject(
    PutObjectRequest.builder()
        .bucket(bucketName)
        .key("archive/2023/logs.gz")
        .storageClass(StorageClass.STANDARD_IA)
        .build(),
    RequestBody.fromFile(logFile)
);

// Upload to Glacier Deep Archive
s3Client.putObject(
    PutObjectRequest.builder()
        .bucket(bucketName)
        .key("compliance/2020/audit.zip")
        .storageClass(StorageClass.DEEP_ARCHIVE)
        .build(),
    RequestBody.fromFile(archiveFile)
);
```

### Copy Object to Change Storage Class

```bash
# Move existing object to cheaper tier
aws s3 cp s3://bucket/old-file.txt s3://bucket/old-file.txt \
  --storage-class STANDARD_IA \
  --metadata-directive COPY

# Bulk reclassify objects matching prefix
aws s3 cp s3://bucket/logs/2022/ s3://bucket/logs/2022/ \
  --recursive \
  --storage-class GLACIER \
  --metadata-directive COPY
```

---

## ⚖️ Comparison Table: Key Metrics

| Class               | $/GB/mo           | Retrieval     | Min Days | Durability | AZs |
| ------------------- | ----------------- | ------------- | -------- | ---------- | --- |
| Standard            | $0.023            | Instant       | None     | 11 9s      | ≥3  |
| Intelligent-Tiering | $0.023 (Frequent) | Instant       | None     | 11 9s      | ≥3  |
| Standard-IA         | $0.0125           | Instant + fee | 30       | 11 9s      | ≥3  |
| One Zone-IA         | $0.01             | Instant + fee | 30       | 11 9s      | 1   |
| Glacier Instant     | $0.004            | Instant + fee | 90       | 11 9s      | ≥3  |
| Glacier Flexible    | $0.0036           | 1-12hr + fee  | 90       | 11 9s      | ≥3  |
| Deep Archive        | $0.00099          | 12-48hr + fee | 180      | 11 9s      | ≥3  |

---

## ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                     |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| "Glacier = always hours to retrieve"      | Glacier Instant = milliseconds (like Standard-IA but cheaper for infrequent access)                                         |
| "Intelligent-Tiering is always better"    | IT has monitoring fee ($0.0025/1000 objects); for small objects or predictable access, Standard-IA lifecycle may be cheaper |
| "Changing storage class = free"           | Lifecycle transitions: $0.01 per 1000 objects; direct copy also incurs request cost                                         |
| "Delete before min duration = save money" | Minimum duration is charged regardless; plan objects' expected lifespan                                                     |

---

## 🔗 Related Keywords

- [S3](/cloud-aws/s3/) — S3 overview and core concepts
- [S3 Lifecycle Policies](/cloud-aws/s3-lifecycle-policies/) — automate storage class transitions
- [AWS Cost Optimization](/cloud-aws/aws-cost-optimization/) — storage as cost center

---

## 📌 Quick Reference Card

```bash
# Check storage class of object
aws s3api head-object \
  --bucket my-bucket \
  --key path/to/object \
  --query 'StorageClass'

# List objects with storage class
aws s3api list-objects-v2 \
  --bucket my-bucket \
  --prefix logs/ \
  --query 'Contents[].{Key:Key,Class:StorageClass,Size:Size}'

# Initiate Glacier retrieval (Flexible)
aws s3api restore-object \
  --bucket my-bucket \
  --key archive/2020/audit.zip \
  --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}'

# Check restoration status
aws s3api head-object \
  --bucket my-bucket \
  --key archive/2020/audit.zip \
  --query 'Restore'
```

---

## 🧠 Think About This

A common mistake is applying Intelligent-Tiering to ALL objects thinking it's always cheapest. Intelligent-Tiering charges a monitoring fee of $0.0025 per 1,000 objects above 128KB. For a bucket with 1 billion small objects (common for log lines, metrics, etc.), that's $2,500/month in monitoring fees alone — negating the tiering savings. The rule: use Intelligent-Tiering for large objects with unpredictable access patterns; use lifecycle policies with Standard-IA or Glacier for predictable patterns (e.g., "all logs older than 90 days go to Glacier"). For very small objects, the monitoring overhead makes Intelligent-Tiering uneconomical. Use S3 Storage Lens to analyze your object size distribution and access patterns before choosing a tiering strategy — the data often reveals that a simple lifecycle policy is more cost-effective than Intelligent-Tiering.
