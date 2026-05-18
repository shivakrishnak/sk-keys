---
version: 1
layout: default
title: "Aurora"
parent: "Cloud - AWS"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/cloud-aws/aurora/
id: AWS-034
category: "Cloud - AWS"
difficulty: "★★★"
depends_on: ["RDS", "VPC", "EBS / EFS"]
used_by: ["AWS Cost Optimization"]
related: ["RDS", "DynamoDB", "ElastiCache", "AWS Cost Optimization"]
tags: [aws, aurora, rds, database, postgresql, mysql, serverless, cloud]
---

## ⚡ TL;DR

**Aurora** is AWS's cloud-native SQL engine compatible with PostgreSQL and MySQL - up to **3x faster than RDS PostgreSQL** and **5x faster than RDS MySQL**. Distributed storage (6-way replication across 3 AZs), up to 15 low-latency Read Replicas, fast failover (<30s), and **Aurora Serverless v2** (auto-scales compute from 0.5 to 128 ACUs per second). Pay more per GB than RDS, but at large scale the performance/HA characteristics make it the default choice.

---

## 🔥 Problem This Solves

RDS Multi-AZ has one readable instance + a non-readable standby + up to 5 read replicas with async replication lag. Aurora solves: standby is now readable (up to 15 replicas), replication lag is sub-10ms, failover is faster (<30s vs 60s), and Serverless v2 eliminates over-provisioning for variable workloads.

---

## 📘 Textbook Definition

Amazon Aurora is a MySQL- and PostgreSQL-compatible relational database engine that combines the speed and availability of high-end commercial databases with the simplicity and cost-effectiveness of open-source databases. Aurora's storage layer replicates data 6 ways across 3 AZs automatically. The writer instance and up to 15 read replicas share the same storage cluster.

---

## ⏱️ 30 Seconds

```
Aurora Architecture:
  Shared distributed storage: 6 copies across 3 AZs
  Writer endpoint: routes to primary writer
  Reader endpoint: load-balances across read replicas
  Up to 15 read replicas (shared storage = sub-10ms lag)
  Auto-failover: <30s (replica promoted, storage unchanged)

Aurora Serverless v2:
  Scale unit: Aurora Capacity Units (ACUs); 1 ACU = ~2GB
    RAM
  Min: 0.5 ACU; Max: 128 ACU
  Scales incrementally in 0.5 ACU steps
  Billing: per ACU-second (pay for actual usage)

Storage: $0.10/GB/month (auto-grows in 10GB increments)
I/O: $0.20/million requests (or Aurora I/O Optimized: flat
  storage+I/O rate)
```

---

## 🔩 First Principles

- **Shared storage**: all instances (writer + replicas) read from same storage layer; no data copying during replication
- **6-way replication**: 6 storage nodes across 3 AZs; tolerates loss of 2 nodes without data loss; writes succeed with 4/6 quorum
- **Fast failover**: no data to copy at failover; replica just takes over as writer in same shared storage
- **Aurora Serverless v2**: compute scales with load; storage scales independently; can be mixed (serverless + provisioned replicas)
- **Aurora I/O Optimized**: pricing model for I/O-heavy workloads; no per-I/O charge, just higher storage price (~2.25x)

---

## 🧪 Thought Experiment

SaaS product with variable load: minimal during weekdays, spikes on Monday mornings and end-of-quarter. Traditional RDS: size for peak (expensive), idle rest of time. Aurora Serverless v2: 0.5 ACU at off-peak ($0.0065/ACU-hr × 0.5 = ~$0.003/hr), scales to 32 ACU during peak (auto, ~5s to scale). No manual instance class changes. Compare: db.r7g.large always-on = $0.29/hr; Aurora Serverless v2 = ~$0.05/hr average for variable workload.

---

## 🧠 Mental Model / Analogy

Traditional RDS = single hard drive attached to a server (EBS). Aurora = **shared SAN (Storage Area Network)** that multiple servers plug into: all instances see the same data instantly, failover is just "the other server takes control of the SAN." This explains why Aurora replication lag is sub-10ms (no data to send) and failover is faster (no data to copy to standby).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create Aurora PostgreSQL cluster. Two endpoints: Writer Endpoint for writes, Reader Endpoint for reads. Multi-AZ by default. Add read replicas in minutes (shared storage: no data copy needed).

