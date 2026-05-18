---
version: 1
layout: default
title: "EC2 Instance Types"
parent: "Cloud - AWS"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/cloud-aws/ec2-instance-types/
id: AWS-028
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on: ["EC2"]
used_by: ["Auto Scaling Groups", "EKS", "ECS / Fargate"]
related: ["EC2", "Spot Instances / Reserved Instances", "K8s Cost Optimization"]
tags: [aws, ec2, instance-types, compute, graviton, gpu, cpu, cloud]
---

## ⚡ TL;DR

EC2 instance types follow the pattern `family.size` (e.g., `m7g.xlarge`). **Families**: General Purpose (m/t), Compute Optimized (c), Memory Optimized (r/x), Storage Optimized (i/d), Accelerated (p/g/inf/trn). **Generation**: higher = newer/better (5, 6, 7). **Processor**: default=Intel, `g`=AMD Graviton (ARM), `a`=AMD EPYC. Graviton3 (m7g) = best price/performance for most workloads.

---

## 🔥 Problem This Solves

Different workloads have different bottlenecks: a CPU-bound batch job needs more vCPUs, a Java heap cache needs 128GB RAM, a Redis cluster needs fast NVMe, a ML training job needs GPUs. Instance type selection matches hardware to workload, maximizing performance per dollar.

---

## 📘 Textbook Definition

EC2 instance types define the hardware configuration (vCPU, memory, network performance, storage) available to an instance. They are grouped into families optimized for different use cases, with each family having multiple sizes offering more CPU/memory while maintaining the same family characteristics.

---

## ⏱️ 30 Seconds

```
Instance type naming:
  [family][generation][processor].[size]
  m7g.xlarge
  ^  = General Purpose
   ^ = 7th generation
    ^ = Graviton (ARM)
       ^^^^^^ = xlarge (4 vCPU, 16GB)

Sizes: nano < micro < small < medium < large < xlarge <
  2xlarge ... 48xlarge

Common families:
  t3/t4g  General Purpose burstable     (dev, low-traffic)
  m6i/m7g General Purpose balanced      (web servers, app
    servers)
  c6i/c7g Compute Optimized             (CPU-heavy batch,
    gaming)
  r6i/r7g Memory Optimized              (Redis, Kafka,
    Java heap)
  p4/p5   GPU (NVIDIA)                  (ML training)
  i4i/i3  Storage Optimized NVMe        (Cassandra,
    MongoDB)
```

---

## 🔩 First Principles

- **vCPU**: virtual CPU (2 per physical core with hyperthreading)
- **Memory**: DRAM allocated to instance
- **Network bandwidth**: up to 25/50/100 Gbps depending on instance size
- **EBS bandwidth**: separate from network; larger instances have higher EBS throughput
- **Instance store**: ephemeral NVMe SSDs (i family) - data lost on stop; use for temp data
- **Graviton (ARM)**: AWS-designed ARM CPU; 40% better price/performance vs x86 for many workloads

---

## 🧪 Thought Experiment

You have a Java Spring Boot API with 512MB heap that's CPU-bound. Current: m5.xlarge (4 vCPU, 16GB RAM, $0.192/hr). CPU: 70%, Memory: 5GB used (31% of 16GB). Right-sizing: c7g.medium (1 vCPU, 2GB Graviton3, $0.036/hr) → no, too little CPU. Try c7g.large (2 vCPU, 4GB, $0.0725/hr) → CPU: 50%, RAM: 60% → better fit at 62% cost savings.

---

## 🧠 Mental Model / Analogy

EC2 instance types are like **tool sizes at a workshop**: a hand drill (t3.micro) for small jobs, a workbench drill press (m5.large) for general work, a lathe (c5.4xlarge) for precision heavy cutting, a forklift (r5.8xlarge) for moving heavy loads, a CNC machine (p4d.24xlarge with GPUs) for complex manufacturing. Choosing the wrong tool = inefficiency; right tool = fast + cheap.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: t3.micro for dev/test (burstable). m5.large or m7g.large for production web servers. Check AWS calculator for pricing.

