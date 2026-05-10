---
layout: default
title: "K8s Security Hardening"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 65
permalink: /kubernetes/k8s-security-hardening/
id: K8S-065
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  [
    "RBAC (K8s)",
    "Network Policy",
    "Pod Security Standards",
    "Kubernetes Secrets Management",
    "Service Account",
  ]
used_by: ["K8s Upgrade Strategy", "AWS Security Best Practices"]
related:
  [
    "RBAC (K8s)",
    "Network Policy",
    "Pod Security Standards",
    "Admission Controllers",
    "Kubernetes Secrets Management",
    "Service Mesh on K8s",
  ]
tags:
  [
    kubernetes,
    security,
    hardening,
    rbac,
    network-policy,
    pod-security,
    opa,
    k8s,
    cis,
  ]
version: 1
version: 1
---

# K8s Security Hardening

## ⚡ TL;DR

K8s security hardening: **4Cs** (Cloud → Cluster → Container → Code). Cluster: RBAC least privilege, disable anonymous auth, audit logging. Workload: Pod Security Standards (Restricted), `automountServiceAccountToken: false`, read-only root filesystem, drop ALL capabilities. Network: default-deny NetworkPolicy. Secrets: encrypt at rest, use External Secrets Operator. Scan: Trivy, Falco for runtime detection.

---

## 🔥 Problem This Solves

Kubernetes has a large attack surface: API server is publicly accessible by default in managed clusters, RBAC misconfiguration grants too much access, containers run as root, secrets stored in plaintext (base64), and network is flat (any Pod can reach any Pod). Hardening systematically closes each attack vector.

---

## 📘 Textbook Definition

Kubernetes security hardening refers to the systematic process of reducing the attack surface and potential impact of a security compromise in a Kubernetes cluster. It covers authentication, authorization, admission control, network segmentation, container security context, secrets management, and runtime threat detection.

---

## ⏱️ 30 Seconds

```
4C Security Model:
  Cloud (IAM, VPC, node security groups)
    └── Cluster (RBAC, audit logging, API server flags)
          └── Container (securityContext, PSS, image scanning)
                └── Code (SAST, SCA, no hardcoded secrets)

Top K8s attack vectors:
  1. Over-permissive RBAC
  2. Default service accounts with cluster-admin
  3. Privileged containers
  4. Secrets in env vars or unencrypted etcd
  5. Flat network (no NetworkPolicy)
  6. Vulnerable container images
```

---

## 🔩 First Principles

- **Defense in depth**: Multiple layers; one breach ≠ full compromise
- **Least privilege**: minimum permissions for each actor at every layer
- **Immutability**: read-only filesystem prevents post-exploitation persistence
- **Audit trail**: all API server calls logged (who did what, when)
- **Zero trust**: mTLS + AuthorizationPolicy - authenticated AND authorized for every call
- **Admission gates**: policy enforcement before objects enter etcd

---

## 🧪 Thought Experiment

Attacker exploits app vulnerability → Remote Code Execution in container. Without hardening: container runs as root → mounts host filesystem → escalates to node → reads all Pod secrets → accesses cluster-admin ServiceAccount token → owns the cluster. With hardening: runs as nonroot uid 10000 → read-only filesystem → no capability → NetworkPolicy denies outbound C2 → Falco alerts on suspicious process execution. Blast radius: one container.

---

## 🧠 Mental Model / Analogy

K8s security hardening is **layered physical security**: the data center (cloud) has perimeter security. The server room (cluster) has keycard access. The server rack (namespace) has individual locks. The server (container) is bolted down (read-only, non-root). Even if one layer is breached, the next stops the attacker. Audit logs = security cameras recording all access.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Don't run containers as root. Enable Pod Security Standards (namespace label). Set RBAC to least privilege - no cluster-admin bindings for service accounts.

**Level 2 - Practitioner**: NetworkPolicy default-deny. `automountServiceAccountToken: false` for all Pods. Encrypt etcd secrets (`EncryptionConfiguration`). Scan images with Trivy in CI. Enable API server audit logging.

**Level 3 - Advanced**: OPA/Gatekeeper or Kyverno for policy-as-code (enforce standards beyond PSS). Falco for runtime threat detection (unexpected process spawn, file access). seccomp profile (RuntimeDefault or custom). AppArmor profiles. Vulnerability management pipeline (Trivy + SBOM generation). `capabilities: drop: [ALL]` + add only what's needed.