**Level 2 - Practitioner**: Aurora Serverless v2: set min/max ACUs, let AWS scale compute automatically. Aurora Global Database: cross-region replication with ~1s replication lag for DR or read proximity. Aurora clones: instant copy of production database for dev/test (copy-on-write, $0 additional storage until changes diverge).

**Level 3 - Advanced**: Aurora Parallel Query: offloads query execution to storage layer (eliminate pushing 100GB to compute for analytics). Aurora Data API (Serverless): HTTP API to Aurora without connection pool management (useful for Lambda without RDS Proxy). Aurora Machine Learning integration: call SageMaker/Comprehend from SQL functions. Blue-green deployment: AWS manages replica + switchover for zero-downtime upgrades.

**Level 4 - Expert**: Aurora storage internals: redo log segments written to 6 storage nodes; background thread reconstructs page cache from redo log on demand (no dirty page flushing). Aurora storage quorum: write succeeds when 4/6 nodes acknowledge; read quorum: 3/6. Aurora write-forwarding: read replicas can accept writes and forward to writer (reduces connection management). Monitoring: AuroraReplicaLag CloudWatch metric (alert if >100ms means read replica falling behind). Aurora I/O Optimized pricing crossover: if I/O costs exceed 25% of total Aurora bill, I/O Optimized is cheaper - check via Cost Explorer.

---

## ⚙️ How It Works

---

### Aurora Cluster (Terraform)

```hcl
# Aurora PostgreSQL Cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier      = "main-aurora"
  engine                  = "aurora-postgresql"
  engine_version          = "15.4"
  database_name           = "appdb"
  master_username         = "dbadmin"

  # Credentials managed by AWS Secrets Manager
  manage_master_user_password = true

  # Networking
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]

  # Storage
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.aurora.arn

  # Backups
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"

  # Enable Data API (for Aurora Serverless)
  enable_http_endpoint    = true

  # Deletion protection
  deletion_protection     = true
  skip_final_snapshot     = false
  final_snapshot_identifier = "main-aurora-final"

  tags = {
    Environment = "prod"
  }
}

# Serverless v2 Writer + Reader
resource "aws_rds_cluster_instance" "writer" {
  identifier         = "main-aurora-writer"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"  # Aurora Serverless v2
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn
}

resource "aws_rds_cluster_instance" "reader" {
  identifier         = "main-aurora-reader-1"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  performance_insights_enabled = true
}

# Serverless v2 scaling configuration
resource "aws_rds_cluster" "main" {
  # ... (same as above) ...

  serverlessv2_scaling_configuration {
    min_capacity = 0.5   # 0.5 ACU minimum (cost-efficient)
    max_capacity = 32    # 32 ACU maximum (~64GB RAM)
  }
}
```

---

### Aurora Global Database (Multi-Region DR)

```hcl
# Primary region cluster (us-east-1)
resource "aws_rds_global_cluster" "main" {
  global_cluster_identifier = "my-global-db"
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
  database_name             = "appdb"
  storage_encrypted         = true
}

resource "aws_rds_cluster" "primary" {
  # ... in us-east-1
  global_cluster_identifier = aws_rds_global_cluster.main.id
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
}

# Secondary region cluster (eu-west-1)
# This cluster replicates from primary with ~1s lag
resource "aws_rds_cluster" "secondary" {
  provider = aws.eu_west_1

  global_cluster_identifier = aws_rds_global_cluster.main.id
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
  # No master_username/password on secondary
}
```

---

### Spring Boot Connection to Aurora (Reader/Writer)

```yaml
# application.yml - separate read/write datasources
spring:
  datasource:
    url: jdbc:postgresql://${AURORA_WRITER_ENDPOINT}:5432/appdb
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20

  # Read replica for read-heavy operations
  read-datasource:
    url: jdbc:postgresql://${AURORA_READER_ENDPOINT}:5432/appdb
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 40 # more connections to reader
```

