---
layout: default
title: "AWS Secrets Manager"
parent: "Cloud — AWS"
nav_order: 2197
permalink: /cloud-aws/aws-secrets-manager/
number: "2197"
category: Cloud — AWS
difficulty: ★★★
depends_on: AWS Parameter Store, AWS KMS, Security
used_by: Cloud — AWS, CI-CD
related: AWS Parameter Store, HashiCorp Vault, Kubernetes Secrets
tags:
  - aws
  - cloud
  - security
  - advanced
---

# 2197 — AWS Secrets Manager

⚡ **TL;DR —** A managed AWS service that stores, rotates, and audits secrets — database passwords, API keys, and tokens — automatically and invisibly.

| | |
|---|---|
| **Depends on** | AWS Parameter Store, AWS KMS, Security |
| **Used by** | Cloud — AWS, CI-CD |
| **Related** | AWS Parameter Store, HashiCorp Vault, Kubernetes Secrets |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Developers hardcode database passwords in source code and environment variables. Credentials appear in Git history, CI/CD logs, and AMI snapshots. Rotating a password means updating dozens of config files across microservices — a manual, error-prone, downtime-causing operation.

**THE BREAKING POINT:** A single leaked credential in a public repo causes a full database breach. The security team mandates 90-day password rotation. No team wants to coordinate the multi-hour rotation window across 15 services with zero downtime.

**THE INVENTION MOMENT:** AWS built Secrets Manager to answer one question: what if credential rotation was automatic, audited, and invisible to the application?

---

### 📘 Textbook Definition

**AWS Secrets Manager** is a fully managed service that enables you to store, retrieve, rotate, and audit secrets — credentials, API keys, OAuth tokens, and certificates — with automatic rotation via Lambda functions, fine-grained IAM access control, and integration with AWS KMS for encryption at rest and in transit.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A locked vault for application secrets that rotates its own contents on a schedule.

**One analogy:**
> Secrets Manager is like a bank safe deposit box where the bank automatically replaces the key inside every 90 days, gives each employee only the access they need, and logs every time anyone opens it.

**One insight:** The application never stores the secret — it asks Secrets Manager at runtime, always getting the current value regardless of how many rotations have happened.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Secrets are never stored in code, environment variables, or config files.
2. Every access is authenticated by IAM and encrypted by KMS.
3. Rotation is handled by a Lambda function — not by the application.
4. Every secret access is logged immutably in CloudTrail.

**DERIVED DESIGN:** Each secret has versioned content with stage labels (`AWSCURRENT`, `AWSPENDING`, `AWSPREVIOUS`). The application calls `GetSecretValue` against the current version. When rotation runs, Lambda updates the target system and promotes the new version atomically — maintaining overlapping validity so in-flight requests never break.

**THE TRADE-OFFS:**
**Gain:** Zero hardcoded credentials, automatic rotation, full audit trail, cross-region replication.
**Cost:** API call latency per retrieval ($0.40/10K API calls), Lambda cost for rotation, added complexity in local dev without mocking.

---

### 🧪 Thought Experiment

**SETUP:** Your application connects to an RDS database. The password is in an environment variable baked into the container image at build time.

**WHAT HAPPENS WITHOUT Secrets Manager:** A penetration tester pulls the container image from ECR. They find `DB_PASSWORD=s3cr3t` in the `ENV` layer. They access production data directly with no time limit on that credential.

**WHAT HAPPENS WITH Secrets Manager:** The container has no credentials. At startup it calls `GetSecretValue`. IAM validates the task role. KMS decrypts the ciphertext. The app gets the current password — which rotated 3 days ago and has already changed since the tester's theoretical intercept.

**THE INSIGHT:** The security model shifts from "protect the static secret forever" to "the secret changes so frequently that the attacker's window is days, not indefinite."

---

### 🧠 Mental Model / Analogy

> Secrets Manager is like a combination lock safe where the combination changes automatically on a schedule. The safe notifies the right systems of the new combination, logs every access attempt, and lets you define exactly who is allowed to even try to open it.

