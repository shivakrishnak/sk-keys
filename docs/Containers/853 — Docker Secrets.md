---
layout: default
title: "Docker Secrets"
parent: "Containers"
nav_order: 853
permalink: /containers/docker-secrets/
number: "0853"
category: Containers
difficulty: ★★★
depends_on: Docker, Container Security, Docker Compose, Dockerfile, Volume Mounts
used_by: CI/CD, Container Security, Image Provenance / SBOM
related: Container Security, Kubernetes Secrets Management, Docker BuildKit, Image Scanning, Distroless Images
tags:
  - containers
  - docker
  - security
  - advanced
  - production
---

# 853 — Docker Secrets

⚡ TL;DR — Docker Secrets provides encrypted, in-memory storage for sensitive data (passwords, tokens, certificates) that containers need at runtime, without exposing them in environment variables or image layers.

| #853 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker, Container Security, Docker Compose, Dockerfile, Volume Mounts | |
| **Used by:** | CI/CD, Container Security, Image Provenance / SBOM | |
| **Related:** | Container Security, Kubernetes Secrets Management, Docker BuildKit, Image Scanning, Distroless Images | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer needs to pass a database password to a containerised application. Options without secrets management: (1) Hardcode in Dockerfile: `ENV DB_PASSWORD=mypassword123` — permanent in image history, visible to anyone who pulls the image; (2) Pass as environment variable: `docker run -e DB_PASSWORD=mypassword123` — visible in `docker inspect`, in shell history, in CI logs; (3) Bake into a config file in the image — same as option 1. All three options expose credentials to anyone with access to the container runtime, the image, or the CI logs.

**THE BREAKING POINT:**
Credentials in environment variables are a major attack vector: container inspect APIs expose all environment variables without authentication on misconfigured systems, CI/CD logs may echo them, and any code running in the container can read its own environment and exfiltrate it. A 2019 Capital One breach involved a compromised environment variable leak. The 2023 CircleCI breach resulted in exposed environment variables.

**THE INVENTION MOMENT:**
This is exactly why Docker Secrets were developed — a mechanism to provide sensitive data to containers as in-memory filesystem entries (`tmpfs`), encrypted at rest in Docker Swarm's Raft log, transmitted encrypted over TLS, and never exposed in environment variables, image histories, `docker inspect` output, or log files.

---

### 📘 Textbook Definition

**Docker Secrets** is a secret management feature in Docker Swarm mode that allows sensitive data (passwords, certificates, API keys, SSH keys) to be stored encrypted in the Swarm manager's Raft log and delivered to authorised service containers as files mounted on `tmpfs` at `/run/secrets/<secret-name>`. Secrets are: encrypted at rest (AES-256-GCM), encrypted in transit (mutual TLS between Swarm nodes), only available to containers explicitly granted access, and never written to any filesystem layer or container history. In `docker-compose`, the `secrets` key provides a similar mechanism for single-host use (backed by tmpfs mounts or external secret backends like Vault, AWS Secrets Manager).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Docker Secrets places credentials in a temporary in-memory file inside the container — not in environment variables, not in the image, not anywhere persistent.

**One analogy:**
> A bank safe delivers valuables to a customer's private room in a sealed envelope. The customer opens the envelope inside the room, uses the contents, and when they leave, the envelope vanishes — no trace. Environment variables are like writing the combination on a whiteboard in the lobby — visible to anyone who walks past. Docker Secrets is the sealed envelope: delivered directly to the authorised recipient, used in private, and leaves no trace on departure.

**One insight:**
The critical insight is the tmpfs mount. Secrets are mounted as temporary in-memory files — they are never written to disk. When the container stops, the secret disappears from memory. This is fundamentally different from environment variables, which exist in multiple system places: `docker inspect` output, `/proc/<pid>/environ`, shell history, and CI logs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Secrets must not appear in image layers (immutable, public, long-lived).
2. Secrets must not appear in environment variables (visible via inspect, environ, logs).
3. Secrets must not be written to any disk layer (prevents forensic recovery).
4. Access to secrets must be scoped: only explicitly authorised services/containers.

**DERIVED DESIGN:**

