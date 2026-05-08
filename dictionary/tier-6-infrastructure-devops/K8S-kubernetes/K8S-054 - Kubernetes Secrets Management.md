---
layout: default
title: "Kubernetes Secrets Management"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /kubernetes/kubernetes-secrets-management/
id: K8S-054
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Secret", "RBAC (K8s)", "Service Account", "etcd"]
used_by: ["K8s Security Hardening", "GitOps with Kubernetes"]
related:
  ["Secret", "Service Account", "RBAC (K8s)", "etcd", "K8s Security Hardening"]
tags:
  [
    kubernetes,
    secrets,
    secrets-management,
    vault,
    external-secrets,
    k8s,
    security,
  ]
---

# Kubernetes Secrets Management

## ⚡ TL;DR

Kubernetes Secrets store sensitive data (passwords, tokens, keys) but are **only base64-encoded by default (not encrypted)**. Production secrets management requires: encryption at rest (`EncryptionConfiguration`), RBAC restrictions, and ideally an external secrets store (HashiCorp Vault, AWS Secrets Manager) via External Secrets Operator or Secrets Store CSI Driver.

---

## 🔥 Problem This Solves

Apps need passwords, API keys, and TLS certificates. Hardcoding in images is terrible. ConfigMaps store config but not secrets. Kubernetes Secrets provide a mechanism for injection, but require additional hardening (encryption, access control, rotation) to be production-safe.

---

## 📘 Textbook Definition

Kubernetes Secrets is an object that contains small amounts of sensitive data. It allows sensitive information to be included in pods without putting it in the pod spec. Secrets Management encompasses the full lifecycle: creation, storage (encrypted), access control (RBAC), injection (env/volume), and rotation.

---

## ⏱️ 30 Seconds

```yaml
# Secret (base64-encoded - NOT encrypted)
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  DB_PASSWORD: cGFzc3dvcmQxMjM= # base64("password123")
  DB_URL: amRiYzpwb3N0Z3Jlc...

---
# Use in Pod (env or volume)
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: DB_PASSWORD
```

---

## 🔩 First Principles

- Secret data is base64-encoded (obfuscation, not encryption)
- Secrets stored in etcd; **must enable EncryptionConfiguration** for encryption at rest
- Kubernetes transmits Secrets over TLS between API Server and nodes
- Secrets mounted as volumes use `tmpfs` (memory-backed, not written to disk)
- RBAC restricts who can `get`/`list` Secrets (listing all secrets = dump all credentials)
- External secrets stores (Vault, AWS SM) are the enterprise standard

---

## 🧪 Thought Experiment

Your cluster's etcd backup is uploaded to S3. If Secrets are not encrypted at rest: anyone with S3 access can decode all base64 "encrypted" values and get every password in your cluster. With `EncryptionConfiguration`: even with etcd backup access, secrets are AES-256 encrypted. Attacker gets ciphertext, not plaintext.

---

## 🧠 Mental Model / Analogy

Kubernetes native Secrets are like a **filing cabinet with a label "Confidential"** but no lock - base64 is just a label. `EncryptionConfiguration` adds a real lock. External secrets stores (Vault) are like a **bank vault with HSM** - enterprise-grade, with audit trails, auto-rotation, and dynamic credentials.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Kubernetes Secrets hold passwords/keys. They're base64 in YAML but need encryption at rest. Never commit Secret YAMLs to Git.

**Level 2 - Practitioner**: Enable `EncryptionConfiguration` on API Server for AES-256. Use RBAC to restrict who can read secrets. Mount as volumes (tmpfs) rather than env vars (env vars leak in process lists). `kubectl create secret generic` for creation.

**Level 3 - Advanced**: External Secrets Operator: syncs secrets from AWS Secrets Manager/Vault/GCP SM to Kubernetes Secrets. `ExternalSecret` CRD: define source + target. Secrets Store CSI Driver: mounts external secrets as volumes directly (no K8s Secret created). SOPS + GitOps: encrypt Secret YAMLs with SOPS (age/KMS) for safe GitOps storage.

**Level 4 - Expert**: HashiCorp Vault integration: Vault Agent Injector (sidecar injection), Vault CSI Driver, or Vault Secrets Operator. Dynamic secrets: Vault generates unique database credentials per request (TTL-based, auto-revoked). Sealed Secrets (Bitnami): encrypt K8s secrets with cluster's public key → safe to commit to Git. cert-manager: auto-rotates TLS certificates and stores in Secrets.

---

## ⚙️ How It Works

### Encryption at Rest (EncryptionConfiguration)

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc: # AES-CBC (primary, used for new secrets)
          keys:
            - name: key1
              secret: <base64-32-byte-key>
      - identity: {} # fallback for reading old unencrypted secrets
```

```bash
# Enable on API Server:
# --encryption-provider-config=/etc/kubernetes/encryption-config.yaml

# Re-encrypt all existing secrets after enabling
kubectl get secrets -A -o json | kubectl replace -f -

# Use KMS plugin for hardware-backed key management
# providers:
# - kms:
#     name: my-kms-plugin
#     endpoint: unix:///var/run/kms-plugin.sock
```

### External Secrets Operator

```yaml
# SecretStore: points to AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secretsmanager
  namespace: my-app
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa # IRSA-annotated SA

---
# ExternalSecret: define what to sync
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: db-credentials # K8s Secret name to create
    creationPolicy: Owner
  data:
    - secretKey: DB_PASSWORD # key in K8s Secret
      remoteRef:
        key: prod/my-app/db # path in AWS Secrets Manager
        property: password # JSON key in SM value
