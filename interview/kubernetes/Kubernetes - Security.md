---
title: "Kubernetes - Security"
topic: Kubernetes
subtopic: Security
keywords:
  - RBAC
  - Pod Security Standards
  - Service Account
  - Admission Controllers
  - Network Policy Security
  - Cluster Security
difficulty_range: hard
status: complete
version: 1
---

# RBAC

**TL;DR** - Role-Based Access Control (RBAC) in Kubernetes restricts API operations by binding roles (sets of permissions) to users, groups, or service accounts - implementing least-privilege access at namespace or cluster level.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every user and service account has full cluster-admin access. A developer can accidentally delete production namespaces. A compromised pod can read all secrets across the cluster. No audit trail of who did what.

**THE INVENTION MOMENT:**
"This is exactly why Kubernetes RBAC was created."

---

### Textbook Definition

RBAC is an authorization mechanism that regulates access to Kubernetes resources based on the roles of individual users or service accounts. It uses four objects: Role (namespace permissions), ClusterRole (cluster-wide permissions), RoleBinding (assigns Role to subject), and ClusterRoleBinding (assigns ClusterRole to subject).

---

### How It Works

```yaml
# Role: what can be done (namespace-scoped)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list"]

---
# RoleBinding: who gets the role
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: production
  name: dev-pod-reader
subjects:
  - kind: Group
    name: developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

---
# ClusterRole for cluster-wide permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
    # NEVER give list on secrets cluster-wide!
```

```
RBAC Model:
  Subject (who)      + Role (what)     = Access
  User/Group/SA        verbs+resources

  Namespace scope:   Role + RoleBinding
  Cluster scope:     ClusterRole + ClusterRoleBinding

  Built-in roles:
    cluster-admin:  Everything (GOD mode)
    admin:          Full access within namespace
    edit:           Read/write most resources
    view:           Read-only access
```

---

### Quick Recall

**If you remember only 3 things:**

1. Four objects: Role (what, namespace), ClusterRole (what, cluster), RoleBinding (who+what, namespace), ClusterRoleBinding (who+what, cluster)
2. Principle of least privilege: start with no access, add only what's needed. Never give cluster-admin to applications.
3. Use `kubectl auth can-i --list --as=system:serviceaccount:ns:sa` to audit what a service account can do

**Interview one-liner:**
"RBAC implements least-privilege by binding Roles (namespace-scoped permission sets) to subjects via RoleBindings - I define fine-grained roles per team/service, avoid cluster-admin for apps, audit with `can-i`, and use ClusterRoles only for cross-namespace resources like nodes and PVs."

---

### Interview Deep-Dive

**Q1: A developer says they can't deploy to production. How do you debug RBAC?**

_Why they ask:_ Tests practical troubleshooting and RBAC mental model.

**Answer:**

```bash
# Check what they can do
kubectl auth can-i create deployments \
  -n production --as=developer@company.com

# List all their permissions in namespace
kubectl auth can-i --list \
  -n production --as=developer@company.com

# Find their bindings
kubectl get rolebindings -n production \
  -o wide | grep -i developer

# Check group membership
kubectl get clusterrolebindings -o wide \
  | grep developers-group
```

Common causes:

1. **Wrong namespace** in RoleBinding (binding exists in `default` not `production`)
2. **Group name mismatch** between IdP and binding subject
3. **Missing verb** (has `get`/`list` but not `create`/`update`)
4. **Missing apiGroup** (resources: deployments needs apiGroups: ["apps"], not [""])
5. **Aggregate ClusterRoles** not including the needed role

---

---

# Pod Security Standards

**TL;DR** - Pod Security Standards (PSS) define three levels (Privileged, Baseline, Restricted) of security policies enforced at namespace level, replacing the deprecated PodSecurityPolicy to prevent pods from running as root, accessing host, or using dangerous capabilities.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Any pod can run as root, mount host filesystem, share host network, and access every Linux capability. A single container escape means full node compromise. No default security posture.

---

### Textbook Definition

Pod Security Standards define three progressive security levels (Privileged, Baseline, Restricted) that are enforced by the Pod Security Admission controller at namespace level, controlling what security contexts pods may use - restricting root execution, privilege escalation, volume types, and Linux capabilities.

---

### How It Works

```yaml
# Enforce restricted security on namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # Enforce: reject non-compliant pods
    pod-security.kubernetes.io/enforce: restricted
    # Warn: allow but warn on baseline violations
    pod-security.kubernetes.io/warn: restricted
    # Audit: log violations
    pod-security.kubernetes.io/audit: restricted

---
# Compliant pod (restricted level)
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: myapp:1.0
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
        runAsUser: 1000
```

```
Three levels:
  Privileged:  No restrictions (system infra only)
  Baseline:    Prevents known privilege escalations
               (no hostNetwork, no hostPID, no privileged)
  Restricted:  Heavily restricted
               (non-root, drop ALL caps, read-only root,
                seccomp, no host anything)

Enforcement modes per namespace:
  enforce: Reject pod creation
  warn:    Allow but show warning
  audit:   Allow but log to audit log

Migration strategy:
  1. Start with audit: restricted (see violations)
  2. Move to warn: restricted (alert teams)
  3. Finally enforce: restricted (reject violators)
```

