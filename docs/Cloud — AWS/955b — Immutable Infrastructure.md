---
layout: default
title: "Immutable Infrastructure"
parent: "DevOps & SDLC"
nav_order: 456
permalink: /devops-sdlc/immutable-infrastructure/
---
# 456 — Immutable Infrastructure

`#devops` `#sdlc` `#intermediate` `#reliability`

⚡ TL;DR — Never patch or modify running servers; instead, build a new image and replace the old instance entirely.

| #456 | Category: DevOps & SDLC | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | IaC, CI/CD Pipeline, Containers | |
| **Used by:** | GitOps, IaC, Cloud-Native Architecture | |

---

### 📘 Textbook Definition

Immutable Infrastructure is a deployment paradigm where infrastructure components (servers, containers, VM images) are never modified after they are deployed. Any change requires building a new artifact from scratch, deploying it, and replacing the old one. The old infrastructure is discarded rather than patched, ensuring every running instance is a known, version-controlled artifact.

---

### 🟢 Simple Definition (Easy)

Immutable infrastructure means: **never patch a running server — replace it**. Instead of SSH-ing in and installing a fix, you build a new server image with the fix, deploy it, and kill the old one.

---

### 🔵 Simple Definition (Elaborated)

The alternative to immutable infrastructure is mutable infrastructure — patching running servers over time. Over months, every server accumulates small differences: a package here, a config change there. They become "snowflakes" — unique, unreproducible, and fragile. Immutable infrastructure prevents drift by making servers disposable artifacts, like Docker images: every version is a clean build from a known baseline.

---

### 🔩 First Principles Explanation

**The core problem:**
Patching servers over time creates configuration drift. Two servers that started identical diverge over months of patching. You cannot reproduce a server exactly. "It worked on the staging server" becomes meaningless.

**The insight:**
> "Treat infrastructure like a compiled binary: you don't edit a compiled binary — you recompile. Build, don't patch."

```
Mutable (bad):
  Server v1 --> patch --> patch --> config change --> "unique snowflake"
  Cannot reproduce. Cannot roll back. Cannot trust.

Immutable (good):
  Image v1 → deploy → run
  Need change? → build Image v2 → deploy → replace v1 → terminate v1
  Every instance is traceable to a specific known image version.
```

---

### ❓ Why Does This Exist (Why Before What)

Without immutable infrastructure, configuration drift makes environments unreliable and hard to reproduce. Debugging production is harder because you can't be sure the server is in the state you expect. Security patches applied inconsistently across servers leave some unpatched.

---

### 🧠 Mental Model / Analogy

> Think of deployed servers like printed documents. You don't correct a mistake by scribbling on the printed page — you fix the template and reprint. Similarly, you don't fix a running server by SSHing in — you fix the Dockerfile or image configuration and rebuild. The running instance is immutable; the template is where changes happen.

---

### ⚙️ How It Works (Mechanism)

```
Immutable server approach:

  1. Declare server/image configuration in code
     (Dockerfile, Packer template, Ansible image build)
         ↓
  2. CI/CD builds a new image artifact (Docker image,
     VM ami, etc.) from the declaration
         ↓
  3. New image deployed to replace old instances
     (rolling update, blue-green, or autoscaling)
         ↓
  4. Old instances terminated — no manual changes ever
         ↓
  5. Any future change: repeat from step 1

  Key rule: no SSH in production for configuration changes.
  Only break glass access for emergency diagnostic (read-only).
```

---

### 🔄 How It Connects (Mini-Map)

```
[IaC + Dockerfile declares state]
       ↓
[CI/CD builds new image]
       ↓
[New image deployed (rolling/blue-green)]
       ↓
[Old instances terminated]
       ↓
[GitOps enforces: no drift, no manual changes]
```

---

### 💻 Code Example

```dockerfile
# Immutable Docker image — every change = new image version
FROM eclipse-temurin:21-jre-alpine

# All configuration baked into the image
WORKDIR /app
COPY target/myapp.jar app.jar

# No runtime configuration changes — use env vars for runtime config
ENV SPRING_PROFILES_ACTIVE=production
ENV SERVER_PORT=8080

# Security: run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```yaml
# Kubernetes: immutable pods — no exec/patch in production
# Enforced via PodSecurityPolicy / OPA Gatekeeper

# To update: change image tag → rolling update creates new pods
# Old pods are terminated, never modified
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0     # change this = new immutable pods
        # Never: kubectl exec pod -- apt-get install something
        securityContext:
          readOnlyRootFilesystem: true    # enforce immutability at container level
          allowPrivilegeEscalation: false
```

---

### 🔁 Flow / Lifecycle

```
1. Requirement: update Java version in all app servers
        ↓
2. Update Dockerfile: FROM eclipse-temurin:21-jre-alpine
        ↓
3. Push to git → CI builds new Docker image → tagged v2.1.0
        ↓
4. Image pushed to registry
        ↓
5. CD pipeline deploys new image (rolling update)
        ↓
6. New pods start with updated Java version
        ↓
7. Old pods terminated
        ↓
8. Result: all pods identical, running known image v2.1.0
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Immutable means you can never change anything | Configuration changes go through the build pipeline, not manual patching |
| It's only for containers | Applies to VMs, Lambda functions, and any deployable artifact |
| It makes debugging impossible | Centralized logging + distributed tracing replace SSH-based debugging |
| It wastes resources on rebuilds | Build time is cheap; avoiding snowflakes saves far more time |

---

### 🔥 Pitfalls in Production

**Pitfall 1: App State Written to Instance Disk**
Log files, uploads, or database files stored on the instance disk are lost on replacement.
Fix: externalize all state — logs to centralized logging (ELK/Loki), uploads to object storage (S3), data to managed databases.

**Pitfall 2: Configuration Hardcoded in Image**
Environment-specific config baked into the image breaks the "build once, run anywhere" principle.
Fix: inject configuration at runtime via environment variables, ConfigMaps, or Vault.

**Pitfall 3: No Audit Trail for Emergency SSH**
Teams still SSH in for emergencies but don't track what was changed.
Fix: enforce read-only SSH or bastion host with session recording; any fix must be followed by a proper image rebuild.

---

### 🔗 Related Keywords

- **IaC (Infrastructure as Code)** — the tooling that builds immutable images
- **GitOps** — enforces immutability by reverting any manual cluster changes
- **Docker / Containers** — the primary mechanism for immutable application deployment
- **Blue-Green Deployment** — the ideal release strategy for immutable infrastructure
- **Configuration Drift** — the production problem that immutable infrastructure prevents

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Never modify running infrastructure — build   │
│              │ new, replace old, terminate old               │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Cloud-native, containerized, IaC-driven       │
│              │ environments                                   │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Legacy systems with state on disk that cannot │
│              │ yet be externalised                           │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Build, don't patch — every running instance  │
│              │  is a known, version-controlled artifact"     │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Docker --> IaC --> GitOps --> Twelve-Factor App│
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** How does immutable infrastructure change the approach to debugging production issues?  
**Q2.** What must be externalised from an application before it can be deployed as truly immutable infrastructure?  
**Q3.** How does immutable infrastructure interact with database schema migrations?

