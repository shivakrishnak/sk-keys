---
layout: default
title: "RDS"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /cloud-aws/rds/
id: AWS-045
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on:
  ["VPC", "Subnets (Public / Private)", "Security Groups", "EBS / EFS"]
used_by: ["Aurora", "AWS Cost Optimization"]
related: ["Aurora", "DynamoDB", "ElastiCache", "EBS / EFS"]
tags: [aws, rds, relational-database, postgres, mysql, database, cloud]
---

# RDS

## ⚡ TL;DR

**RDS (Relational Database Service)** is managed SQL database hosting. Supports PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, and Db2. AWS handles: OS patching, backups, replication, failover, and scaling. Multi-AZ deployment: synchronous replication, automatic failover in ~30-60s. Read Replicas: async replication for read scaling. Use RDS instead of running your own DB on EC2 unless you need specific extensions or control.

---

## 🔥 Problem This Solves

Running a PostgreSQL server on EC2 means: OS updates, pg_upgrade, WAL archiving, backup automation, standby replication, failover scripting, monitoring. RDS abstracts all of that. You get a managed endpoint; AWS handles operational tasks. You focus on queries and schema, not database administration.

---

## 📘 Textbook Definition

Amazon RDS is a managed relational database service that provides cost-efficient, resizable capacity for standard relational databases. RDS automates common database administration tasks including hardware provisioning, database setup, patching, backups, and recovery. Supported engines: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Db2.

---

## ⏱️ 30 Seconds

```
RDS instance:
  Instance class:  db.t3.micro (dev) → db.r7g.32xlarge (prod)
  Storage:         gp3 or io1/io2 EBS; autoscaling available
  Endpoint:        DB hostname (DNS round-robin Multi-AZ)

Multi-AZ:
  Primary → synchronous replication → Standby (different AZ)
  Failover: ~30-60s; DNS automatically updated
  Standby: NOT readable (use Read Replicas for reads)

Read Replicas:
  Async replication; add up to 5 per instance
  Readable endpoint; good for analytics/reporting
  Can be promoted to standalone DB
  Can be in different region (cross-region RR)
```

---

## 🔩 First Principles

- **Managed != fully managed**: you still choose instance size, storage, and manage schema/queries
- **Multi-AZ vs Read Replica**: Multi-AZ = HA/DR (standby not readable); Read Replica = read scaling (readable, async)
- **DB Subnet Group**: RDS requires subnets across ≥2 AZs defined as a DB Subnet Group
- **Parameter groups**: configure DB engine settings (e.g., max_connections, work_mem for PostgreSQL)
- **IAM database auth**: for supported engines, use IAM role instead of password (token-based, 15-min tokens)
- **Enhanced Monitoring**: OS-level metrics with 1s granularity (separate from CloudWatch)

---

## 🧪 Thought Experiment

E-commerce app. Primary PostgreSQL handles writes. Two read replicas handle product search and reporting queries. Multi-AZ standby for HA. Connection pooling via RDS Proxy (handles thousands of Lambda connections without overwhelming DB). Automated backups (7 days retention). Performance Insights reveals a missing index causing slow ORDER queries → add index without downtime.

---

## 🧠 Mental Model / Analogy

RDS is **managed hosting for your database**: like renting a managed server with a dedicated database administrator. You tell AWS "I need PostgreSQL 15, this size, these settings" and AWS installs it, keeps it patched, backs it up nightly, and handles failover. You're still the chef (schema, queries, data); AWS is the kitchen manager (infrastructure, operations).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create RDS instance in private subnet. Connect from EC2 in same VPC via security group rule. Enable automated backups (retention 7-35 days). Create read replica for reporting queries.

**Level 2 - Practitioner**: Enable Multi-AZ for production. Use RDS Proxy for connection pooling (critical for Lambda → RDS). Enable Performance Insights (1-week free, paid for longer). Storage Auto Scaling: set max storage, RDS scales up automatically when 10% free space remains. IAM database authentication.

