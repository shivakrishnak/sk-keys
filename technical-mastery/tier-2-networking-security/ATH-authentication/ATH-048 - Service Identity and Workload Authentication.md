---
id: ATH-048
title: "Service Identity and Workload Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-039, ATH-043, ATH-047
used_by: ATH-049, ATH-053, ATH-055, ATH-058
related: ATH-039, ATH-047, ATH-049
tags:
  - security
  - authentication
  - service-identity
  - spiffe
  - workload
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/authentication/service-identity-and-workload-authentication/
---

⚡ **TL;DR** - "Service identity" answers: how does service A prove
to service B that it is genuinely service A and not a compromised
workload? The answer in modern cloud-native systems: platform-managed
workload identity. AWS gives IAM roles to EC2/Lambda via instance
metadata. GCP binds Service Accounts to GKE pods. SPIFFE/SPIRE
issues short-lived X.509 certificates to workloads based on their
k8s service account. No static credentials - identity is tied to
the workload's existence, automatically rotated, and bound to the
compute platform.

---

### 📊 Entry Metadata

| #048 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-039 mTLS, ATH-043 SSH Keys, ATH-047 Distributed Auth | |
| **Used by:** | ATH-049, ATH-053, ATH-055, ATH-058 | |
| **Related:** | ATH-039 mTLS, ATH-047 Distributed Auth, ATH-049 mTLS in Mesh | |

---

### 📘 Textbook Definition

Workload authentication (service identity) is the process by
which a running application or service proves its identity to
other services or platforms. Traditional approaches use static
credentials (API keys, passwords). Modern approaches use
platform-managed identity: the compute platform (AWS, GCP,
Azure, Kubernetes) issues and manages short-lived cryptographic
credentials for workloads, bound to the workload's execution
context. SPIFFE (Secure Production Identity Framework For
Everyone) is the open standard for workload identity, using
SPIFFE IDs (URIs) and SVIDs (X.509 certificates or JWTs) to
represent service identities in a verifiable, platform-neutral way.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Workload Identity Platforms                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  AWS: IAM Roles for EC2/ECS/Lambda                     │
│  - Pod/function gets IAM role at deploy time           │
│  - AWS metadata service provides temp credentials      │
│  - curl http://169.254.169.254/latest/meta-data/       │
│          iam/security-credentials/role-name            │
│  - Creds expire every 1-6 hours, auto-rotated          │
│  - No static access keys needed in code               │
│                                                        │
│  GCP: Workload Identity for GKE                        │
│  - K8s ServiceAccount maps to GCP ServiceAccount       │
│  - Pod gets GCP SA credentials via metadata server     │
│  - No JSON key file needed in deployment               │
│                                                        │
│  SPIFFE/SPIRE: platform-neutral                        │
│  - SPIRE Agent runs on each node                       │
│  - Attests workload identity via K8s SA, UID, etc.     │
│  - Issues SVID: X.509 cert with SPIFFE URI in SAN      │
│    spiffe://trust-domain/service/payment               │
│  - Cert valid for 1 hour, auto-rotated by agent        │
│  - Works on-prem, AWS, GCP, Azure, VMs                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - AWS SDK using IAM role (no static credentials)**

```java
@Configuration
public class AwsConfig {

    @Bean
    public S3Client s3Client() {
        // No credentials needed in code
        // SDK auto-discovers via:
        // 1. EC2 instance metadata service
        // 2. ECS task metadata
        // 3. Lambda execution role
        // 4. AWS_WEB_IDENTITY_TOKEN_FILE (EKS)
        return S3Client.builder()
            .region(Region.US_EAST_1)
            // Default credentials provider chain
            // tries all the above automatically
            .credentialsProvider(
                DefaultCredentialsProvider.create())
            .build();
    }
}

// At runtime: SDK calls metadata service
// GET http://169.254.169.254/latest/meta-data/
//          iam/security-credentials/my-app-role
// Returns: AccessKeyId, SecretAccessKey, SessionToken
// (valid for 1-6 hours, transparently rotated by AWS)
```

**Example - SPIRE workload API usage**

```java
// Java SPIFFE helper: X509Source from SPIRE workload API
X509Source source = X509Source.newSource();
// source connects to SPIRE Agent on localhost:8081
// (Unix socket or TCP - no credentials needed)
// Agent verifies workload identity and returns SVID

X509Svid svid = source.getBundleForTrustDomain(
    TrustDomain.parse("example.org"));
// svid.getX509Certificates() = current mTLS cert
// svid is auto-renewed before expiry by SPIRE Agent
// Build SSLContext with this cert for outgoing mTLS
```

---

*Authentication category: ATH | Entry: ATH-048 | v5.0*