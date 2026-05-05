---
layout: default
title: "EBS / EFS"
parent: "Cloud — AWS"
nav_order: 935
permalink: /cloud-aws/ebs-efs/
number: "0935"
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["EC2", "VPC", "AWS Global Infrastructure"]
used_by: ["RDS", "ECS / Fargate", "EKS"]
related: ["S3", "EC2", "RDS", "AWS Cost Optimization"]
tags: [aws, ebs, efs, storage, block-storage, file-storage, ec2, cloud]
---

# EBS / EFS

## ⚡ TL;DR

**EBS (Elastic Block Store)**: persistent block storage for EC2 — like a network-attached hard drive. Single instance (usually), AZ-scoped, high IOPS. Use for OS volumes, databases, high-performance workloads. **EFS (Elastic File System)**: managed NFS shared across multiple EC2 instances or containers, scales automatically. Use for shared config, media, home directories, container shared storage.

---

## 🔥 Problem This Solves

EC2 instance local storage is ephemeral (terminates with instance). Applications need persistent storage. EBS provides persistent block volumes that survive instance termination. EFS solves multi-instance file sharing where S3 HTTP API is too high-latency or inconvenient (POSIX filesystem semantics needed).

---

## 📘 Textbook Definition

**EBS**: provides raw block-level storage volumes attached to EC2 instances; formatted with a filesystem and used like a local disk; AZ-specific; supports snapshots to S3. **EFS**: fully managed Network File System (NFS v4) that can be mounted concurrently on thousands of EC2 instances across multiple AZs; automatically scales from GB to petabytes.

---

## ⏱️ 30 Seconds

```
EBS:
  Types: gp3 (general), io2 (high IOPS), st1 (throughput), sc1 (cold)
  Size: 1GB to 64TB per volume
  IOPS: 3000–64000 (io2 Block Express)
  Scope: Single AZ, single instance (usually)
  Snapshot: incremental, stored in S3, cross-region copy

EFS:
  Protocol: NFS v4.1/v4.2
  Scope: Multi-AZ, thousands of clients simultaneously
  Performance modes: General Purpose, Max I/O
  Throughput modes: Elastic (auto), Bursting, Provisioned
  Storage classes: Standard, Infrequent Access (EFS lifecycle)

Cost comparison (us-east-1):
  EBS gp3: $0.08/GB/month
  EFS Standard: $0.30/GB/month (but pay for what you use)
  S3 Standard: $0.023/GB/month
```

---

## 🔩 First Principles

- **EBS is network storage**: attached via AWS network fabric (Nitro NVMe), not literally local; ~sub-ms latency
- **EBS is AZ-locked**: cannot attach to instance in different AZ; snapshot → restore in new AZ to move
- **EBS Multi-Attach**: io1/io2 can attach to multiple instances (same AZ) for clustered DB use cases
- **EFS is NFS**: acts like a network drive; POSIX-compatible; supports file locking
- **EFS scale**: no provisioning; grows and shrinks automatically; you pay for bytes stored
- **EBS snapshots**: incremental (only changed blocks); stored in S3; basis for AMIs

---

## 🧪 Thought Experiment

RDS (relational database) needs persistent storage: EBS io2 for high IOPS, replicated within AZ, snapshots for backup. A fleet of web servers need to share uploaded images: EFS mount point, all servers read/write same filesystem. A Lambda function needs no persistent storage (ephemeral = fine). EC2 boot volume: EBS gp3 (OS + app files). Big video transcoding pipeline: S3 for input/output; EC2 local NVMe for temp processing.

---

## 🧠 Mental Model / Analogy

**EBS** = USB drive attached to your computer: fast, works like local disk, but only one computer uses it at a time, and it's tied to your desk (AZ). **EFS** = a shared network drive (NAS) that the whole office can access simultaneously, and it expands automatically as you add files.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: EBS: create volume, attach to EC2, format, mount. EFS: create filesystem, create mount targets in subnets, mount on EC2 via NFS.