**Level 2 - Practitioner**: Profile your workload: CPU-bound → c family; memory-bound → r family; balanced → m family. Graviton (g suffix) for 20-40% cost savings on Linux workloads. Use EC2 Compute Optimizer recommendations.

**Level 3 - Advanced**: Burstable (t3): earn CPU credits during idle; spend on bursts. Sustained T3 unlimited mode: can burst indefinitely but charged for sustained credits. For latency-sensitive production: avoid t3 (variable CPU). Enhanced Networking (ENA): all modern instances; up to 100 Gbps. Elastic Fabric Adapter (EFA): RDMA-like networking for HPC/MPI workloads.

**Level 4 - Expert**: Graviton vs x86: Graviton3 (m7g, c7g, r7g) use custom ARMv8.2+ cores; 40% better perf/watt. Most Java, Python, Node.js apps run natively on ARM with no changes (check Docker images: use `linux/arm64` or multi-arch). AMD (a suffix: m6a, c6a): competitive with Intel at lower price; good alternative to Graviton on x86. NVMe instance store: i3en.xlarge has 2.5TB NVMe at 2.4 GB/s read; 10x EBS throughput for database scratch space. Nitro System: custom hardware (Nitro cards) for NVMe, networking, and security - allows bare-metal performance on virtualized instances.

---

## ⚙️ How It Works

---

### Instance Family Reference

```
GENERAL PURPOSE:
  t3/t4g  Burstable: 2-8 vCPU, 0.5-32GB  Dev, low traffic
           t4g = Graviton2; t3 = Intel
  m5/m6i  Intel:     2-96 vCPU             Web, app servers
  m6g/m7g Graviton:  2-64 vCPU             Best price/perf
    for web

COMPUTE OPTIMIZED:
  c5/c6i  Intel:     2-96 vCPU             CPU-heavy
    batch, gaming
  c6g/c7g Graviton:  2-64 vCPU             Best price/perf
    for CPU

MEMORY OPTIMIZED:
  r5/r6i  Intel:     2-96 vCPU, up to 768GB  In-memory DB,
    caches
  r6g/r7g Graviton:  2-64 vCPU, up to 512GB  Redis, Kafka,
    large heaps
  x2idn   Intel:     32-128 vCPU, up to 2TB  In-memory
    analytics
  u-*     Ultra high memory: 3.8-24TB          SAP HANA

STORAGE OPTIMIZED:
  i3      Intel NVMe:  2-64 vCPU, up to 60TB  Cassandra,
    MongoDB
  i4i     Intel NVMe:  2-96 vCPU              High IOPS
    databases
  d3      HDD dense:   4-48 vCPU, up to 336TB  Hadoop,
    data lakes

ACCELERATED COMPUTING:
  p4d     NVIDIA A100 (8x per instance)    ML training
  p5      NVIDIA H100 (8x per instance)    Large model
    training
  g4dn    NVIDIA T4 (1-8x per instance)    ML inference,
    gaming
  inf2    AWS Inferentia2                   ML inference
    (cheaper)
  trn1    AWS Trainium                      ML training
    (cheaper)
```

---

### Picking the Right Instance

```
Workload Analysis Checklist:
  1. CPU utilization: >70% sustained → need more vCPUs
  2. Memory utilization: >70% → need more RAM
  3. Network bandwidth: check Mbps used vs instance limits
  4. Storage IOPS: for DB workloads, check EBS vs NVMe
  5. Architecture: can app run on ARM? → try Graviton

Rule of thumb:
  - Generic Java API:        m7g.large  ($0.0808/hr)
  - Heavy CPU batch:         c7g.xlarge ($0.1448/hr)
  - Redis/Kafka:             r7g.xlarge ($0.2016/hr)
  - ML inference:            inf2.xlarge ($0.7582/hr)

Use AWS Compute Optimizer:
  aws compute-optimizer get-ec2-instance-recommendations
```

---

### Graviton Migration for Spring Boot

