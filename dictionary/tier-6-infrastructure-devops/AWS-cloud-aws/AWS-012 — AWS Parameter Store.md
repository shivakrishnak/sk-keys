---
layout: default
title: "AWS Parameter Store"
parent: "Cloud — AWS"
nav_order: 12
permalink: /cloud-aws/aws-parameter-store/
id: AWS-012
category: Cloud — AWS
difficulty: ★★★
depends_on: AWS, Configuration Management, Security
used_by: CI-CD, Cloud — AWS, Spring Cloud Config
related: AWS Secrets Manager, HashiCorp Vault, Spring Cloud Config
tags:
  - aws
  - cloud
  - security
  - advanced
  - devops
---

# AWS-012 — AWS Parameter Store

⚡ **TL;DR —** AWS Systems Manager's hierarchical key-value store for centralised configuration and secrets, with KMS encryption, IAM path-based access control, and versioned parameter history.

| Attribute    | Value                                               |
|--------------|-----------------------------------------------------|
| Depends on   | AWS, Configuration Management, Security             |
| Used by      | CI-CD, Cloud — AWS, Spring Cloud Config             |
| Related      | AWS Secrets Manager, HashiCorp Vault, Spring Cloud Config |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Database passwords, API keys, and feature flags live in environment variables baked into EC2 AMIs, Lambda function configs, or committed (accidentally) to Git. Rotating a database password requires redeploying every service. A developer inspecting a container sees the plaintext secret in `env`. A misconfigured security group leaks a host, and the attacker harvests all secrets from `env`.

**THE BREAKING POINT:** You have 12 microservices, 4 environments (dev/staging/uat/prod), and 30 config values each. Managing 1 440 individual env vars across deployments is untenable. When the prod DB password rotates, you need to update 3 services — and you are not sure which services use it. An auditor asks for evidence that secrets are encrypted at rest. You cannot provide it.

**THE INVENTION MOMENT:** What if every configuration value lived in a central, versioned, IAM-controlled hierarchy? Services fetch their config at startup. Secrets are encrypted with KMS. A path `/prod/orders-service/db-password` is readable only by the `orders-service` ECS task role. Rotating the value requires changing one parameter — all services fetch it fresh on next start.

---

### 📘 Textbook Definition

**AWS Systems Manager Parameter Store** is a secure, hierarchical key-value store for configuration data and secrets. Parameters are organised in a **path hierarchy** (e.g. `/app/env/key`), enabling retrieval of entire subtrees via `GetParametersByPath`. Two tiers exist: **Standard** (free, 4 KB max value, 10 000 parameters/account/region) and **Advanced** (paid, 8 KB max value, parameter policies for expiry and change notifications). Parameter types include **String**, **StringList** (comma-separated), and **SecureString** (KMS-encrypted). All parameter changes are versioned — previous versions are accessible. Access is controlled via IAM policies that can restrict to specific path prefixes.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Parameter Store is a secure, versioned, IAM-controlled config and secrets registry organised as a file-system path hierarchy.

> Think of it as a filing cabinet where each drawer is locked by a different key, labelled by environment and service, and every time a file is updated, the old version is kept in the back of the drawer.

**One insight:** The hierarchy is not cosmetic — it is functional. `GetParametersByPath(/prod/orders-service)` fetches all parameters for the orders service in production in a single API call, replacing 30 individual `GetParameter` calls and enabling applications to self-configure at startup.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Secrets must not live in source code, container images, or unencrypted environment variables.
2. Access to secrets must be auditable, scoped to least-privilege, and revocable without redeployment.
3. Configuration must be environment-specific and changeable without application redeployment.
4. Secret rotation must propagate to consumers without manual per-service configuration changes.

**DERIVED DESIGN:**

Parameter Store separates configuration ownership (ops/security teams manage parameters) from configuration consumption (applications fetch at runtime). The path hierarchy (`/env/service/key`) enables IAM resource-based policies of the form `arn:aws:ssm:*:*:parameter/prod/orders-service/*` — scoping a service's IAM role to only its own parameters. KMS integration for SecureString means the plaintext never touches disk unencrypted; KMS key policies add a second layer of access control independent of IAM.

**THE TRADE-OFFS:**

**Gain:** Zero secrets in code. Centralised audit trail (CloudTrail logs every `GetParameter` call). Environment isolation via path prefix. Version history for rollback. Native integration with ECS, Lambda, CloudFormation, CodeDeploy.

