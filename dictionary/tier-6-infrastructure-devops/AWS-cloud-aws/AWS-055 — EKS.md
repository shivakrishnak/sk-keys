---
layout: default
title: "EKS"
parent: "Cloud — AWS"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /cloud-aws/eks/
id: AWS-055
category: "Cloud — AWS"
difficulty: "★★★"
depends_on:
  ["Kubernetes", "VPC", "IAM (Identity and Access Management)", "ECS / Fargate"]
used_by: ["AWS Cost Optimization", "AWS Security Best Practices"]
related:
  ["ECS / Fargate", "ELB / ALB / NLB", "Auto Scaling Groups", "CloudWatch"]
tags: [aws, eks, kubernetes, k8s, container, orchestration, cloud]
---

# EKS

## ⚡ TL;DR

**EKS (Elastic Kubernetes Service)** is AWS's managed Kubernetes control plane. AWS manages etcd, API server, controller manager. You manage worker nodes (EC2 Node Groups or Fargate profiles) and Kubernetes workloads. EKS is the choice when you need the Kubernetes ecosystem (Helm, Argo, Istio), have existing K8s expertise, or need portability. Key integrations: IRSA (IAM roles for service accounts), Karpenter (node autoscaling), AWS Load Balancer Controller.

---

## 🔥 Problem This Solves

Running self-managed Kubernetes: install kubeadm, configure etcd cluster, upgrade control plane, manage certificates, set up HA. EKS: managed control plane with 99.95% SLA. You focus on workloads, not infrastructure. AWS handles K8s upgrades, etcd backups, API server HA across 3 AZs.

---

## 📘 Textbook Definition

Amazon EKS is a managed Kubernetes service that runs the Kubernetes control plane across multiple AWS availability zones, automatically detects and replaces unhealthy control plane nodes, and provides automated version upgrades and patching. EKS integrates deeply with AWS services: VPC networking, IAM auth, ECR, ELB, EFS, CloudWatch.

---

## ⏱️ 30 Seconds

```
EKS components:
  Control plane: managed by AWS ($0.10/hr per cluster)
  Worker nodes: EC2 Node Groups or Fargate profiles (you pay for EC2/Fargate)

Node Group options:
  Managed Node Group: AWS-managed EC2 ASG with K8s labels/taints
  Self-managed Node Group: you manage ASG
  Fargate Profile: serverless pods (no EC2 management)
  Karpenter: node provisioner (faster than Cluster Autoscaler)

Key AWS integrations:
  IRSA: IAM Roles for Service Accounts (pod-level AWS permissions)
  AWS LB Controller: ALB/NLB from K8s Ingress/Service
  EBS CSI: persistent volumes from EBS
  EFS CSI: shared persistent volumes from EFS
  Karpenter: intelligent node provisioning
```

---

## 🔩 First Principles

- **Control plane = AWS managed**: you cannot SSH into control plane nodes; AWS handles HA, upgrades
- **Data plane = your responsibility**: worker nodes, OS patching, capacity, networking
- **IRSA (IAM Roles for Service Accounts)**: replaces node-level IAM roles; pods get fine-grained IAM via projected service account tokens → STS AssumeRoleWithWebIdentity
- **VPC CNI**: AWS VPC CNI assigns pod real VPC IP addresses; pods are first-class VPC citizens (security groups work at pod level)
- **aws-auth ConfigMap / EKS Access Entries**: maps IAM users/roles to Kubernetes RBAC groups

---

## 🧪 Thought Experiment

Java Spring Boot microservices at company with existing K8s expertise. Choose EKS: teams already know kubectl/Helm; Argo CD already in place; need Istio for mTLS between services; Karpenter provisions right-sized nodes. Pods use IRSA for S3/DynamoDB access (no node-level over-permissions). AWS LB Controller creates ALB for Ingress. Result: AWS manages the boring parts; K8s ecosystem for the productive parts.

---

## 🧠 Mental Model / Analogy