**Docker Swarm Secrets architecture:**
```
┌──────────────────────────────────────────────────────────┐
│            Docker Swarm Secrets Flow                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Admin: docker secret create db-pass ./db-pass.txt       │
│       ↓                                                  │
│  Swarm manager: encrypts secret (AES-256)                │
│  Stored in Raft log (encrypted at rest)                  │
│       ↓                                                  │
│  docker service create --secret db-pass myapp           │
│  (service is granted access to the secret)               │
│       ↓                                                  │
│  Swarm schedules container on a node                     │
│       ↓                                                  │
│  Swarm manager sends encrypted secret to node            │
│  (via mTLS: Docker Swarm control plane encryption)       │
│       ↓                                                  │
│  Container runtime: mounts secret as tmpfs:              │
│    /run/secrets/db-pass  (640 permissions, root:root)    │
│  (tmpfs = in-memory, never written to disk)              │
│       ↓                                                  │
│  App reads: cat /run/secrets/db-pass → password value    │
│       ↓                                                  │
│  Container stops: tmpfs unmounted → secret gone          │
└──────────────────────────────────────────────────────────┘
```

**Why not environment variables:**

| Property | Environment Variable | Docker Secret |
|---|---|---|
| Image layer | Exposed if in Dockerfile ENV | Never |
| `docker inspect` | Visible | Not visible |
| `/proc/<pid>/environ` | Readable by any process in container | Not in environ |
| CI log exposure | Easy accidental echo | File, no default echo |
| Memory persistence | Entire lifecycle | tmpfs only during run |
| Access control | Implicit (set at run time) | Explicit (service grant) |
| Rotation | Restart required | Live rotation via update |

**Docker Compose secrets:**
In non-Swarm compose, secrets can reference:
- Files: `file: ./secret.txt` — the file is volume-mounted (NOT tmpfs — security limitation)
- External: `external: true` — references a Docker Swarm secret by name

**THE TRADE-OFFS:**

**Gain:** Secrets not in images, not in env vars, encrypted at rest and in transit, access-controlled.

**Cost:** Docker Swarm only for full tmpfs + encryption — Docker Compose file-backed secrets are just bind mounts (less secure). Adds operational overhead (secret lifecycle management). No dynamic rotation without service restart in basic Swarm mode.

---

### 🧪 Thought Experiment

**SETUP:**
A container needs an API key to call a third-party payment service. The key value is `sk-live-abc123xyz456`.

**WHAT HAPPENS WITH ENVIRONMENT VARIABLE:**
`docker run -e PAYMENT_KEY=sk-live-abc123xyz456 myapp` — the key is:
- Visible in `docker inspect` output (accessible to anyone with Docker socket access)
- Readable from inside the container at `/proc/1/environ` — any process in the container can read all environment variables
- Potentially logged in CI/CD system output if the `docker run` command is echoed
- If the container is compromised, the attacker can read `printenv` to get all credentials

**WHAT HAPPENS WITH DOCKER SECRETS:**
`docker secret create payment-key ./payment-key.txt` followed by referencing in service. Inside the container the app reads `/run/secrets/payment-key`. The key:
- Is NOT in `docker inspect` output
- Is NOT in environment variables (NOT in `/proc/1/environ`)
- Is NOT in any image layer
- Lives only in tmpfs — when the container stops, the memory is freed
- Is only available to services explicitly granted `--secret payment-key` access
- The attacker who compromises the container can still read the file at `/run/secrets/payment-key` — but the exposure window closes when the container stops

**THE INSIGHT:**
Docker Secrets doesn't prevent reading by a compromised container process (the container must be able to read the secret to use it). Its value is in preventing leakage through inspection, logs, images, and environment variables — the most common real-world credential leak vectors.

---

### 🧠 Mental Model / Analogy

> A Docker Secret is a sealed envelope slipped under a hotel room door. The hotel management (Swarm) encrypts and stores the envelope securely. At check-in (container start), the envelope is slipped under the door. Inside the room (container), the guest (application) reads the contents. When the guest checks out (container stops), the envelope dissolves — nothing remains. The hotel lobby (docker inspect), the cleaning staff (other containers), and the security cameras (logs) never saw the contents.

Mapping:
- "Sealed envelope" → encrypted secret value
- "Hotel management secure vault" → Swarm Raft encrypted log
- "Slipped under the door" → tmpfs mount to `/run/secrets/`
- "Guest reads contents inside room" → application reads `/run/secrets/secret-name`
- "Envelope dissolves at checkout" → tmpfs unmounted on container stop
- "Hotel lobby never saw contents" → secret not in `docker inspect`, env, or image