- **Safe** = the Secrets Manager secret store
- **Combination** = the actual credential value
- **Scheduled combination change** = automatic rotation policy
- **Access log** = CloudTrail audit trail
- **Authorized persons** = IAM resource policy on the secret

Where this analogy breaks down: a real safe requires communicating the new combination to people manually; Secrets Manager propagates the new value into the application path automatically via Lambda.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
It's a password manager for your cloud applications. Your app asks it for the database password instead of having the password written down somewhere a thief could find it.

**Level 2 — How to use it (junior developer):**
Store a secret in the console or with the CLI. In your app, call `GetSecretValue` using the AWS SDK. Add the `secretsmanager:GetSecretValue` permission to your IAM role. Never put the actual password in your code.

**Level 3 — How it works (mid-level engineer):**
Each secret has a current version (`AWSCURRENT`) and a pending version (`AWSPENDING`). Rotation uses a Lambda function with four sequential steps: `createSecret` → `setSecret` → `testSecret` → `finishSecret`. Lambda updates the target system (RDS, Redshift, etc.) before promoting `AWSPENDING` to `AWSCURRENT`. The old value lives as `AWSPREVIOUS` for a grace window.

**Level 4 — Why it was designed this way (senior/staff):**
The four-step rotation with overlapping versions solves the distributed consistency problem: multiple in-flight requests may hold an open connection using the old password while rotation happens. Keeping `AWSPREVIOUS` valid briefly means both credentials work simultaneously. This mirrors the dual-key rotation pattern in cryptographic key lifecycle management — a fundamental technique for zero-downtime transitions.

---

### ⚙️ How It Works (Mechanism)

1. **Secret creation** — secret stored as JSON blob (or plain text), encrypted with a KMS key.
2. **Access** — app calls `GetSecretValue(SecretId)`. IAM policy on the caller AND resource policy on the secret must allow access. KMS decrypts the ciphertext and returns plaintext to Secrets Manager, which forwards it to the caller.
3. **Rotation trigger** — on schedule (cron) or on-demand. Secrets Manager invokes the rotation Lambda with the secret ARN and a client request token.
4. **Rotation steps** — Lambda executes four lifecycle methods in sequence against the backing service.
5. **Versioning** — stage labels track state: `AWSPENDING` → `AWSCURRENT` → `AWSPREVIOUS` after each rotation cycle.
6. **Replication** — secrets replicated to secondary regions for DR with independent KMS keys per region.
7. **Audit** — every API call captured in CloudTrail: principal, time, secret ARN, source IP.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
App (ECS Task)          Secrets Manager     KMS       RDS
     |                        |              |          |
     |-- GetSecretValue() --->|              |          |
     |              [IAM check on role]      |          |
     |              [resource policy check] |          |
     |                        |-- Decrypt ->|          |
     |                        |<- plaintext-|          |
     |<- {"password":"abc"} --|  ← YOU ARE HERE        |
     |-- connect(password) ----------------------->    |
     |<-- connection established ------------------>   |
```

**FAILURE PATH:**
- IAM role missing `secretsmanager:GetSecretValue` → `AccessDeniedException`
- KMS key policy denies the role → `AccessDeniedException` from KMS layer
- Secret does not exist → `ResourceNotFoundException`
- Lambda rotation fails mid-cycle → secret stuck in `AWSPENDING`

**WHAT CHANGES AT SCALE:**
With thousands of pods, every DB connection attempt calling `GetSecretValue` hits API rate limits. Use the AWS Secrets Manager caching client (available in Java, Python, Go) with a 5-minute TTL. On rotation, the cache TTL naturally expires before the grace window closes.

---

### 💻 Code Example

**BAD — hardcoded credentials:**
```python
# Never do this — password in source code
DB_PASSWORD = "mypassword123"
conn = psycopg2.connect(password=DB_PASSWORD)
```

**GOOD — retrieve from Secrets Manager with caching:**
```python
import boto3, json
from botocore.exceptions import ClientError