EKS is like **leasing a managed office building (control plane)** while you furnish and run the offices (worker nodes and workloads). Building management (AWS) handles: electrical, plumbing, security, maintenance, and building upgrades. You handle: office furniture, staff, and business operations. You get all the Kubernetes capabilities with reduced operational overhead for the infrastructure layer.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Create EKS cluster. Add managed node group. Configure kubectl with `aws eks update-kubeconfig`. Deploy pods, services, deployments.

**Level 2 — Practitioner**: IRSA: create IAM role with service account annotation, pods assume role (no access keys in pods). AWS LB Controller: Ingress resource creates ALB. Karpenter: install via Helm, configure NodePool and EC2NodeClass, remove Cluster Autoscaler. Managed add-ons: CoreDNS, kube-proxy, VPC CNI managed and updated by AWS.

**Level 3 — Advanced**: EKS Fargate Profiles: run specific pods serverlessly (no node management); useful for low-throughput services. EKS Blueprints: IaC templates for production-ready EKS with batteries included (GitOps, monitoring, security). Pod Security Standards (PSS): enforce pod security via namespace labels (Kubernetes native, replaces PodSecurityPolicy). Security Groups for Pods: assign SG directly to pod (not just node SG); fine-grained network control.

**Level 4 — Expert**: EKS Auto Mode: AWS manages node groups, autoscaling, and AMI updates automatically (2024 feature). EKS Hybrid Nodes: run EKS worker nodes on-premises. Cluster upgrade strategy: update managed add-ons → update node groups one at a time → use eksctl or AWS console. IPv6 cluster: pods get IPv6 addresses; useful for address exhaustion at massive scale. EKS network policy enforcement via VPC CNI: enable network policy support in VPC CNI add-on for K8s NetworkPolicy enforcement (uses eBPF). OIDC provider: EKS cluster has associated OIDC provider; required for IRSA. Each cluster = separate OIDC endpoint; IRSA trust policy references cluster-specific OIDC issuer.

---

## ⚙️ How It Works

### EKS Cluster (Terraform with EKS Module)

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "production"
  cluster_version = "1.31"

  # VPC
  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets  # for control plane ENIs

  # Cluster endpoint access
  cluster_endpoint_public_access  = true   # for kubectl from outside VPC
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access_cidrs = ["10.0.0.0/8"]  # restrict to corp IPs

  # Enable cluster add-ons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
      configuration_values = jsonencode({
        enableNetworkPolicy = "true"  # enable K8s NetworkPolicy
      })
    }
    aws-ebs-csi-driver = {
      most_recent              = true
      service_account_role_arn = module.ebs_csi_irsa_role.iam_role_arn
    }
  }

  # Managed Node Groups
  eks_managed_node_groups = {
    general = {
      instance_types = ["m7g.xlarge"]  # Graviton3
      ami_type       = "AL2023_ARM_64_STANDARD"

      min_size     = 3
      max_size     = 20
      desired_size = 6

      labels = {
        workload = "general"
      }

      taints = {}
    }

    memory_optimized = {
      instance_types = ["r7g.2xlarge"]  # for memory-intensive workloads
      ami_type       = "AL2023_ARM_64_STANDARD"

      min_size     = 0
      max_size     = 10
      desired_size = 2

      labels = {
        workload = "memory-intensive"
      }

      taints = [{
        key    = "workload"
        value  = "memory-intensive"
        effect = "NO_SCHEDULE"
      }]
    }
  }

  # EKS Access Management (API-based, replaces aws-auth ConfigMap)
  access_entries = {
    admin_team = {
      kubernetes_groups = []
      principal_arn     = "arn:aws:iam::123456789:role/EKSAdminRole"

      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  tags = {
    Environment = "prod"
  }
}
```

### IRSA (IAM Roles for Service Accounts)

```hcl
# IRSA role for a service account
module "s3_access_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name = "s3-access-role"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:my-app-sa"]  # namespace:serviceaccount
    }
  }

  role_policy_arns = {
    s3 = aws_iam_policy.s3_access.arn
  }
}
```

```yaml
# K8s Service Account annotated with IAM role
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/s3-access-role
---
# Deployment using the service account
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      serviceAccountName: my-app-sa # pod gets IAM role via IRSA
      containers:
        - name: app
          image: 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
          # AWS SDK auto-discovers credentials from projected service account token