**Level 3 - Advanced**: Read Replica promotion: create cross-region read replica → promote for DR scenario (RPO=replication lag, RTO=promotion time ~minutes). Point-in-time recovery (PITR): restore to any second within backup retention period. RDS Proxy: manages connection pool, reduces failover impact from 30-60s to ~5s (proxy maintains connections through failover). Custom Parameter Groups: tune PostgreSQL performance (shared_buffers, effective_cache_size, work_mem).

**Level 4 - Expert**: RDS Optimized Reads (local NVMe SSD): instances with local storage cache read-heavy workloads (db.r6gd instances). Graviton-based instances (db.r7g): 20-35% better price/performance for PostgreSQL/MySQL. Blue-green deployments: RDS creates replica, you test against it, then promote (zero-downtime major version upgrades). pg_logical replication: replicate from RDS PostgreSQL to external destinations. Aurora Migration: convert RDS PostgreSQL → Aurora PostgreSQL using logical replication (near-zero downtime). Multi-AZ cluster (RDS): 1 writer + 2 readable standbys (PostgreSQL); readable standbys + automatic failover in <35s.

---

## ⚙️ How It Works

### RDS Provisioning (Terraform)

```hcl
# DB Subnet Group (required)
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "main-db-subnet-group"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier        = "main-postgres"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.r7g.large"     # Graviton3

  # Storage
  allocated_storage     = 100
  max_allocated_storage = 1000            # storage autoscaling
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  # Credentials (use Secrets Manager, not hardcode)
  manage_master_user_password = true      # RDS manages in Secrets Manager
  username                    = "dbadmin"

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false          # NEVER public

  # Availability
  multi_az = true

  # Backups
  backup_retention_period   = 7           # days
  backup_window             = "03:00-04:00"
  maintenance_window        = "sun:04:00-sun:05:00"
  delete_automated_backups  = false
  deletion_protection       = true        # prevent accidental deletion
  skip_final_snapshot       = false
  final_snapshot_identifier = "main-postgres-final-${formatdate("YYYYMMDD", timestamp())}"

  # Performance
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60   # Enhanced Monitoring
  monitoring_role_arn                   = aws_iam_role.rds_monitoring.arn

  # Parameters
  parameter_group_name = aws_db_parameter_group.postgres.name

  tags = {
    Environment = "prod"
  }
}

# PostgreSQL parameter group tuning
resource "aws_db_parameter_group" "postgres" {
  family = "postgres15"
  name   = "custom-postgres15"

  parameter {
    name  = "shared_buffers"        # 25% of RAM for db.r7g.large (16GB)
    value = "4000000"               # in 8KB blocks = ~32GB; capped to instance RAM
    apply_method = "pending-reboot"
  }
  parameter {
    name  = "work_mem"
    value = "65536"                 # 64MB per sort operation
    apply_method = "immediate"
  }
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"                  # log queries >1s
    apply_method = "immediate"
  }
  parameter {
    name  = "log_connections"
    value = "1"
    apply_method = "immediate"
  }
}

# Read Replica (async)
resource "aws_db_instance" "read_replica" {
  identifier             = "main-postgres-replica"
  replicate_source_db    = aws_db_instance.main.identifier
  instance_class         = "db.r7g.large"
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]

  performance_insights_enabled = true
  skip_final_snapshot          = true
}
```

### RDS Proxy (Connection Pooling for Lambda)

```hcl
resource "aws_db_proxy" "main" {
  name                   = "main-proxy"
  debug_logging          = false
  engine_family          = "POSTGRESQL"
  idle_client_timeout    = 1800
  require_tls            = true
  role_arn               = aws_iam_role.rds_proxy.arn
  vpc_security_group_ids = [aws_security_group.rds.id]
  vpc_subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  auth {
    auth_scheme = "SECRETS"
    iam_auth    = "REQUIRED"   # require IAM auth (no password in Lambda)
    secret_arn  = aws_secretsmanager_secret.rds.arn
  }
}

resource "aws_db_proxy_default_target_group" "main" {
  db_proxy_name = aws_db_proxy.main.name

  connection_pool_config {
    max_connections_percent      = 90
    max_idle_connections_percent = 50
    connection_borrow_timeout    = 120
  }
}
```