**Level 4 - Expert**: CIS Kubernetes Benchmark (kube-bench). SPIFFE/SPIRE for workload identity across clusters. Kubescape for multi-cluster compliance scanning. Supply chain security: SLSA, Sigstore/Cosign for image signing. Admission webhook: deny unsigned images (Cosign Kubernetes Policy Controller). Ephemeral containers for debugging (no SSH, no exec to prod) - Kyverno policy blocking `kubectl exec` on prod Pods. Secrets rotation automation (ESO + Vault dynamic secrets). kube-audit2rbac: generate minimal RBAC from audit logs.

---

## ⚙️ How It Works

### API Server Hardening Flags

```yaml
# kube-apiserver flags (kubeadm ClusterConfiguration)
apiServerExtraArgs:
  # Disable anonymous authentication
  anonymous-auth: "false"

  # Enable audit logging
  audit-log-path: /var/log/kubernetes/audit.log
  audit-log-maxage: "30"
  audit-log-maxbackup: "3"
  audit-log-maxsize: "100"
  audit-policy-file: /etc/kubernetes/audit-policy.yaml

  # Enable admission controllers
  enable-admission-plugins: "NodeRestriction,PodSecurity,EventRateLimit"

  # Encryption config
  encryption-provider-config: /etc/kubernetes/encryption.yaml
```

### Secure Pod SecurityContext

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      # Pod-level security
      securityContext:
        runAsNonRoot: true
        runAsUser: 10000
        runAsGroup: 10000
        fsGroup: 10000
        seccompProfile:
          type: RuntimeDefault

      # No service account token auto-mount
      automountServiceAccountToken: false

      containers:
        - name: my-service
          image: my-service:v1.5.0@sha256:abc123... # Pin digest

          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
              add: [] # Add ONLY what's needed; usually nothing

          # Writable volumes for temp data
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: var-cache
              mountPath: /var/cache/nginx

      volumes:
        - name: tmp
          emptyDir: {}
        - name: var-cache
          emptyDir: {}
```

### Kyverno Policy-as-Code

```yaml
# Require non-root containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: enforce
  background: true
  rules:
    - name: check-non-root
      match:
        any:
          - resources:
              kinds: [Pod]
              namespaces: ["production", "staging"]
      validate:
        message: "Containers must not run as root"
        pattern:
          spec:
            containers:
              - securityContext:
                  runAsNonRoot: true