---

### Quick Recall

**If you remember only 3 things:**

1. Three levels: Privileged (anything goes), Baseline (no known exploits), Restricted (hardened). Apply at namespace via labels.
2. Use `enforce: restricted` for production workloads. Use `enforce: privileged` only for system namespaces (kube-system).
3. Replaces deprecated PodSecurityPolicy (removed in K8s 1.25). Applied via namespace labels, not separate policy objects.

**Interview one-liner:**
"Pod Security Standards enforce security posture at namespace level via three progressive profiles - I use `restricted` enforcement for production (non-root, drop-all-caps, read-only-root, seccomp) with a graduated rollout starting with audit mode to identify violations before enforcing."

---

---

# Service Account

**TL;DR** - Service Accounts provide identity for pods to authenticate with the Kubernetes API and external services, enabling RBAC-based access control for workloads and integration with cloud IAM via workload identity.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
All pods in a namespace share the default service account, which may have excessive permissions. No workload identity for external service authentication. No way to differentiate "this pod should read secrets" from "this pod should only list pods."

---

### Textbook Definition

A ServiceAccount provides an identity for processes running in a Pod to authenticate with the Kubernetes API server. Pods are assigned a ServiceAccount (default if unspecified) whose token is auto-mounted and can be bound to RBAC roles. Since K8s 1.24, tokens are short-lived bound tokens (not long-lived secrets).

---

### How It Works

```yaml
# Create dedicated service account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
  annotations:
    # AWS IAM Role for Service Accounts (IRSA)
    eks.amazonaws.com/role-arn: >-
      arn:aws:iam::123456:role/app-role

---
# Pod uses the service account
spec:
  serviceAccountName: app-sa
  automountServiceAccountToken: false # If no K8s API access
  containers:
    - name: app
      image: myapp:1.0

---
# RBAC for the service account
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-sa-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: production
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
```

```
Best practices:
  1. One ServiceAccount per workload (not shared)
  2. automountServiceAccountToken: false if pod
     doesn't need K8s API access
  3. Use workload identity (IRSA/GKE WI) for
     cloud access instead of storing credentials
  4. Short-lived tokens (default since 1.24)
     instead of long-lived secrets
```

---

### Quick Recall

**If you remember only 3 things:**

1. Every pod gets a service account (default if unspecified). Create dedicated SAs with least-privilege RBAC.
2. `automountServiceAccountToken: false` - disable token mount if pod doesn't need K8s API access (reduces attack surface)
3. Workload identity (AWS IRSA, GKE Workload Identity) lets pods assume cloud IAM roles without storing credentials

**Interview one-liner:**
"Service Accounts provide workload identity for RBAC - I create dedicated SAs per application with minimal permissions, disable auto-mount when K8s API access isn't needed, and use IRSA/Workload Identity for cloud service authentication instead of storing credentials in Secrets."

---

---

# Admission Controllers

**TL;DR** - Admission Controllers intercept API requests after authentication/authorization but before persistence, allowing mutation (adding sidecars, defaults) and validation (policy enforcement, security checks) of resources.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
RBAC says "user CAN create a pod" but can't say "pod MUST have resource limits" or "pod MUST NOT use latest tag" or "automatically inject sidecar proxy." You need a hook between authorization and object creation.

---

### Textbook Definition

Admission Controllers are plugins that intercept requests to the Kubernetes API server after the request is authenticated and authorized but before the object is persisted. They can mutate objects (MutatingAdmissionWebhook), validate them (ValidatingAdmissionWebhook), or both.

---

### How It Works

```
API Request Flow:
  Client -> Authentication -> Authorization (RBAC)
    -> Mutating Admission (modify request)
      -> Object Schema Validation
        -> Validating Admission (accept/reject)
          -> etcd (persist)

Built-in controllers:
  LimitRanger:        Enforce default resource limits
  ResourceQuota:      Enforce namespace resource quotas
  PodSecurity:        Enforce Pod Security Standards
  MutatingWebhook:    Call external webhook to modify
  ValidatingWebhook:  Call external webhook to validate

External policy engines (via webhooks):
  OPA/Gatekeeper:  Rego policies
  Kyverno:         YAML-native policies
  Datree:          Best-practice enforcement
```

```yaml
# Kyverno policy: require resource limits
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-limits
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-limits
      match:
        resources:
          kinds: ["Pod"]
      validate:
        message: "CPU and memory limits required"
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"
```

---

### Quick Recall

**If you remember only 3 things:**

1. Mutating admission modifies objects (inject sidecars, add labels/defaults). Validating admission accepts/rejects (enforce policies).
2. Order: AuthN -> AuthZ -> Mutating -> Schema -> Validating -> Persist. Mutating runs first so validators see final state.
3. Policy engines (Kyverno, OPA Gatekeeper) use admission webhooks for guardrails: require labels, block latest tag, enforce limits, restrict registries.