**Cost:** Applications add startup latency fetching parameters (mitigated by caching). Advanced tier costs $0.05/parameter/month. No built-in automatic secret rotation (use Secrets Manager for that). API rate limits apply (40 `GetParameter` calls/s for Standard, 1 000/s for Advanced). Parameter Store has no cross-account access without custom tooling.

---

### 🧪 Thought Experiment

**SETUP:** You manage a payment service that connects to a PostgreSQL database. The DB password is currently in a Lambda environment variable. The security team rotates the password quarterly.

**WHAT HAPPENS WITHOUT Parameter Store:** Password is in Lambda env var → rotation requires redeploying Lambda. Every rotation is a deployment risk. The password is visible in the Lambda console to anyone with `lambda:GetFunction` permission. CloudTrail shows Lambda deployments, not password reads — no secret access audit trail. A junior developer accidentally commits the password to a test script → it lives in Git history forever.

**WHAT HAPPENS WITH Parameter Store:** Password is at `/prod/payment-service/db-password` (SecureString, KMS-encrypted). Lambda IAM role has `ssm:GetParameter` on `/prod/payment-service/*` only. At startup, Lambda fetches the password — KMS decrypts it in memory only. Quarterly rotation: ops updates the parameter → new Lambda invocations fetch the new value. No redeployment. CloudTrail shows every `GetParameter` call with timestamp, caller ARN, and parameter name — full audit trail.

**THE INSIGHT:** Parameter Store moves secrets from the deployment pipeline (where they are visible and baked in) to the runtime access path (where they are fetched on demand, audited, and revocable without redeployment).

---

### 🧠 Mental Model / Analogy

> Parameter Store is like a hotel safe system where every room has a safe with a different combination, the combination is managed by the concierge (AWS), and the hotel keeps a log of every time a safe was opened and who opened it. The guest's key card only opens their own room's safe.

- **Hotel safe** → Individual SSM Parameter
- **Safe combination** → KMS encryption key
- **Key card** → IAM role attached to ECS task / Lambda function
- **Only opens own room** → IAM resource policy scoped to `/prod/my-service/*`
- **Concierge manages combinations** → AWS manages KMS; ops manages parameter values
- **Log of every opening** → CloudTrail audit trail for every `GetParameter` API call
- **Room number hierarchy** → Parameter path `/environment/service/key`

Where this analogy breaks down: unlike a hotel safe, Parameter Store versions every change — the concierge keeps every historical value, and you can retrieve version N of any parameter.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Parameter Store is a secure place to store passwords and settings. Your application asks for a value by name and gets it back. The password never lives in your code.

**Level 2 — How to use it (junior developer):**
Store a parameter:
```bash
aws ssm put-parameter \
  --name "/prod/orders-service/db-password" \
  --value "s3cr3t" \
  --type SecureString \
  --key-id alias/my-kms-key
```
Fetch in application (Python):
```python
ssm = boto3.client('ssm')
param = ssm.get_parameter(
    Name='/prod/orders-service/db-password',
    WithDecryption=True
)
password = param['Parameter']['Value']
```
Add `ssm:GetParameter` + `kms:Decrypt` to the Lambda/ECS IAM role. Done.

**Level 3 — How it works (mid-level engineer):**
Parameters are stored in SSM's backend with metadata: name, type, value, version, last modified time, ARN. For SecureString, the value is encrypted by KMS before storage — `GetParameter` with `WithDecryption=True` calls KMS to decrypt before returning. `GetParametersByPath` retrieves all parameters under a prefix recursively (up to 10 per call, paginated). Parameter versions: each `PutParameter` (without `--overwrite`) fails; with `--overwrite`, a new version is created and the old version is preserved. Access patterns: at startup (fetch all config), at request time (cache in memory), or via AWS AppConfig integration (hot-reload without restart). CloudFormation can reference parameters via `{{resolve:ssm:/path/to/param:version}}` syntax.

**Level 4 — Why it was designed this way (senior/staff):**
The path hierarchy is implemented as a prefix scan over a key-value store, not a real filesystem. `GetParametersByPath` efficiency depends on using path prefixes as the primary access pattern — avoid creating flat namespaces. Standard vs Advanced tier exists for cost optimisation: Standard is free to incentivise adoption for non-secret config (feature flags, connection strings); Advanced charges for high-value use cases (large values, parameter policies). The rate limit separation (Standard: 40/s, Advanced: 1 000/s) incentivises Advanced for high-throughput microservice environments. The absence of built-in automatic rotation (vs Secrets Manager) is a deliberate scope boundary — Parameter Store is a generic config store; Secrets Manager is purpose-built for secret lifecycle management including rotation, with service-specific rotation Lambda functions maintained by AWS.