---
# Require approved image registries
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: enforce
  rules:
    - name: check-registry
      match:
        any:
          - resources:
              kinds: [Pod]
      validate:
        message: "Only approved registries allowed"
        pattern:
          spec:
            containers:
              - image: "123456789.dkr.ecr.us-east-1.amazonaws.com/* |
                  my-registry.example.com/*"
```

### Default-Deny NetworkPolicy

```yaml
# Deny all ingress and egress by default in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {} # applies to all Pods
  policyTypes:
    - Ingress
    - Egress

---
# Allow specific: my-service can receive from api-gateway
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: my-service-allow
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: my-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - port: 53 # DNS
          protocol: UDP
```

### Falco Runtime Threat Detection

```yaml
# Falco rule: alert on shell spawn in container
- rule: Terminal Shell in Container
  desc: Container started with shell
  condition: >
    evt.type = execve and
    container and
    proc.name in (shell_binaries)
  output: >
    Shell spawned in container
    (user=%user.name container=%container.name
     image=%container.image.repository:%container.image.tag
     cmd=%proc.cmdline)
  priority: WARNING
  tags: [container, shell]

# Falco rule: alert on sensitive file access
- rule: Read Sensitive File
  desc: Attempt to read passwords/keys
  condition: >
    open_read and
    sensitive_files and
    not user_known_read_sensitive_files_activities
  output: >
    Sensitive file opened
    (file=%fd.name user=%user.name container=%container.name)
  priority: ERROR
```

### Image Scanning in CI

```yaml
# GitHub Actions: Trivy scan on PR
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/my-service:${{ env.VERSION }}
    format: "sarif"
    output: "trivy-results.sarif"
    severity: "CRITICAL,HIGH"
    exit-code: "1" # fail build on CRITICAL/HIGH

# Upload to GitHub Security tab
- name: Upload Trivy scan results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: "trivy-results.sarif"
```

---

## 🔄 E2E Flow: CIS Benchmark Compliance Check

```
1. Run kube-bench:
   kubectl apply -f kube-bench-job.yaml

   Output: 50 PASS, 10 FAIL, 20 WARN

   FAIL examples:
   [FAIL] 1.2.6 Ensure anonymous requests are not authorized
   [FAIL] 1.3.1 Ensure profiling is disabled
   [FAIL] 4.2.6 Ensure seccomp profile is set

2. Remediation:
   For 1.2.6: Add --anonymous-auth=false to API server
   For 1.3.1: Add --profiling=false to controller manager
   For 4.2.6: Add seccompProfile: RuntimeDefault to all Pods

3. Re-run kube-bench: 60 PASS, 0 FAIL, 20 WARN
4. Schedule monthly compliance scans (Kubescape / kube-bench)
```

---

## ⚖️ Comparison Table

| Tool               | Category           | When                             |
| ------------------ | ------------------ | -------------------------------- |
| **Kyverno**        | Policy enforcement | Admission-time policy-as-code    |
| **OPA/Gatekeeper** | Policy enforcement | Complex Rego policies            |
| **Falco**          | Runtime detection  | Detecting attacks in progress    |
| **Trivy**          | Image scanning     | CI/CD vulnerability scanning     |
| **kube-bench**     | Compliance         | CIS Benchmark assessment         |
| **Kubescape**      | Compliance         | Multi-cluster NSA/CISA framework |

---

## ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| "RBAC is enough security"                    | RBAC = authorization only; need PSS, NetworkPolicy, runtime detection too                |
| "Namespaces provide security isolation"      | Namespaces = soft isolation; need NetworkPolicy + RBAC for real isolation                |
| "Base64 = encryption"                        | Base64 is encoding; use EncryptionConfiguration + External Secrets for actual encryption |
| "Managed K8s (EKS/GKE) is secure by default" | Cloud manages control plane security; workload and RBAC security is your responsibility  |

---

## 🚨 Failure Modes

| Failure                                | Symptom                                 | Fix                                          |
| -------------------------------------- | --------------------------------------- | -------------------------------------------- |
| Overly strict securityContext          | App crashes (can't write files)         | Add emptyDir for /tmp, /var/run etc          |
| Kyverno enforcing breaks existing pods | Deployments fail with policy violations | Audit mode first, then enforce               |
| NetworkPolicy too strict               | App can't reach database                | Add explicit egress rules for DB port        |
| PSS Restricted breaks legacy apps      | Pods fail admission                     | Start with `warn` or `audit`, then `enforce` |

---

## 🔗 Related Keywords

- [RBAC (K8s)](/kubernetes/rbac-k8s/) - authorization layer
- [Network Policy](/kubernetes/network-policy/) - network segmentation
- [Pod Security Standards](/kubernetes/pod-security-standards/) - workload hardening
- [Admission Controllers](/kubernetes/admission-controllers/) - enforcement point
- [Kubernetes Secrets Management](/kubernetes/kubernetes-secrets-management/) - secrets handling

---

## 📌 Quick Reference Card

```bash
# Check for dangerous RBAC
kubectl get clusterrolebindings -o json | \
  jq '.items[] | select(.roleRef.name == "cluster-admin") | .subjects'

# Find privileged pods
kubectl get pods -A -o json | jq '.items[] |
  select(.spec.containers[].securityContext.privileged == true) |
  .metadata.name'

# Run kube-bench
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job/kube-bench

# Scan image
trivy image myrepo/myimage:latest --severity CRITICAL,HIGH

# List PSS violations (audit mode)
kubectl get events -A | grep "violates PodSecurity"

# Check anonymous auth
kubectl --insecure-skip-tls-verify \
  --server https://api-server:6443 get pods 2>&1 | \
  grep -i forbidden  # should see forbidden, not list of pods
```

---

## 🧠 Think About This

The single most impactful K8s security action is often the simplest: **audit your ClusterRoleBindings for cluster-admin**. Run `kubectl get clusterrolebindings -o json | jq '.items[] | select(.roleRef.name == "cluster-admin")'` - most organizations are shocked to find 5-15 service accounts with cluster-admin. Each one represents a token that, if compromised, allows complete cluster takeover. After fixing that, apply default-deny NetworkPolicy to all production namespaces. These two changes close the most common lateral movement paths without requiring any application changes. Security hardening is not a one-time project - it's a continuous process. Use Kubescape or kube-bench on a schedule to catch configuration drift.