Where this analogy breaks down: the hotel guest can photograph the envelope contents. Similarly, a compromised container process can read and exfiltrate the secret file. Docker Secrets protects against passive observers, not against a fully compromised application.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Docker Secrets is a secure way to give your container a password without putting that password in the container's code, settings, or environment. The password is given to the container as a temporary file that only the container can read, and disappears when the container stops.

**Level 2 — How to use it (junior developer):**
In Docker Swarm: `docker secret create my-secret ./secret-file.txt`. Then in the service: `docker service create --secret my-secret myapp`. Inside the container: `cat /run/secrets/my-secret`. In Docker Compose: define secrets under the `secrets:` key and reference them from services. The app reads the secret file path: `os.readFile('/run/secrets/my-secret')`.

**Level 3 — How it works (mid-level engineer):**
Docker Swarm stores secrets in its Raft database (etcd-like distributed log) encrypted with Swarm's internally-managed encryption keys. When a service with a granted secret is scheduled, the Swarm manager sends the decrypted secret value to the worker node over the mTLS-secured Swarm control plane. The container runtime (containerd) mounts the secret as a `tmpfs` filesystem entry at `/run/secrets/<name>` with `640` permissions (readable by root and the container's first user). The secret content is held in kernel memory (RAM), never written to any storage layer. When the container exits, the tmpfs is unmounted and the memory freed.

**Level 4 — Why it was designed this way (senior/staff):**
The tmpfs mount design was a deliberate choice: tmpfs lives entirely in kernel memory, never synced to disk, never visible in the container filesystem union (not a layer), and cleaned up automatically on unmount. This satisfies the key threat model: secrets should not survive container lifecycle events in any recoverable storage. The Swarm Raft log was extended to store secrets because Raft provides consensus, replication, and encrypted-at-rest storage — exactly what secret management requires. The decision to use file-based delivery (rather than environment injection) was informed by the well-known risks of environment variables in Linux: they appear in `/proc/<pid>/environ` (readable by all processes in the container), in `ps auxe` output historically, and are trivially echoed in scripts. Files in `/run/secrets/` require an explicit `cat` or `open()` call. For Kubernetes, the equivalent is `Secret` objects mounted as volume files — the same design philosophy. Kubernetes Secrets are critiqued for base64-encoding (not encryption) by default; Sealed Secrets and External Secrets Operator (ESO) with Vault/AWS SM are the production-grade extensions.

---

### ⚙️ How It Works (Mechanism)

**Docker Swarm secret lifecycle:**
```
┌──────────────────────────────────────────────────────────┐
│            Docker Secret Lifecycle                       │
├──────────────────────────────────────────────────────────┤
│  1. Create: docker secret create name ./file             │
│     → file content encrypted (AES-256-GCM)               │
│     → stored in Swarm Raft log                           │
│     → original file: you should shred it                 │
│                                                          │
│  2. Grant: docker service create --secret name svc       │
│     → service spec references secret by name             │
│                                                          │
│  3. Schedule: Swarm places task on node                  │
│     → manager sends secret to node (mTLS)               │
│     → worker decrypts in memory                          │
│     → runtime mounts as tmpfs /run/secrets/<name>        │
│                                                          │
│  4. Runtime: app reads /run/secrets/<name>               │
│     → file permissions: 640 (root:root read)             │
│     → content: raw bytes of secret value                 │
│                                                          │
│  5. Rotation: docker secret create name-v2 ./new-file    │
│     → docker service update --secret-rm name \          │
│          --secret-add name-v2 svc                        │
│     → tasks restart with new secret                      │
│                                                          │
│  6. Container stop: tmpfs unmounted → memory freed       │
│     → secret no longer accessible on host               │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Admin creates secret: docker secret create db-pass ./pass.txt
  → Raft log: encrypted db-pass entry
  → Service deploy with --secret db-pass
  → Container start: /run/secrets/db-pass mounted (tmpfs)
  → App reads /run/secrets/db-pass ← YOU ARE HERE
  → App connects to DB with read password
  → Container stops: tmpfs unmounted
```