**Level 2 — Practitioner**: EBS snapshot strategy: daily snapshots via AWS Backup or Data Lifecycle Manager. EBS gp3 vs gp2: gp3 baseline 3000 IOPS + 125 MB/s independent of size ($0.08/GB); gp2 IOPS tied to size (3 IOPS/GB, burst to 3000). Migrate gp2 → gp3: zero downtime, same price, better performance. EFS lifecycle: Standard → IA after 30 days (saves 91% on storage cost for cold files).

**Level 3 — Advanced**: EBS io2: guaranteed IOPS (up to 64K), 99.999% durability (vs 99.8-99.9% for gp3). io2 Block Express: up to 256K IOPS, sub-millisecond latency, multi-attach. EBS fast snapshot restore (FSR): eliminates I/O warming on snapshot restore (for auto-scaling with snapshots). EFS provisioned throughput: for burst-heavy workloads that exhaust burst credits; set guaranteed throughput independent of data size.

**Level 4 — Expert**: EBS encryption: uses KMS; encryption at rest + in transit (Nitro instances); minimal performance impact. EBS volume modification (elastic volumes): change type, size, IOPS without detaching (hot modification). EFS Access Points: enforce POSIX user identity (UID/GID); useful for ECS tasks with different access contexts. EFS Replication: cross-region replication for DR (creates read-only replica, sub-minute RPO). EFS One Zone: single-AZ EFS at 47% lower cost; suitable for dev/test or data easily reproducible.

---

## ⚙️ How It Works

### EBS (Terraform)

```hcl
# gp3 EBS volume (modern default - better than gp2)
resource "aws_ebs_volume" "app_data" {
  availability_zone = "us-east-1a"
  size              = 100      # GB
  type              = "gp3"
  iops              = 3000     # baseline (free up to 3000)
  throughput        = 125      # MB/s (free up to 125)
  encrypted         = true
  kms_key_id        = aws_kms_key.ebs.arn

  tags = {
    Name = "app-data-volume"
  }
}

resource "aws_volume_attachment" "app" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.app_data.id
  instance_id = aws_instance.app.id
}

# Automated snapshots via Data Lifecycle Manager
resource "aws_dlm_lifecycle_policy" "ebs_backup" {
  description        = "Daily EBS snapshots"
  execution_role_arn = aws_iam_role.dlm.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]

    schedule {
      name = "daily-snapshots"

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["23:45"]
      }

      retain_rule {
        count = 7  # keep 7 days of snapshots
      }
    }

    target_tags = {
      Snapshot = "true"
    }
  }
}
```

### EFS (Terraform)

```hcl
# EFS File System
resource "aws_efs_file_system" "shared" {
  encrypted        = true
  kms_key_id       = aws_kms_key.efs.arn
  performance_mode = "generalPurpose"
  throughput_mode  = "elastic"  # auto-scales throughput

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"  # move cold files to IA
  }
  lifecycle_policy {
    transition_to_primary_storage_class = "AFTER_1_ACCESS"  # move back on access
  }

  tags = {
    Name = "shared-storage"
  }
}

# Mount targets in each AZ subnet (needed for multi-AZ access)
resource "aws_efs_mount_target" "az_a" {
  file_system_id  = aws_efs_file_system.shared.id
  subnet_id       = aws_subnet.private_a.id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_mount_target" "az_b" {
  file_system_id  = aws_efs_file_system.shared.id
  subnet_id       = aws_subnet.private_b.id
  security_groups = [aws_security_group.efs.id]
}

# EFS Access Point (POSIX identity enforcement)
resource "aws_efs_access_point" "app" {
  file_system_id = aws_efs_file_system.shared.id

  posix_user {
    uid = 1001
    gid = 1001
  }

  root_directory {
    path = "/app-data"
    creation_info {
      owner_uid   = 1001
      owner_gid   = 1001
      permissions = "755"
    }
  }
}
```