---

### ⚙️ How It Works (Mechanism)

```
+-----------------------------------------------+
| Application at runtime                        |
|  ssm.GetParameter(Name, WithDecryption=True)  |
|       |                                       |
|       v                                       |
| IAM checks: does caller role have             |
|  ssm:GetParameter on this ARN?                |
|       |                                       |
|       v                                       |
| SSM retrieves encrypted value from store      |
|       |                                       |
|  If SecureString:                             |
|  KMS.Decrypt(ciphertext, keyId)               |
|  IAM checks: kms:Decrypt allowed?             |
|  Returns plaintext only in API response       |
|       |                                       |
|       v                                       |
| Parameter returned (current version or :N)   |
| CloudTrail: logs GetParameter call            |
+-----------------------------------------------+
```

**Parameter Tiers:**

| Feature                | Standard      | Advanced           |
|------------------------|---------------|--------------------|
| Cost                   | Free          | $0.05/param/month  |
| Max value size         | 4 KB          | 8 KB               |
| Parameter limit        | 10 000/region | 100 000/region     |
| Parameter policies     | No            | Yes (expiry/notify)|
| Higher throughput      | 40 req/s      | 1 000 req/s        |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Ops engineer rotates DB password
  |
  v
aws ssm put-parameter \   <- YOU ARE HERE
  --name /prod/orders/db-password \
  --value "new-secret" \
  --overwrite
  |
  v
SSM creates Version 3
Previous versions (1, 2) retained
  |
  v
New Lambda invocation starts
  |
  v
Lambda handler fetches config on cold start:
  GetParametersByPath(/prod/orders)
  -> returns Version 3 of db-password
  -> all parameters under /prod/orders
  |
  v
Lambda connects to DB with new password
No redeployment required
  |
  v
CloudTrail: logs GetParameter(
  caller=arn:aws:sts::123:assumed-role/orders-lambda,
  parameter=/prod/orders/db-password,
  version=3
)
```

**FAILURE PATH:** Application cannot connect to DB after rotation — ops retrieves Version 2 of the parameter and can roll back by overwriting with the old value. `GetParameter` with `:2` suffix (e.g. `/prod/orders/db-password:2`) fetches a specific historical version.

**WHAT CHANGES AT SCALE:** At high Lambda invocation rates, `GetParameter` calls per second can hit rate limits (40/s for Standard). Mitigate by: (1) fetching on cold start only (cache in module scope), (2) using `GetParametersByPath` to batch all params in one call, (3) upgrading to Advanced tier for 1 000/s throughput, (4) using AWS AppConfig with caching agent sidecar.

---

### 💻 Code Example

**BAD — Secrets in environment variables and code:**
```python
# BAD: secret in env var set at deploy time
import os

DB_PASSWORD = os.environ['DB_PASSWORD']
# Visible in Lambda console, CloudWatch logs,
# and any process listing environment variables.
# Rotation requires Lambda redeployment.
```

**GOOD — SecureString fetched at cold start, cached in memory:**
```python
import boto3
import json
from functools import lru_cache

ssm = boto3.client('ssm', region_name='us-east-1')

@lru_cache(maxsize=1)
def get_config() -> dict:
    """
    Fetch all parameters for this service at cold start.
    Cached in module scope; refreshed only on Lambda
    cold start (environment reuse keeps cache warm).
    """
    response = ssm.get_parameters_by_path(
        Path='/prod/orders-service',
        Recursive=True,
        WithDecryption=True    # KMS decrypt SecureString
    )
    # Build flat dict: /prod/orders-service/db-password
    # -> key "db-password"
    config = {}
    for param in response['Parameters']:
        key = param['Name'].split('/')[-1]
        config[key] = param['Value']
    return config

def lambda_handler(event, context):
    config = get_config()          # cached after first call
    db_password = config['db-password']
    # use db_password to connect...