```

### AWS Load Balancer Controller (Ingress)

```yaml
# Ingress → ALB (via AWS LB Controller)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip # recommended for EKS
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    alb.ingress.kubernetes.io/healthcheck-path: /actuator/health
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api/users
            pathType: Prefix
            backend:
              service:
                name: users-service
                port:
                  number: 8080
          - path: /api/orders
            pathType: Prefix
            backend:
              service:
                name: orders-service
                port:
                  number: 8080
```

---

## ⚖️ Comparison Table: EKS vs ECS vs Lambda

|                   | EKS                                    | ECS                               | Lambda                    |
| ----------------- | -------------------------------------- | --------------------------------- | ------------------------- |
| **Orchestration** | Kubernetes                             | ECS native                        | None                      |
| **Complexity**    | High                                   | Low                               | Minimal                   |
| **Portability**   | High (K8s)                             | Low (AWS-specific)                | Low (AWS-specific)        |
| **Ecosystem**     | Huge (CNCF)                            | Limited                           | Limited                   |
| **Cost overhead** | $0.10/hr cluster                       | None                              | None                      |
| **Best for**      | K8s expertise teams, complex workloads | Simple container workloads on AWS | Event-driven, short tasks |

---

## ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                   |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "EKS is just Kubernetes"                  | EKS adds AWS-specific integrations (IRSA, VPC CNI, LB Controller) that work differently from standard K8s |
| "EKS is more expensive than ECS"          | EKS cluster = $0.10/hr; you pay for nodes similarly; cost difference is operational, not compute          |
| "aws-auth ConfigMap is the only way"      | EKS Access Entries API (2024) replaces aws-auth ConfigMap; more reliable                                  |
| "Fargate profiles work for all workloads" | Fargate profiles don't support DaemonSets, privileged containers, or hostNetwork                          |

---

## 🔗 Related Keywords

- [ECS / Fargate](/cloud-aws/ecs-fargate/) — simpler container orchestration on AWS
- [Kubernetes](/kubernetes/kubernetes/) — EKS runs standard Kubernetes
- [ELB / ALB / NLB](/cloud-aws/elb-alb-nlb/) — ALB/NLB created by AWS LB Controller

---

## 📌 Quick Reference Card

```bash
# Update kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name my-cluster

# List node groups
aws eks list-nodegroups --cluster-name my-cluster

# Describe cluster
aws eks describe-cluster \
  --name my-cluster \
  --query 'cluster.{Status:status,K8sVersion:version,Endpoint:endpoint}'

# Check add-on versions
aws eks describe-addon-versions \
  --kubernetes-version 1.31 \
  --query 'addons[].{Name:addonName,Version:addonVersions[0].addonVersion}'

# Get node group status
aws eks describe-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name general \
  --query 'nodegroup.{Status:status,Desired:scalingConfig.desiredSize,Min:scalingConfig.minSize,Max:scalingConfig.maxSize}'

# Enable EKS Exec (for debugging)
aws eks create-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123:role/DevRole \
  --type STANDARD
```

---

## 🧠 Think About This

IRSA (IAM Roles for Service Accounts) is the most important EKS security feature and is widely underused. Before IRSA, pods running on EC2 nodes inherited the node's IAM role — meaning any pod on that node had the same AWS permissions. If you had a node role with S3 access for your app, every pod on that node (including any compromised one) had S3 access. IRSA gives each service account its own IAM role. Now your user-service gets S3 read access; your payment-service gets DynamoDB access; a compromised pod can only access what its service account can access. Implement this from day one: create one IAM role per service account, follow least privilege, and never grant node roles broad AWS permissions. This is the foundation of EKS security hardening.