**FAILURE PATH:**
```
Secret referenced but not granted to service:
  → docker service create --secret non-existent svc
  → Error: secret non-existent not found
  → fix: docker secret create the secret first
  → docker service update --secret-add name svc
```

**WHAT CHANGES AT SCALE:**
At scale with hundreds of services and thousands of containers, secret rotation becomes operational overhead: `docker service update --secret-rm old --secret-add new` triggers a rolling restart of all service tasks. Secret rotation automation (Vault dynamic secrets, AWS Secrets Manager automatic rotation) is required at scale to handle credential rotation without manual intervention.

---

### 💻 Code Example

**Example 1 — Docker Swarm secrets:**
```bash
# Create a secret from a file (file should be created securely)
echo "supersecretpassword" | docker secret create db-password -
# '-' reads from stdin

# Create service with secret access
docker service create \
  --name myapp \
  --secret db-password \
  myapp:latest

# Inside container: read the secret
# cat /run/secrets/db-password
# Output: supersecretpassword
```

**Example 2 — Docker Compose secrets (dev):**
```yaml
# docker-compose.yml
version: '3.9'
services:
  myapp:
    image: myapp:latest
    secrets:
      - db_password     # readable at /run/secrets/db_password
    environment:
      - DB_HOST=postgres

  postgres:
    image: postgres:15
    secrets:
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password  # postgres reads from file

secrets:
  db_password:
    file: ./secrets/db_password.txt  # local dev: file-backed
    # production Swarm: external: true
```

**Example 3 — Application reading secrets:**
```javascript
// Node.js: read secret from file
const fs = require('fs');

function getSecret(name) {
  const secretPath = `/run/secrets/${name}`;
  try {
    return fs.readFileSync(secretPath, 'utf8').trim();
  } catch {
    // Fallback to env var for local development
    return process.env[name.toUpperCase()];
  }
}

const dbPassword = getSecret('db_password');
```

```java
// Java: read secret from file
import java.nio.file.Files;
import java.nio.file.Path;

String dbPassword = Files.readString(
    Path.of("/run/secrets/db_password")
).strip();
```

**Example 4 — Secret rotation:**
```bash
# Rotate a secret: create v2, update service to use v2
echo "newpassword123" | docker secret create db-password-v2 -

docker service update \
  --secret-rm db-password \
  --secret-add source=db-password-v2,target=db-password \
  myapp
# Rolling restart of service tasks with new secret
# --source=v2: which secret to use; --target=db-password: same path in container

# Clean up old secret after rotation verified
docker secret rm db-password
```

---

### ⚖️ Comparison Table

| Secret Storage | Encryption At Rest | Env Var Exposure | Rotation | Auditability | Best For |
|---|---|---|---|---|---|
| **Docker Secrets (Swarm)** | Yes (AES-256) | No | Manual (service update) | Basic | Docker Swarm production |
| Kubernetes Secrets | No (base64 only!) | No (if mounted as file) | Manual | etcd audit log | K8s (supplement with ESO) |
| HashiCorp Vault | Yes (AES-256-GCM) | No | Automatic (dynamic) | Full audit trail | Enterprise multi-platform |
| AWS Secrets Manager | Yes (KMS) | No | Automatic (rotation lambda) | CloudTrail | AWS-native workloads |
| Environment Variables | No | Yes | Restart required | None | Local dev only |

How to choose: Docker Secrets for Docker Swarm production. Vault or AWS/GCP Secrets Manager for enterprise/multi-platform. Kubernetes secrets only as a transport layer — encrypt with KMS and use External Secrets Operator for production-grade security.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Docker Secrets prevents a compromised container from reading the credential" | No. A compromised container process can still `cat /run/secrets/db-password`. Docker Secrets prevents passive leakage (logs, inspect, images) — not active exfiltration by malicious code inside the container. |
| "Docker Compose secrets are as secure as Swarm secrets" | File-backed Docker Compose secrets (`file: ./secret.txt`) are bind-mounted from the host filesystem — NOT tmpfs. They are written to disk (albeit a local file). Swarm-backed secrets use encrypted Raft storage + tmpfs delivery. |
| "Kubernetes Secrets are encrypted at rest by default" | By default, Kubernetes Secrets are stored as base64-encoded plaintext in etcd. Enabling encryption at rest via KMS is an explicit configuration step. |
| "Environment variables in containers are secure" | Environment variables are readable from `/proc/<pid>/environ` by any process in the container, visible in `docker inspect`, and can appear in CI logs. They are not secure secret storage. |
| "Rotating a Docker Swarm secret is instant and non-disruptive" | Secret rotation via `docker service update --secret-rm old --secret-add new` triggers a rolling restart of all service tasks. Applications must handle graceful restart. Process is not instantaneous. |