```

### Vault Agent Injector

```yaml
# Annotations trigger sidecar injection
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "my-app"
        vault.hashicorp.com/agent-inject-secret-config: "secret/data/my-app/db"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/data/my-app/db" -}}
          export DB_PASSWORD="{{ .Data.data.password }}"
          {{- end }}
    spec:
      serviceAccountName: my-app # bound to Vault role via K8s auth
      containers:
        - name: app
          command: ["sh", "-c", "source /vault/secrets/config && ./app"]
```

### SOPS + GitOps (Safe Git Storage)

```bash
# Encrypt K8s Secret YAML with age key
sops --encrypt --age age1xxxxxxxx \
  --encrypted-regex '^(data|stringData)$' \
  secret.yaml > secret.enc.yaml

# Commit secret.enc.yaml to Git (encrypted)
# FluxCD/ArgoCD decrypts at apply time using cluster's key

# FluxCD Kustomization with SOPS
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age-key
```

---

## 🔄 E2E Flow: External Secrets Operator

```
AWS Secrets Manager:
  - Path: prod/my-app/db
  - Value: {"password": "s3cr3tP@ss", "host": "db.prod.example.com"}

ExternalSecret CRD applied:
  → External Secrets Operator (using IRSA SA) calls AWS SM API
  → Reads secret from prod/my-app/db
  → Creates K8s Secret "db-credentials" in namespace my-app
  → K8s Secret data:
      DB_PASSWORD = s3cr3tP@ss (base64-encoded)
      DB_HOST = db.prod.example.com

Every 1 hour (refreshInterval):
  → ESO re-reads AWS SM
  → If value changed (password rotation), updates K8s Secret
  → Pod environment: Deployment must restart to pick up new env var
  → OR: mount as volume → auto-updates without restart
```

---

## ⚖️ Comparison Table

|                   | K8s Secret    | K8s Secret + Encryption | External Secrets Operator | Vault Agent              |
| ----------------- | ------------- | ----------------------- | ------------------------- | ------------------------ |
| **Encryption**    | Base64 only   | AES-256 at rest         | Depends on source         | Vault (HSM-backed)       |
| **Audit trail**   | K8s audit log | K8s audit log           | Source + K8s logs         | Vault audit log          |
| **Auto-rotation** | Manual        | Manual                  | ✅ (refreshInterval)      | ✅ (dynamic credentials) |
| **Git-safe**      | ❌            | ❌                      | ✅ (no secret in Git)     | ✅                       |
| **Complexity**    | Low           | Medium                  | Medium                    | High                     |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                   |
| --------------------------------------- | ------------------------------------------------------------------------- |
| "Kubernetes Secrets are encrypted"      | Only base64 by default; need EncryptionConfiguration for real encryption  |
| "env vars are fine for secrets"         | Env vars leak in proc lists, crash dumps, logs; volume mounts are better  |
| "Listing secrets requires extra rights" | Default `edit` ClusterRole can list/get secrets - review carefully        |
| "Sealed Secrets = Vault"                | Sealed Secrets encrypts for Git storage; Vault is full secrets management |

---

## 🚨 Failure Modes

| Failure                          | Symptom                               | Fix                                                                 |
| -------------------------------- | ------------------------------------- | ------------------------------------------------------------------- |
| Secret committed to Git          | Credential exposure                   | Use SOPS/Sealed Secrets; rotate compromised credentials immediately |
| Missing RBAC for SA              | ESO can't read AWS SM                 | Verify IRSA annotation; check IAM policy                            |
| Secret not rotated               | Old password after rotation in AWS SM | Trigger Deployment rollout after ESO sync; or use volume mount      |
| EncryptionConfiguration key lost | All secrets unreadable                | Backup encryption keys separately from cluster                      |

---

## 🔗 Related Keywords

- [Secret](/kubernetes/secret/) - the core Kubernetes Secret object
- [etcd](/kubernetes/etcd/) - where Secrets are stored
- [RBAC (K8s)](/kubernetes/rbac-k8s/) - controls access to Secrets
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) - Secrets handling is critical

---

## 📌 Quick Reference Card

```bash
# Create secret
kubectl create secret generic db-creds \
  --from-literal=password=mysecret \
  --from-file=tls.key=server.key \
  -n my-namespace

# Get secret (decoded)
kubectl get secret db-creds -o jsonpath='{.data.password}' | base64 -d

# Verify encryption at rest is enabled
kubectl get secret db-creds -n default -o yaml
# Check etcd: etcdctl get /registry/secrets/default/db-creds
# If encrypted, value starts with "k8s:enc:aescbc:v1:key1:..."

# External Secrets Operator
kubectl get externalsecrets -A
kubectl describe externalsecret db-credentials -n my-app

# Check secret store status
kubectl get secretstore -n my-app
```

---

## 🧠 Think About This

The secret management architecture choice is one of the most consequential security decisions for your Kubernetes platform. The progression: (1) K8s Secrets → fine for dev. (2) Encryption at rest → minimum for production. (3) External Secrets Operator + AWS SM/Vault → recommended for multi-cluster, with auto-rotation. (4) Vault dynamic secrets → gold standard: credentials exist only for the lifetime of a request, auto-revoked, every credential unique to the workload. Dynamic database credentials (Vault DB secret engine) mean a compromised pod can't reuse credentials after expiry - the blast radius of a breach is limited to the credential's TTL (15 minutes default).
