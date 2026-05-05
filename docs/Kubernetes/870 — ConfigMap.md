---
layout: default
title: "ConfigMap"
parent: "Kubernetes"
nav_order: 870
permalink: /kubernetes/configmap/
number: "0870"
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Deployment", "Namespace (K8s)"]
used_by: ["Centralized Configuration", "Spring Core"]
related:
  [
    "Secret",
    "Deployment",
    "Pod",
    "Centralized Configuration",
    "Namespace (K8s)",
  ]
tags: [kubernetes, configmap, configuration, environment-variables, k8s]
---

# ConfigMap

## ⚡ TL;DR

A ConfigMap stores **non-sensitive** configuration data as key-value pairs. Pods consume it as environment variables or mounted files. Changing a ConfigMap value updates mounted files automatically (within ~60s); env vars require Pod restart.

---

## 🔥 Problem This Solves

Hardcoding configuration (DB URLs, feature flags, log levels) in container images makes them environment-specific. ConfigMaps externalize config from images, enabling the same image to run in dev/staging/prod with different settings.

---

## 📘 Textbook Definition

A ConfigMap is an API object used to store non-confidential data in key-value pairs. Pods can consume ConfigMaps as environment variables, command-line arguments, or as configuration files in a volume.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "INFO"
  DB_URL: "jdbc:postgresql://postgres:5432/mydb"
  application.properties: |
    server.port=8080
    spring.datasource.url=jdbc:postgresql://postgres:5432/mydb
    logging.level.root=INFO
```

Usage:

```yaml
# As env vars
envFrom:
  - configMapRef:
      name: app-config

# As mounted file
volumes:
  - name: config-volume
    configMap:
      name: app-config
volumeMounts:
  - name: config-volume
    mountPath: /config
```

---

## 🔩 First Principles

- ConfigMaps are namespaced resources — same name can exist in different namespaces
- **Not** for secrets (use Secret instead) — ConfigMap data is stored unencrypted in etcd
- Volume-mounted ConfigMaps update automatically (kubelet syncs every ~60s)
- Env var ConfigMaps do NOT update without Pod restart
- Size limit: 1 MiB per ConfigMap

---

## 🧪 Thought Experiment

You want to change log level from INFO to DEBUG in production without redeploying. Mount the ConfigMap as a file, and your app reads it at runtime. Update the ConfigMap → kubelet propagates the new file to all Pods → app detects change (via inotify or polling) → logging level updated. Zero Pod restarts.

---

## 🧠 Mental Model / Analogy

ConfigMaps are like **`.env` files** that Kubernetes manages and injects into containers. Instead of copying `.env` files into each container image, you store them in Kubernetes and mount or inject them at runtime.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: ConfigMap = Kubernetes's way to pass configuration to Pods without baking it into images.

**Level 2 — Practitioner**: Two consumption methods: `envFrom` (all keys as env vars) or `env.valueFrom.configMapKeyRef` (specific key). Volume mounts expose files. Multiple ConfigMaps can be combined.

**Level 3 — Advanced**: Immutable ConfigMaps (`immutable: true`) prevent accidental changes and reduce API Server watch load (controller stops watching immutable resources). ConfigMap naming convention: `<app>-config` per environment (or use namespaces for env separation).

**Level 4 — Expert**: ConfigMap updates with volume mounts: kubelet symlinks (`/config/..data` → `..2024_01_01_12_00_00.123456789`). Atomic update via symlink swap. Apps can use inotify (`WatchedFile` in Spring Boot) to detect changes. Admission webhooks can validate ConfigMap content before creation.

---

## ⚙️ How It Works

### Consumption Methods

**Method 1: All keys as env vars**

```yaml
envFrom:
  - configMapRef:
      name: app-config
# All keys → env vars: LOG_LEVEL=INFO, DB_URL=...
```

**Method 2: Specific key**

```yaml
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: LOG_LEVEL
```

**Method 3: Volume mount (auto-updates)**

```yaml
volumes:
  - name: config-vol
    configMap:
      name: app-config
      items:
        - key: application.properties
          path: application.properties
volumeMounts:
  - name: config-vol
    mountPath: /app/config
    readOnly: true
```

### Spring Boot Auto-Reload

```java
// application.properties (in ConfigMap)
management.endpoint.refresh.enabled=true
// POST /actuator/refresh triggers config reload
// Or use spring-cloud-kubernetes for auto-watch
```

---

## 🔄 E2E Flow: Config Update

```
kubectl edit configmap app-config  # change LOG_LEVEL=DEBUG
  → etcd updated
  → kubelet (on each node) polls ConfigMap (~60s)
  → Kubelet: update symlink /config/..data → new version
  → App using inotify detects file change
  → App reloads config: LOG_LEVEL=DEBUG
  → No Pod restart, no service interruption
```

---

## ⚖️ Comparison Table

|                     | ConfigMap            | Secret                                    |
| ------------------- | -------------------- | ----------------------------------------- |
| **Data type**       | Non-sensitive config | Sensitive data (passwords, tokens)        |
| **Encoding**        | Plain text           | Base64 encoded (not encrypted by default) |
| **RBAC**            | Standard             | Can have stricter access                  |
| **etcd encryption** | Not encrypted        | Can enable encryption at rest             |
| **Example**         | DB_URL, LOG_LEVEL    | DB_PASSWORD, API_KEY                      |

---

## ⚠️ Common Misconceptions

| Misconception                    | Reality                                                             |
| -------------------------------- | ------------------------------------------------------------------- |
| "ConfigMap is encrypted"         | ConfigMap data is plain text in etcd; use Secret for sensitive data |
| "Env var ConfigMaps auto-update" | Only volume-mounted ConfigMaps update automatically                 |
| "ConfigMap can be any size"      | Limit is 1 MiB; use PersistentVolumes for large configs             |
| "ConfigMaps are cluster-scoped"  | ConfigMaps are **namespace-scoped**                                 |

---

## 🚨 Failure Modes

| Failure                     | Symptom                                   | Fix                                     |
| --------------------------- | ----------------------------------------- | --------------------------------------- |
| Missing ConfigMap           | Pod stuck in `CreateContainerConfigError` | Create ConfigMap before Pod             |
| Wrong key name              | Env var not set; app uses default         | Check `kubectl describe pod` for events |
| Large ConfigMap             | ConfigMap creation fails                  | Split config; use PV for large files    |
| Sensitive data in ConfigMap | Security audit failure                    | Move to Secret                          |

---

## 🔗 Related Keywords

- [Secret](/kubernetes/secret/) — for sensitive config data
- [Deployment](/kubernetes/deployment/) — consumes ConfigMaps
- [Centralized Configuration](/microservices/centralized-configuration/) — broader config patterns
- [Pod](/kubernetes/pod/) — uses ConfigMap via env or volume

---

## 📌 Quick Reference Card

```bash
# Create ConfigMap
kubectl create configmap app-config --from-literal=LOG_LEVEL=INFO
kubectl create configmap app-config --from-file=application.properties
kubectl apply -f configmap.yaml

# View
kubectl get configmap app-config -o yaml
kubectl describe configmap app-config

# Edit
kubectl edit configmap app-config

# Make immutable
kubectl patch configmap app-config -p '{"immutable": true}'

# Delete
kubectl delete configmap app-config
```

---

## 🧠 Think About This

Should you use one ConfigMap per application or per environment? One per app (named `<app>-config`) with environment differences handled by namespaces is cleaner than environment-specific ConfigMap names. Namespaces already provide the separation: `default/app-config` for prod, `staging/app-config` for staging — same name, different namespace, different values.