---

### 🚨 Failure Modes & Diagnosis

**Secret not available at expected path**

**Symptom:**
App fails to start: `FileNotFoundException: /run/secrets/db-password not found`.

**Root Cause:**
Secret not granted to service, or secret name mismatch between `docker service create --secret` and the path the app reads.

**Diagnostic Command / Tool:**
```bash
# Check which secrets are mounted in container
docker exec <container-id> ls -la /run/secrets/

# Check service secrets
docker service inspect myapp --format '{{.Spec.TaskTemplate.ContainerSpec.Secrets}}'
```

**Fix:**
```bash
# Add missing secret to service
docker service update --secret-add db-password myapp
```

**Prevention:**
Document exactly which secrets each service requires. Add startup validation: if `/run/secrets/required-secret` doesn't exist, exit 1 with a clear error message before binding ports.

---

**Secret value contains trailing newline causing auth failures**

**Symptom:**
Authentication fails despite correct-looking password. DB driver reports "authentication failed" with credentials that look correct in logs.

**Root Cause:**
Secret file has a trailing newline (`\n`). App reads it literally including the newline character, passing `"password\n"` to the auth layer.

**Diagnostic Command / Tool:**
```bash
# Check for trailing newline
docker exec <container> xxd /run/secrets/db-password | tail -2
# Look for 0x0a (newline) at end of file
```

**Fix:**
Application should always trim/strip when reading secret files:
```python
password = open('/run/secrets/db-password').read().strip()
```

**Prevention:**
Create secrets without trailing newlines: `printf "password" | docker secret create db-password -` (printf vs echo — no trailing newline).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — secrets are a Docker feature; understand Docker basics first
- `Container Security` — secrets management is a critical layer of container security
- `Volume Mounts` — secrets are implemented as tmpfs volume mounts under the hood

**Builds On This (learn these next):**
- `Kubernetes Secrets Management` — the equivalent Kubernetes primitive (with Vault/ESO extensions)
- `Container Security` — secrets management is one dimension of the full container security model
- `CI/CD` — secrets management in CI/CD pipelines follows the same principles

**Alternatives / Comparisons:**
- `Container Security` — broader security context in which Docker Secrets is one tool
- `Docker BuildKit` — BuildKit's `--mount=type=secret` for build-time secrets (different from runtime Docker Secrets)
- `Kubernetes Secrets Management` — equivalent and extended concept in Kubernetes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Encrypted, in-memory file delivery of     │
│              │ credentials to Docker containers          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Credentials in env vars/images: visible   │
│ SOLVES       │ in inspect, logs, history, CI output      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ tmpfs = in-memory, zero disk writes.      │
│              │ Secret appears only inside running        │
│              │ container. Vanishes on container stop.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any secret a container needs at runtime:  │
│              │ DB passwords, API keys, TLS certs         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use env vars for production secrets │
│              │ Never hardcode in Dockerfile              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security vs operational complexity        │
│              │ (secret rotation requires service update) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Secrets live in memory, not in images,   │
│              │  not in env vars, and vanish at exit"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Kubernetes Secrets Management →           │
│              │ HashiCorp Vault → Container Security      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A compliance requirement mandates that every access to a production database password must be logged, with: timestamp, which service accessed it, which user/role authorised the access, and the requesting container's identity. Docker Secrets provides delivery but no access logging. Design a secret management architecture using HashiCorp Vault that satisfies all four audit requirements — describe exactly where and how each audit record is generated, stored, and retained, and identify which Vault features provide each property.

**Q2.** Your application uses a database password stored as a Docker Secret. The password must be rotated every 90 days (compliance requirement). Rotation involves: generating a new password, updating the database to accept both old and new passwords, updating the Docker Secret, and retiring the old password once no containers use it. Design a zero-downtime rotation procedure: trace every step, specify the exact Docker commands, identify the window during which both old and new passwords must be accepted by the database, and explain why a rolling restart of the service is or is not safe to perform during rotation.

