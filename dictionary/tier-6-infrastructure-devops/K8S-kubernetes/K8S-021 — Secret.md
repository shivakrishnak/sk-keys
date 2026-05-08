---
layout: default
title: "Secret"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /kubernetes/secret/
id: K8S-021
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "ConfigMap", "RBAC (K8s)"]
used_by: ["Kubernetes Secrets Management", "Service Account", "mTLS"]
related:
  [
    "ConfigMap",
    "RBAC (K8s)",
    "Kubernetes Secrets Management",
    "Service Account",
    "Pod",
  ]
tags: [kubernetes, secret, credentials, tls, k8s, security]
---

# Secret

## ⚡ TL;DR

A Kubernetes **Secret** stores sensitive data (passwords, tokens, TLS certs) as base64-encoded values. Base64 is NOT encryption — Secrets need **encryption at rest** (etcd) + **RBAC** + **least privilege** to be secure. Consider HashiCorp Vault for production-grade secrets management.

---

## 🔥 Problem This Solves

Passwords and tokens can't be in ConfigMaps (plain text in etcd) or container images (visible in `docker history`). Secrets provide a dedicated resource with stricter access controls and optional encryption at rest.

---

## 📘 Textbook Definition

Secrets let you store and manage sensitive information, such as passwords, OAuth tokens, and SSH keys. Storing confidential information in a Secret is safer and more flexible than putting it verbatim in a Pod definition or container image.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData: # auto-base64-encoded on creation
  DB_PASSWORD: "s3cur3pass!"
  API_KEY: "sk-abc123..."
---
# Consume in Pod
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: DB_PASSWORD

# Or mount as file
volumes:
  - name: secrets
    secret:
      secretName: db-secret
volumeMounts:
  - name: secrets
    mountPath: /secrets
    readOnly: true
```

---

## 🔩 First Principles

- Secrets are base64-encoded in etcd — NOT encrypted by default
- Encryption at rest requires `EncryptionConfiguration` in API Server or a KMS provider
- Secrets only sent to nodes that need them (Pods requesting them)
- Secrets are in memory on nodes (tmpfs mount) — not written to disk
- RBAC `get` on a Secret = full access to its value — keep strict RBAC on Secrets

---

## 🧪 Thought Experiment

You create a Secret with a DB password. A developer with `kubectl get secret db-secret -o yaml` access can see the base64 value and decode it in seconds. "Base64" ≠ "secret." Real security requires: RBAC (restrict who can `get`), encryption at rest (etcd), audit logging (who accessed what), and ideally externalizing to Vault.

---

## 🧠 Mental Model / Analogy

Kubernetes Secrets are like a **locked filing cabinet** with the key hanging next to it (base64). The lock keeps casual browsers out, but anyone who knows to look for the key can get in. For real security, you need the key to be held by a security guard (external secret manager like Vault, AWS Secrets Manager).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Secrets store passwords and tokens. Use them instead of ConfigMaps for sensitive data.

**Level 2 — Practitioner**: Three built-in types: `Opaque` (generic), `kubernetes.io/tls` (TLS certs), `kubernetes.io/service-account-token`. Use `stringData` to avoid manual base64 encoding.

**Level 3 — Advanced**: Enable etcd encryption: `EncryptionConfiguration` with AES-CBC or AES-GCM. Use KMS (AWS KMS, GCP KMS) as the encryption provider for envelope encryption. `ExternalSecrets` operator syncs secrets from Vault/AWS SM/GCP SM to Kubernetes Secrets.

**Level 4 — Expert**: Sealed Secrets (Bitnami) encrypt Secret values with a cluster-specific key — safe to commit to Git. CSI Secret Store Driver (Vault/AWS SM) injects secrets directly to Pod filesystem without Kubernetes Secret object. Avoid environment variable injection (visible in `docker inspect`); prefer volume mounts (in-memory tmpfs).

---

## ⚙️ How It Works

### Secret Types

| Type                                  | Use                                   |
| ------------------------------------- | ------------------------------------- |
| `Opaque`                              | Generic key-value (passwords, tokens) |
| `kubernetes.io/tls`                   | TLS certificates                      |
| `kubernetes.io/dockerconfigjson`      | Image pull credentials                |
| `kubernetes.io/service-account-token` | Service account tokens                |
| `kubernetes.io/ssh-auth`              | SSH keys                              |

### TLS Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-cert
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

### Image Pull Secret

```bash
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass

# In Pod spec:
spec:
  imagePullSecrets:
  - name: regcred
```

### Encryption at Rest (EncryptionConfiguration)

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources: [secrets]
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {} # fallback for unencrypted
```

---

## 🔄 E2E Flow: Secret Access

```
Secret stored in etcd (base64, optionally encrypted)
  → Pod scheduled on Node-2
  → kubelet: fetches Secret from API Server (HTTPS)
  → Creates in-memory tmpfs volume at /secrets/
  → Mounts tmpfs into container
  → App reads /secrets/DB_PASSWORD
  → Secret value never written to disk on node
  → Pod deleted → tmpfs unmounted → Secret value gone from node
```

---

## ⚖️ Comparison Table

|                     | Kubernetes Secret          | HashiCorp Vault            | AWS Secrets Manager |
| ------------------- | -------------------------- | -------------------------- | ------------------- |
| **Encryption**      | Optional (config required) | Built-in AES               | Built-in            |
| **Dynamic secrets** | ❌                         | ✅ (auto-rotate DB creds)  | ✅                  |
| **Audit log**       | K8s audit logs             | Vault audit log            | CloudTrail          |
| **Rotation**        | Manual                     | Automatic                  | Automatic           |
| **Complexity**      | Low                        | High                       | Medium              |
| **Cost**            | Free                       | OSS free / Enterprise paid | Per-secret charge   |

---

## ⚠️ Common Misconceptions

| Misconception                 | Reality                                                            |
| ----------------------------- | ------------------------------------------------------------------ |
| "Secrets are encrypted"       | Secrets are base64 only by default — enable encryption at rest     |
| "base64 = encryption"         | base64 is encoding, not encryption — trivially reversible          |
| "Env var secrets are safe"    | Visible in `docker inspect`, proc filesystem; prefer volume mounts |
| "Deleting Pod deletes Secret" | Secrets are independent objects; must be deleted separately        |

---

## 🚨 Failure Modes

| Failure             | Symptom                      | Fix                                                      |
| ------------------- | ---------------------------- | -------------------------------------------------------- |
| Secret not found    | `CreateContainerConfigError` | Create Secret before Pod                                 |
| Wrong key name      | App crashes; env var empty   | Check `kubectl describe pod` for events                  |
| Secret rotated      | App uses stale value         | Use volume mount (auto-updates) instead of env var       |
| Too permissive RBAC | All devs can read secrets    | Least privilege: only service accounts that need secrets |

---

## 🔗 Related Keywords

- [ConfigMap](/kubernetes/configmap/) — for non-sensitive config
- [Kubernetes Secrets Management](/kubernetes/kubernetes-secrets-management/) — advanced patterns
- [RBAC (K8s)](/kubernetes/rbac-k8s/) — access control for Secrets
- [Service Account](/kubernetes/service-account/) — Pod identity for Secret access
- [mTLS](/kubernetes/mtls/) — TLS Secrets for mutual auth

---

## 📌 Quick Reference Card

```bash
# Create Secret
kubectl create secret generic db-secret \
  --from-literal=DB_PASSWORD=s3cure!

# View (base64 encoded)
kubectl get secret db-secret -o yaml

# Decode value
kubectl get secret db-secret -o jsonpath='{.data.DB_PASSWORD}' | base64 -d

# Create TLS Secret
kubectl create secret tls my-tls \
  --cert=server.crt --key=server.key

# List secrets
kubectl get secrets

# Delete
kubectl delete secret db-secret
```

---

## 🧠 Think About This

Kubernetes Secrets solve the "password in ConfigMap" problem but introduce a "password in etcd" problem. The real security journey: ConfigMap (bad) → Secret without encryption (better) → Secret with etcd encryption (good) → External Secrets Operator + Vault (best). For most production environments, using the `external-secrets` operator to sync secrets from AWS Secrets Manager or Vault into Kubernetes Secrets gives you the best of both worlds: strong secret management + standard Kubernetes consumption patterns.