### Mount EFS on EC2

```bash
# Install NFS client
sudo yum install -y amazon-efs-utils

# Mount EFS (recommended: via DNS, TLS)
sudo mount -t efs \
  -o tls,accesspoint=fsap-xxx \
  fs-xxxxxxxx:/ /mnt/efs

# Persistent mount (/etc/fstab)
echo "fs-xxxxxxxx:/ /mnt/efs efs defaults,tls,_netdev 0 0" \
  >> /etc/fstab
```

---

## ⚖️ Comparison Table

| Feature          | EBS gp3        | EBS io2         | EFS            |
| ---------------- | -------------- | --------------- | -------------- |
| **Type**         | Block          | Block           | File (NFS)     |
| **IOPS**         | 3K-16K         | Up to 64K       | Shared         |
| **Throughput**   | 125-1000 MB/s  | Up to 4000 MB/s | Up to 10 GB/s  |
| **Cost**         | $0.08/GB       | $0.125/GB       | $0.30/GB       |
| **Multi-attach** | ❌ (usually)   | ✅ (same AZ)    | ✅ (any AZ)    |
| **AZ scope**     | Single AZ      | Single AZ       | Multi-AZ       |
| **Use case**     | OS, DB volumes | High IOPS DB    | Shared storage |

---

## ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                       |
| -------------------------------------- | --------------------------------------------------------------------------------------------- |
| "EBS works across AZs"                 | EBS is AZ-scoped; use snapshot + restore to move across AZs                                   |
| "EFS = NAS = slow"                     | EFS Elastic throughput bursts to 10 GB/s; with Provisioned throughput, consistent performance |
| "gp2 is fine, no need to migrate"      | gp3 provides same or better performance at same price; migrate immediately                    |
| "EFS charges for provisioned capacity" | EFS charges for bytes stored (pay-per-use), not provisioned capacity                          |

---

## 🔗 Related Keywords

- [S3](/cloud-aws/s3/) — object storage for files not needing POSIX semantics
- [EC2](/cloud-aws/ec2/) — EBS attaches to EC2 instances
- [RDS](/cloud-aws/rds/) — uses EBS storage under the hood

---

## 📌 Quick Reference Card

```bash
# List EBS volumes
aws ec2 describe-volumes \
  --query 'Volumes[].{Id:VolumeId,Type:VolumeType,State:State,Size:Size}'

# Create snapshot
aws ec2 create-snapshot \
  --volume-id vol-xxxxxxxx \
  --description "Pre-upgrade backup $(date +%Y%m%d)"

# Modify gp2 volume to gp3 (zero downtime)
aws ec2 modify-volume \
  --volume-id vol-xxxxxxxx \
  --volume-type gp3 \
  --iops 3000 \
  --throughput 125

# Check modification progress
aws ec2 describe-volumes-modifications \
  --volume-ids vol-xxxxxxxx

# List EFS file systems
aws efs describe-file-systems

# Check EFS mount targets
aws efs describe-mount-targets \
  --file-system-id fs-xxxxxxxx
```

---

## 🧠 Think About This

The gp2→gp3 migration is one of the simplest AWS cost optimizations with immediate impact. gp2 prices IOPS to storage size (3 IOPS/GB): a 1TB gp2 volume gets 3,000 IOPS. A 100GB gp2 gets only 300 IOPS. To get 3,000 IOPS on gp2, you need 1TB minimum — even if you're only using 100GB. gp3 decouples IOPS from size: any size gets baseline 3,000 IOPS at the same price. Run this against your entire account: `aws ec2 describe-volumes --filters Name=volume-type,Values=gp2`. Convert all gp2 → gp3 for instant 0% cost increase with up to 20% IOPS improvement for small volumes. For large volumes, gp3 can be cheaper because you're not over-provisioning size just to get IOPS.