```dockerfile
# Multi-arch Docker image (supports both x86 and ARM)
FROM --platform=$BUILDPLATFORM maven:3.9-amazoncorretto-17 AS builder
ARG TARGETPLATFORM
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:resolve
COPY src ./src
RUN mvn package -DskipTests

FROM amazoncorretto:17-al2023
# Works on both x86 (amd64) and ARM (arm64/Graviton)
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```bash
# Build multi-arch
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t myrepo/myapp:latest .

# Test on Graviton (m7g instance or locally with QEMU)
docker run --platform linux/arm64 myrepo/myapp:latest
```

---

## ⚖️ Comparison Table: Common Production Choices

| Workload       | Recommended | vCPU | GB RAM | $/hr    |
| -------------- | ----------- | ---- | ------ | ------- |
| Dev/test       | t3.medium   | 2    | 4      | $0.042  |
| Web server     | m7g.large   | 2    | 8      | $0.0808 |
| Heavy API      | m7g.xlarge  | 4    | 16     | $0.1616 |
| CPU batch      | c7g.xlarge  | 4    | 8      | $0.1448 |
| Redis          | r7g.large   | 2    | 16     | $0.1008 |
| Kafka broker   | r7g.xlarge  | 4    | 32     | $0.2016 |
| Cassandra node | i4i.xlarge  | 4    | 32     | $0.378  |

_Prices approximate us-east-1 on-demand_

---

## ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                    |
| -------------------------------------------- | ------------------------------------------------------------------------------------------ |
| "More vCPUs always better"                   | Wrong family costs more; often memory or IOPS is the bottleneck                            |
| "Graviton = for AI only"                     | Graviton is for all workloads; Java/Python/Node.js benefit significantly                   |
| "t3 is fine for production"                  | t3 burstable CPU is unpredictable under sustained load; use m/c for consistent performance |
| "Newer generation is only marginally better" | Gen 6→7 Graviton: 25% better compute perf, 2x crypto performance                           |

---

## 🔗 Related Keywords

- [EC2](/cloud-aws/ec2/) - EC2 overview
- [Auto Scaling Groups](/cloud-aws/auto-scaling-groups/) - scale instance count
- [Spot Instances / Reserved Instances](/cloud-aws/spot-instances-reserved-instances/) - cost optimization for instance types
- [K8s Cost Optimization](/kubernetes/k8s-cost-optimization/) - choosing instance types for EKS nodes

---

## 📌 Quick Reference Card

```bash
# List instance types in a region
aws ec2 describe-instance-types \
  --filters Name=current-generation,Values=true \
  --query 'InstanceTypes[].{Type:InstanceType,
      vCPU:VCpuInfo.DefaultVCpus,Memory:MemoryInfo.SizeInMiB}' \
  --output table | sort

# Get Compute Optimizer recommendations
aws compute-optimizer get-ec2-instance-recommendations \
  --account-ids $(
      aws sts get-caller-identity --query Account --output text)

# Check instance type availability in AZ
aws ec2 describe-instance-type-offerings \
  --location-type availability-zone \
  --filters Name=instance-type,Values=m7g.xlarge

# Compare instance prices (pricing API)
aws pricing get-products \
  --service-code AmazonEC2 \
  --filters Type=TERM_MATCH,Field=instanceType,Value=m7g.xlarge \
            Type=TERM_MATCH,Field=location,
                Value="US East (N. Virginia)" \
            Type=TERM_MATCH,Field=operatingSystem,Value=Linux
```

---

## 🧠 Think About This

The Graviton3 instance generation (`m7g`, `c7g`, `r7g`) represents one of the best cost optimization opportunities in AWS today - often overlooked because "AWS-designed ARM chip" sounds risky. In practice: Java runs natively on ARM with no changes; the JVM, Spring Boot, and all major Java libraries support ARM64. Amazon itself runs most of its internal services on Graviton. The steps to evaluate: (1) check your Docker images support `linux/arm64` or use multi-arch builds, (2) launch a test m7g instance in staging, (3) run your performance tests. If performance is equivalent (it often exceeds x86 for CPU-intensive work), the 20-40% cost reduction translates directly to budget savings with zero architectural change. EC2 Compute Optimizer provides data-driven recommendations for free.