### Spring Boot RDS Connection

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://${RDS_ENDPOINT}:5432/${DB_NAME}
    username: ${DB_USER}
    password: ${DB_PASSWORD} # prefer Secrets Manager injection
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

---

## ⚖️ Comparison Table: RDS vs Aurora vs Self-Managed

|                   | RDS PostgreSQL     | Aurora PostgreSQL   | Self-Managed EC2   |
| ----------------- | ------------------ | ------------------- | ------------------ |
| **Management**    | Managed            | Fully managed       | Manual             |
| **Performance**   | Standard           | 3x vs RDS           | Variable           |
| **Failover**      | 30-60s             | <30s                | Manual             |
| **Read Replicas** | 5 (async)          | 15 (sub-10ms lag)   | Manual             |
| **Cost**          | ~$0.29/hr (r7g.lg) | ~$0.29/hr + storage | $0.20/hr EC2 + ops |
| **Scaling**       | Vertical (restart) | Serverless v2 auto  | Manual             |
| **Extensions**    | Standard           | Standard            | Anything           |

---

## ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                              |
| ----------------------------------------- | ------------------------------------------------------------------------------------ |
| "Multi-AZ standby is readable"            | Multi-AZ standby is NOT readable; use Read Replicas for reads                        |
| "Bigger instance = faster queries"        | More RAM helps, but missing indexes/inefficient queries won't be fixed by scaling up |
| "RDS automatic backups are always 7 days" | Default is 7 days but configurable 0-35 days; 0 disables backups                     |
| "Read replica lag is zero"                | Async replication; lag can be milliseconds to seconds under heavy write load         |

---

## 🔗 Related Keywords

- [Aurora](/cloud-aws/aurora/) - cloud-native SQL with better performance and scaling
- [DynamoDB](/cloud-aws/dynamodb/) - NoSQL alternative
- [ElastiCache](/cloud-aws/elasticache/) - cache layer in front of RDS
- [EBS / EFS](/cloud-aws/ebs-efs/) - RDS uses EBS storage

---

## 📌 Quick Reference Card

```bash
# List RDS instances
aws rds describe-db-instances \
  --query 'DBInstances[].{Id:DBInstanceIdentifier,Engine:Engine,Class:DBInstanceClass,Status:DBInstanceStatus}'

# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier my-db \
  --db-snapshot-identifier my-db-snapshot-$(date +%Y%m%d)

# Restore to point in time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier my-db \
  --target-db-instance-identifier my-db-restored \
  --restore-time 2024-01-15T12:00:00Z

# Failover (test Multi-AZ)
aws rds reboot-db-instance \
  --db-instance-identifier my-db \
  --force-failover

# Check Performance Insights
aws pi get-resource-metrics \
  --service-type RDS \
  --identifier db-XXXXXXXX \
  --metric-queries '[{"Metric":"db.load.avg"}]' \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period-in-seconds 60
```

---

## 🧠 Think About This

The most common RDS scaling mistake: vertical scaling (bigger instance) instead of query optimization. When you see high CPU or slow queries in Performance Insights, the instinct is to upgrade the instance class. But a single missing index can turn a 30-second full table scan into a 2ms index lookup. Before scaling vertically, spend 30 minutes in Performance Insights → Top SQL → identify the top 5 queries by total time → check their execution plans. Add appropriate indexes. This is free and often a 10-100x improvement. Vertical scaling buys time but not a fix - the bad queries will slow down the bigger instance too, just later. RDS Performance Insights is one of the most underused AWS features; the "Top SQL" view alone is worth enabling on every production RDS instance.