```

```bash
# IAM policy: orders-service can only read its own params
# CloudFormation snippet
OrdersServiceSSMPolicy:
  Type: AWS::IAM::ManagedPolicy
  Properties:
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - ssm:GetParameter
            - ssm:GetParametersByPath
          Resource:
            - !Sub >-
              arn:aws:ssm:${AWS::Region}:
              ${AWS::AccountId}:parameter/prod/orders-service/*
        - Effect: Allow
          Action: kms:Decrypt
          Resource: !GetAtt AppKMSKey.Arn
```

---

### ⚖️ Comparison Table

| Feature                | Parameter Store (Std) | Parameter Store (Adv) | Secrets Manager       | HashiCorp Vault      |
|------------------------|-----------------------|-----------------------|-----------------------|----------------------|
| Cost                   | Free                  | $0.05/param/month     | $0.40/secret/month    | Self-managed or HCP  |
| Auto secret rotation   | No                    | No                    | Yes (built-in)        | Yes (leases)         |
| Max value size         | 4 KB                  | 8 KB                  | 64 KB                 | Unlimited            |
| Versioning             | Yes                   | Yes                   | Yes (AWSPREVIOUS/AWSCURRENT) | Yes (leases)|
| Cross-account access   | Manual (assume role)  | Manual                | Native resource policy| Yes                  |
| Audit trail            | CloudTrail            | CloudTrail            | CloudTrail            | Vault audit log      |
| Path hierarchy         | Yes                   | Yes                   | No (flat namespace)   | Yes (mounts)         |
| Parameter policies     | No                    | Yes (expiry/notify)   | Rotation policy       | TTL-based leases     |
| Multi-cloud            | AWS only              | AWS only              | AWS only              | Multi-cloud          |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Parameter Store and Secrets Manager are interchangeable" | Secrets Manager has built-in automatic rotation (AWS-managed Lambda), cross-account native access, and costs $0.40/secret/month. Use it for secrets requiring rotation. Use Parameter Store for config and secrets that don't need automatic rotation. |
| "SecureString means the value is always encrypted in transit" | All AWS API calls use TLS — both String and SecureString are encrypted in transit. SecureString means the value is also encrypted at rest in SSM storage using KMS. |
| "IAM resource policy `*` on SSM is fine for dev" | It grants access to all parameters in the account including production secrets stored by other services. Always scope to a specific path prefix. |
| "GetParameter always returns the latest version" | Without a version suffix, yes. But if you pin with `:1` or `:AWSPREVIOUS` (Secrets Manager equivalent does not apply here), you get a specific version. Automation should explicitly avoid pinning versions to ensure rotation propagates. |
| "Parameter Store is only for secrets" | It is a general-purpose config store. Feature flags, database hostnames, environment names, and non-sensitive configuration all belong here alongside secrets. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 — Application uses stale parameter after rotation**

**Symptom:** After rotating a DB password, some Lambda invocations connect successfully (new password) while others fail (old password). Mixed results for 15–30 minutes.
**Root Cause:** Lambda execution environments that are already warm (not cold-starting) have the old password cached in module-scope. New cold starts fetch the new value; warm environments reuse the cached old value.
**Diagnostic:**
```bash
# Identify which Lambda execution environments are stale
# Check Lambda logs for DB connection errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/orders-service \
  --filter-pattern "authentication failed" \
  --start-time $(date -d '30 minutes ago' +%s000)
```
**Fix:**
```bash
# Force cold start by deploying a trivial config change
# This terminates all warm environments
aws lambda update-function-configuration \
  --function-name orders-service \
  --description "force-cold-start-$(date +%s)"
```
**Prevention:** Design rotation as a two-phase process: (1) add new credential alongside old (dual-write period), (2) update Parameter Store, (3) wait for all warm envs to expire (~15 min), (4) remove old credential. Or use Secrets Manager's built-in rotation which handles this correctly.

---

**Mode 2 — ThrottlingException on GetParameter**

**Symptom:** Lambda/ECS tasks receive `ThrottlingException: Rate exceeded` from SSM on startup, especially during scale-out events.
**Root Cause:** Standard tier allows 40 `GetParameter` calls/s per account per region. A scale-out event with 50 Lambda cold starts each calling `GetParameter` 10 times = 500 calls/s → throttled.
**Diagnostic:**
```bash
# Check SSM throttling in CloudTrail
aws cloudtrail lookup-events \
  --lookup-attributes \
    AttributeKey=EventName,AttributeValue=GetParameter \
  --start-time 2024-01-01T10:00:00Z \
  --end-time 2024-01-01T10:05:00Z \
  | jq '.Events[] | select(
      .CloudTrailEvent | fromjson | .errorCode
      == "ThrottlingException"
    ) | .EventTime'
```
**Fix:** Replace individual `GetParameter` calls with a single `GetParametersByPath` call (counts as one API call for the path scan). Add exponential backoff with jitter on `ThrottlingException`. Upgrade affected parameters to Advanced tier (1 000/s throughput).
**Prevention:** Always use `GetParametersByPath` for multi-parameter fetches. Cache parameters in module scope (Lambda) or in-process (ECS) with TTL-based refresh rather than fetching per invocation.

---

**Mode 3 — Unauthorised access error at runtime**

**Symptom:** Application receives `AccessDeniedException` when calling `GetParameter` for a specific path.
**Root Cause:** IAM role missing `ssm:GetParameter` permission for that parameter ARN, OR the parameter is SecureString and the role lacks `kms:Decrypt` on the KMS key.
**Diagnostic:**
```bash
# Simulate the IAM policy evaluation
aws iam simulate-principal-policy \
  --policy-source-arn \
    arn:aws:iam::123456789012:role/orders-service-role \
  --action-names ssm:GetParameter kms:Decrypt \
  --resource-arns \
    "arn:aws:ssm:us-east-1:123:parameter/prod/orders/*" \
    "arn:aws:kms:us-east-1:123:key/abc-def-123"
# Look for "implicitDeny" or "explicitDeny" results
```
**Fix:** Add the missing IAM permission to the role's policy. For KMS decryption, ensure the role ARN is listed as a key user in the KMS key policy (not just IAM policy).
**Prevention:** Test all IAM permissions using `iam:SimulatePrincipalPolicy` in CI/CD pipeline before deployment. Use least-privilege path scoping from day one.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- AWS — IAM roles, KMS key policies, CloudTrail, resource ARN format
- Configuration Management — the general pattern of externalising config from application code
- Security — encryption at rest/in transit, least-privilege access, secret rotation

**Builds On This (learn these next):**
- AWS Secrets Manager — extends Parameter Store concepts with automatic rotation and cross-account access
- AWS AppConfig — builds on Parameter Store for feature flags with validation, deployment strategies, and hot-reload
- CI/CD — inject parameters into deployment pipelines using `ssm:GetParameter` in CodeBuild/CodeDeploy

**Alternatives / Comparisons:**
- AWS Secrets Manager — use when automatic secret rotation is required; higher cost but richer lifecycle management
- HashiCorp Vault — use for multi-cloud, complex secret leasing, dynamic secrets, or on-premises environments
- Spring Cloud Config — use when centralising config for JVM microservices with Git-backed config and environment profiles

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Hierarchical SSM config/secret    |
|              | store with KMS + IAM + versioning  |
| PROBLEM      | Secrets in code, env vars, images  |
| KEY INSIGHT  | Path = namespace + access boundary;|
|              | IAM scoped to /env/service/*       |
| USE WHEN     | Config, non-rotating secrets,      |
|              | feature flags, DB hostnames        |
| AVOID WHEN   | Auto-rotation needed (use SM)      |
| TRADE-OFF    | Free (Standard) vs $0.05 (Advanced)|
|              | throughput and policies            |
| ONE-LINER    | GetParametersByPath(/prod/svc)     |
|              | -> all config in one call          |
| NEXT EXPLORE | Secrets Manager, AppConfig         |
+--------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** You store 50 000 parameters across 200 microservices and 5 environments. Standard tier is free but limits you to 40 `GetParameter` calls/s. A new microservice auto-scales to 500 instances during peak, each fetching 30 parameters on cold start. Do you upgrade to Advanced tier, redesign the fetch pattern, or both? What specific changes reduce API call rate most dramatically?

2. **(Security)** A Lambda function has `ssm:GetParameter` on `arn:aws:ssm:*:*:parameter/*` (wildcard). Describe three distinct security risks this overly-broad policy creates, and the precise IAM resource ARN you would use instead to scope it correctly to the `orders-service` production parameters.

3. **(System Interaction)** Your Spring Boot application running on ECS fetches configuration via `@Value("${/prod/app/db-url}")` using Spring Cloud AWS SSM integration at startup. The DevOps team updates `/prod/app/db-url` to point to a new database. Which running containers pick up the new value, which ones don't, and what operational procedure ensures all containers see the updated config within 5 minutes?