**Interview one-liner:**
"Admission controllers intercept API requests post-authorization for mutation (injecting sidecars, adding defaults) and validation (enforcing policies like resource limits, image registries, security contexts) - I use Kyverno or OPA Gatekeeper for organizational policies as code."

---

---

# Network Policy Security

**TL;DR** - Network Policy Security implements defense-in-depth microsegmentation by combining default-deny policies, namespace isolation, and explicit allow rules to prevent lateral movement from compromised pods.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Default Kubernetes networking allows all pod-to-pod communication. A compromised frontend can scan the network, access databases, read secrets from other namespaces, and exfiltrate data. One breach = full cluster access.

---

### How It Works

```yaml
# Step 1: Default deny ALL traffic in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
  # Empty rules = deny all

---
# Step 2: Allow specific paths
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080

---
# Step 3: Allow DNS egress (required!)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

```
Defense-in-depth layers:
  1. Default deny (zero trust baseline)
  2. Explicit ingress rules (who can reach what)
  3. Explicit egress rules (what can reach outside)
  4. DNS pinning (only CoreDNS allowed)
  5. Namespace isolation (cross-namespace denied)

Common mistake:
  Default deny without DNS egress rule
  -> All DNS resolution breaks
  -> All services fail to find each other
  -> Always allow UDP 53 to kube-system
```

---

### Quick Recall

**If you remember only 3 things:**

1. Start with default-deny for both ingress AND egress in every namespace (zero trust)
2. Always allow DNS egress (UDP 53 to kube-system) or everything breaks
3. CNI must support Network Policies (Calico, Cilium). Flannel alone does NOT enforce them.

**Interview one-liner:**
"I implement network microsegmentation with default-deny in all namespaces, then explicitly allow required communication paths - frontend to backend, backend to database - always including DNS egress, enforced by Calico or Cilium, and verified with connectivity testing tools."

---

---

# Cluster Security

**TL;DR** - Kubernetes cluster security is a layered approach combining API server hardening, etcd encryption, node security, image security, runtime protection, and audit logging to defend the entire attack surface.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Attack surface is enormous: API server, etcd, kubelet, container runtime, supply chain, network, credentials. A single misconfiguration (anonymous auth, unencrypted etcd, exposed kubelet) compromises the entire cluster.

---

### How It Works

```
Cluster Security Layers:

1. API Server Hardening:
   - Anonymous auth disabled
   - OIDC authentication (no static tokens)
   - Audit logging enabled
   - TLS everywhere

2. etcd Security:
   - Encryption at rest (EncryptionConfiguration)
   - mTLS between API server and etcd
   - Restrict etcd access (not exposed externally)

3. Node Security:
   - Minimal OS (Bottlerocket, Talos)
   - CIS benchmarks applied
   - kubelet authentication required
   - Read-only kubelet port disabled

4. Image Security:
   - Signed images (cosign, Notary)
   - Registry allowlisting (admission controller)
   - Vulnerability scanning (Trivy, Grype)
   - No latest tag in production

5. Runtime Security:
   - Seccomp profiles (restrict syscalls)
   - AppArmor/SELinux profiles
   - Falco for runtime anomaly detection
   - Read-only root filesystem

6. Supply Chain:
   - SBOM generation
   - Dependency scanning
   - Provenance verification (SLSA)
```

```yaml
# etcd encryption at rest
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources: ["secrets"]
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-key>
      - identity: {} # Fallback for reading old data
```

---

### Quick Recall

**If you remember only 3 things:**

1. Defense in depth: no single control is sufficient. Layer API security, network, runtime, and supply chain controls.
2. CIS Kubernetes Benchmark: automated with kube-bench. Run regularly. Fix critical findings immediately.
3. Audit logging on API server captures who did what when - essential for incident response and compliance.

**Interview one-liner:**
"Cluster security requires defense in depth - API server hardening (OIDC, audit logging), etcd encryption at rest, Pod Security Standards enforcement, image signing and scanning, network policies for microsegmentation, and runtime protection with Falco - validated continuously with CIS benchmarks via kube-bench."

---

### Interview Deep-Dive

**Q1: You inherit a cluster with no security controls. What are your first 5 actions in priority order?**

_Why they ask:_ Tests security prioritization and practical knowledge.

**Answer:**

1. **Enable RBAC and audit logging** - Know who's doing what. Remove any anonymous/default admin access. This gives visibility.
2. **Encrypt etcd at rest** - Secrets are stored plaintext by default in etcd. Anyone with etcd access has all secrets.
3. **Apply Pod Security Standards (restricted)** - Prevent privileged containers, root execution. Start with audit mode, move to enforce.
4. **Default-deny Network Policies** - Stop lateral movement. Most important after initial compromise containment.
5. **Image scanning in CI/CD + registry allowlisting** - Prevent vulnerable/malicious images from entering the cluster.

Why this order:

- Items 1-2: Immediate risk of data exposure
- Items 3-4: Contain blast radius of any breach
- Item 5: Prevent new vulnerabilities entering

After these: enable seccomp, implement Falco, set up kube-bench automated scanning, establish secret rotation, implement workload identity.