```java
// Route reads to replica, writes to writer
@Service
public class UserRepository {

    @Autowired
    @Qualifier("writeDataSource")
    private DataSource writeDataSource;

    @Autowired
    @Qualifier("readDataSource")
    private DataSource readDataSource;

    @Transactional  // uses write datasource
    public User save(User user) {
        // write operation → writer endpoint
    }

    @Transactional(readOnly = true)  // can route to reader
    public Optional<User> findById(Long id) {
        // read operation → reader endpoint
    }
}
```

---

## ⚖️ Comparison Table: Aurora vs RDS PostgreSQL

| Feature             | Aurora PostgreSQL            | RDS PostgreSQL             |
| ------------------- | ---------------------------- | -------------------------- |
| **Performance**     | Up to 3x faster              | Baseline                   |
| **Read Replicas**   | 15 (sub-10ms lag)            | 5 (async, variable lag)    |
| **Failover Time**   | <30s                         | 30-60s                     |
| **Serverless**      | ✅ Serverless v2             | ❌                         |
| **Storage**         | Auto-grows, 6-way replicated | EBS, manual management     |
| **Global DB**       | ✅ (~1s cross-region)        | ✅ Cross-region RR         |
| **Price (storage)** | $0.10/GB                     | $0.115/GB (gp3)            |
| **Price (compute)** | Same instance classes        | Same instance classes      |
| **Extensions**      | Most PostgreSQL extensions   | Most PostgreSQL extensions |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| "Aurora is expensive vs RDS"        | Same compute price; storage slightly higher; but operational benefits often justify it                        |
| "Serverless v2 can scale to zero"   | Serverless v2 minimum is 0.5 ACU (not zero); Aurora Serverless v1 could scale to zero but is being deprecated |
| "All 15 read replicas help equally" | Reader Endpoint load-balances; but reader lag can vary - check AuroraReplicaLag metric                        |
| "Aurora = PostgreSQL extensions"    | Some extensions aren't available; verify `aws rds describe-db-engine-versions` for supported extensions       |

---

## 🔗 Related Keywords

- [RDS](/cloud-aws/rds/) - standard managed SQL databases
- [DynamoDB](/cloud-aws/dynamodb/) - NoSQL for different use case
- [ElastiCache](/cloud-aws/elasticache/) - caching in front of Aurora

---

## 📌 Quick Reference Card

```bash
# List Aurora clusters
aws rds describe-db-clusters \
  --query 'DBClusters[].{Id:DBClusterIdentifier,Engine:Engine,
      Status:Status,Endpoint:Endpoint}'

# Get cluster endpoints
aws rds describe-db-clusters \
  --db-cluster-identifier my-cluster \
  --query 'DBClusters[0].{Writer:Endpoint,Reader:ReaderEndpoint}'

# Check replica lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name AuroraReplicaLag \
  --dimensions Name=DBClusterIdentifier,Value=my-cluster \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 300 \
  --statistics Average

# Create Aurora clone (instant, cheap dev copy)
aws rds restore-db-cluster-to-point-in-time \
  --db-cluster-identifier dev-clone \
  --source-db-cluster-identifier my-cluster \
  --restore-type copy-on-write \
  --use-latest-restorable-time
```

---

## 🧠 Think About This

Aurora's shared storage model fundamentally changes the economics of read scaling. With RDS PostgreSQL, each read replica receives a full async replication stream, has its own EBS volume, and replication lag can grow under heavy write loads. With Aurora, all 15 read replicas share the same storage - "replication" is actually just cache invalidation signals (the replicas are already reading from the same 6-way storage layer). This makes Aurora read replicas instantly consistent (sub-10ms lag vs potentially seconds for RDS), and adding a read replica takes minutes vs hours for RDS (no data to copy). For read-heavy workloads (product catalogs, user dashboards, reporting), this changes the architecture: you can add Aurora read replicas aggressively, use the Reader Endpoint for load balancing, and trust that replica lag won't silently serve stale data.