def get_secret(
    secret_name: str,
    region: str = "us-east-1"
) -> dict:
    client = boto3.client(
        "secretsmanager", region_name=region
    )
    try:
        resp = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    return json.loads(resp["SecretString"])

creds = get_secret("prod/myapp/db")
conn = psycopg2.connect(
    host=creds["host"],
    user=creds["username"],
    password=creds["password"]
)
```

**AWS CLI — create, retrieve, and enable rotation:**
```bash
# Create a secret
aws secretsmanager create-secret \
  --name "prod/myapp/db" \
  --kms-key-id alias/myapp-key \
  --secret-string \
    '{"username":"admin","password":"s3cr3t"}'

# Retrieve current value
aws secretsmanager get-secret-value \
  --secret-id "prod/myapp/db" \
  --query SecretString \
  --output text

# Enable automatic 30-day rotation
aws secretsmanager rotate-secret \
  --secret-id "prod/myapp/db" \
  --rotation-lambda-arn \
    "arn:aws:lambda:us-east-1:123:function:Rotate" \
  --rotation-rules AutomaticallyAfterDays=30

# Replicate to a DR region
aws secretsmanager replicate-secret-to-regions \
  --secret-id "prod/myapp/db" \
  --add-replica-regions Region=us-west-2
```

---

### ⚖️ Comparison Table

| Feature | Secrets Manager | Param Store Standard | Param Store Advanced |
|---|---|---|---|
| **Auto rotation** | Yes (Lambda) | No | No |
| **Cost** | $0.40/secret/month | Free | $0.05/param/month |
| **Max secret size** | 65 KB | 4 KB | 8 KB |
| **Cross-region replication** | Yes | No | No |
| **Versioning model** | Stage labels | Version numbers | Version numbers |
| **Resource policy** | Yes | No | No |
| **Best for** | DB creds, rotating secrets | Config values, flags | Large config, policies |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Secrets Manager and Parameter Store are the same thing" | Secrets Manager adds automatic rotation, replication, dedicated secret APIs, and resource-based policies. Parameter Store is for config values; Secrets Manager is for credentials. |
| "Encrypting with Secrets Manager means I don't separately need KMS" | Secrets Manager always uses a KMS key for encryption. You choose which key (AWS-managed or a CMK). KMS charges still apply. |
| "My app must update its cached password when a secret rotates" | Not if it retrieves the secret per-connection or uses the caching client with a short TTL. The rotation is transparent to well-written applications. |
| "Rotation causes downtime" | The four-step rotation keeps `AWSPREVIOUS` valid during the grace window. Both old and new passwords are accepted by the target for a brief overlap period. |
| "A single IAM policy is sufficient for access control" | Both the IAM identity policy on the caller AND the resource-based policy on the secret must permit access. Both gates must open independently. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: AccessDeniedException on GetSecretValue**
**Symptom:** Application fails to start; logs show `AccessDeniedException` from `secretsmanager`.
**Root Cause:** IAM role missing `secretsmanager:GetSecretValue` or the KMS key policy denies `kms:Decrypt` for the role.
**Diagnostic:**
```bash
# Simulate the permission
aws iam simulate-principal-policy \
  --policy-source-arn \
    arn:aws:iam::123456789:role/AppRole \
  --action-names secretsmanager:GetSecretValue \
  --resource-arns \
    arn:aws:secretsmanager:us-east-1:123:secret:prod/db
# Check KMS key policy
aws kms get-key-policy \
  --key-id alias/myapp-key \
  --policy-name default
```
**Fix:** Add `secretsmanager:GetSecretValue` to the role's IAM policy and `kms:Decrypt` for the encryption key ARN.
**Prevention:** Use IAM Access Analyzer to detect missing permissions pre-deployment. Test with least-privilege role in staging.

**Mode 2: Rotation Lambda fails mid-rotation**
**Symptom:** Secret version stuck in `AWSPENDING`; application connects with stale password; next rotation is blocked.
**Root Cause:** Lambda timeout, VPC connectivity issue, or incorrect DB admin credentials in the Lambda environment.
**Diagnostic:**
```bash
# Check version stage labels
aws secretsmanager describe-secret \
  --secret-id "prod/myapp/db" \
  --query 'VersionIdsToStages'
# Tail rotation Lambda logs
aws logs tail \
  /aws/lambda/SecretsManagerRotation \
  --follow
```
**Fix:** Fix the Lambda environment (VPC subnet, security group, DB admin permissions). Manually finish or re-trigger the rotation.
**Prevention:** Test rotation Lambda in a non-production account first. Use VPC endpoints so Lambda reaches Secrets Manager without requiring a NAT Gateway.

**Mode 3: ThrottlingException under pod-scale load**
**Symptom:** `ThrottlingException` on `GetSecretValue` during traffic spikes or pod scaling events.
**Root Cause:** Each pod calls `GetSecretValue` on every database connection pool creation. 500 pods × 10 connections = 5000 calls/burst — approaching the default limit.
**Diagnostic:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/SecretsManager \
  --metric-name NumberOfRequestsThrottled \
  --period 60 \
  --statistics Sum \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z
```
**Fix:** Use the AWS Secrets Manager caching client SDK. Cache the secret in memory with a 5-minute TTL.
**Prevention:** Always cache secrets. Fetch once per process lifecycle and refresh on TTL expiry or explicit rotation notification via EventBridge.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- AWS KMS — Secrets Manager uses KMS for all encryption; understanding key policies is essential before managing CMK-encrypted secrets.
- AWS IAM — All access control is IAM-based with resource policies layered on top; both must be correct.
- AWS Parameter Store — Understand the simpler, cheaper alternative to know when Secrets Manager is justified.

**Builds On This (learn these next):**
- AWS CDK — Define secrets, rotation Lambdas, and IAM permissions as reusable infrastructure code.
- AWS PrivateLink — Access Secrets Manager from private subnets without internet exposure via VPC interface endpoints.
- CI/CD Pipelines — Inject secrets into CodePipeline/CodeBuild build environments without any hardcoded values.

**Alternatives / Comparisons:**
- HashiCorp Vault — Self-managed, cloud-agnostic secrets management with dynamic secrets and a rich plugin ecosystem.
- Kubernetes Secrets — Native K8s secrets (base64-encoded, not encrypted by default; requires KMS integration for encryption at rest).
- AWS Parameter Store — Simpler and cheaper, but lacks automatic rotation and cross-region replication.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Managed secret store with          |
|                  | auto-rotation, KMS encryption,      |
|                  | IAM access, and CloudTrail audit    |
| PROBLEM IT SOLVES| Hardcoded credentials, manual       |
|                  | rotation, leaked secrets in logs    |
| KEY INSIGHT      | App retrieves secret at runtime;   |
|                  | rotation is invisible to the app    |
| USE WHEN         | DB passwords, API keys, OAuth       |
|                  | tokens that require rotation        |
| AVOID WHEN       | Plain config flags or non-sensitive |
|                  | values (use Parameter Store)        |
| TRADE-OFF        | API latency + $0.40/month vs       |
|                  | zero static credentials in code     |
| ONE-LINER        | secretsmanager:GetSecretValue()    |
| NEXT EXPLORE     | AWS KMS, AWS PrivateLink           |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Scale)** Your 2,000-pod application calls `GetSecretValue` on every new database connection. The Secrets Manager default API limit is 10,000 requests/second per region. What caching strategy ensures pods never throttle while still reflecting a rotated credential within the rotation grace window?

2. **(Design Trade-off)** Secrets Manager costs $0.40/secret/month plus API fees; SSM Parameter Store Standard is free. A 200-microservice platform has 800 secrets total. What criteria — beyond cost — determine which service is appropriate for each secret type, and who should own that decision in the organisation?

3. **(First Principles)** The rotation process keeps both `AWSCURRENT` and `AWSPREVIOUS` valid simultaneously for a grace window. What distributed systems failure does this overlap window prevent, and what new attack surface — if any — does maintaining two valid credentials create?
