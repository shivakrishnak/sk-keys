---
version: 1
layout: default
title: "Admission Controllers"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /kubernetes/admission-controllers/
id: K8S-042
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["API Server", "RBAC (K8s)", "CRD (Custom Resource Definition)"]
used_by: ["Pod Security Standards", "K8s Security Hardening", "Operators"]
related:
  [
    "API Server",
    "RBAC (K8s)",
    "Pod Security Standards",
    "K8s Security Hardening",
  ]
tags: [kubernetes, admission-controllers, webhooks, security, policy, k8s]
---

# Admission Controllers

## ⚡ TL;DR

Admission controllers are **API Server plugins that intercept requests after authentication/authorization, before object persistence**. They can mutate (modify) or validate (accept/reject) objects. Webhooks extend this externally. Used for security policies, default injection, resource quotas, and policy enforcement.

---

## 🔥 Problem This Solves

You need to ensure all Pods have resource limits, inject sidecar containers automatically, prevent pulling from untrusted registries, or enforce naming conventions. RBAC controls who can create resources; admission controllers control what those resources look like.

---

## 📘 Textbook Definition

An admission controller is a piece of code that intercepts requests to the Kubernetes API Server prior to persistence in etcd, but after authentication and authorization. Admission controllers may be validating, mutating, or both. Mutating controllers modify the object; validating controllers accept or reject it.

---

## ⏱️ 30 Seconds

```
API Server request pipeline:
  1. Authentication  (who are you?)
  2. Authorization   (are you allowed?)
  3. Mutation        (modify object defaults)
  4. Schema validate (object structure valid?)
  5. Validation      (custom validation rules)
  6. Persist to etcd

Webhook types:
  - MutatingWebhookConfiguration   → called in step 3
  - ValidatingWebhookConfiguration → called in step 5
```

---

## 🔩 First Principles

- Built-in controllers: `NamespaceLifecycle`, `LimitRanger`, `ResourceQuota`, `PodSecurity`, `DefaultStorageClass`
- External: `MutatingAdmissionWebhook`, `ValidatingAdmissionWebhook` - HTTP POST to your service
- Webhook receives AdmissionReview JSON, returns allow/deny + optional patch
- Mutating runs before validating (mutation happens first, then validation validates the mutated object)
- Webhooks are `failurePolicy: Fail` (reject on webhook error) or `Ignore` (allow on error)

---

## 🧪 Thought Experiment

Istio service mesh uses a mutating webhook. When you create a Pod in a labeled namespace, Istio's webhook automatically adds the Envoy sidecar container to the Pod spec before it's stored in etcd. You never write sidecar injection code in your Deployments - the webhook does it transparently. This is admission controller magic.

---

## 🧠 Mental Model / Analogy

Admission controllers are like **airport security checkpoints**: authentication is showing your passport (who are you), authorization is checking your visa (are you allowed to enter), admission controllers are the security screening that can modify your luggage (mutation) or turn you away (validation), before you board the plane (etcd persist).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Admission controllers check and possibly modify Kubernetes objects before they're saved. They can reject invalid objects.

**Level 2 - Practitioner**: Built-in `LimitRanger` adds default resource limits. `ResourceQuota` enforces namespace quotas. `PodSecurity` enforces security policies. External webhooks use `MutatingWebhookConfiguration` and `ValidatingWebhookConfiguration`.

**Level 3 - Advanced**: Webhook receives HTTP POST with `AdmissionReview`. Response includes `allowed: true/false` and optional `patch` (JSON Patch for mutations). `namespaceSelector` and `objectSelector` filter which objects trigger the webhook. TLS required between API Server and webhook.

**Level 4 - Expert**: Admission controllers are a critical extension point for policy engines (OPA/Gatekeeper, Kyverno). CEL (Common Expression Language) admission policies in K8s 1.26+: native policy enforcement without webhooks. `ValidatingAdmissionPolicy` eliminates webhook round-trips for common policies. Webhook performance: must respond in <10s (default), impacts API Server throughput at scale.

---

## ⚙️ How It Works

### MutatingWebhookConfiguration

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
  - name: inject-sidecar.example.com
    admissionReviewVersions: ["v1"]
    clientConfig:
      service:
        name: sidecar-injector
        namespace: injection-system
        path: /inject
      caBundle: <base64-CA> # API Server uses this to verify webhook TLS
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
        operations: ["CREATE"]
    namespaceSelector:
      matchLabels:
        injection: enabled
    failurePolicy: Fail # reject Pod if webhook is down
    sideEffects: None
```

### Webhook Handler (Go)

```go
func (h *SidecarHandler) Handle(ctx context.Context, req admission.Request) admission.Response {
    pod := &corev1.Pod{}
    if err := h.decoder.Decode(req, pod); err != nil {
        return admission.Errored(http.StatusBadRequest, err)
    }

    // Add sidecar container
    sidecar := corev1.Container{
        Name:  "envoy-proxy",
        Image: "envoyproxy/envoy:v1.27",
        Ports: []corev1.ContainerPort{{ContainerPort: 15001}},
    }
    pod.Spec.Containers = append(pod.Spec.Containers, sidecar)

    // Return JSON patch
    marshaledPod, err := json.Marshal(pod)
    if err != nil {
        return admission.Errored(http.StatusInternalServerError, err)
    }
    return admission.PatchResponseFromRaw(req.Object.Raw, marshaledPod)
}
```

### ValidatingAdmissionPolicy (CEL, K8s 1.26+)

```yaml
apiVersion: admissionregistration.k8s.io/v1alpha1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-resource-limits
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        resources: ["deployments"]
        operations: ["CREATE", "UPDATE"]
  validations:
    - expression: >
        object.spec.template.spec.containers.all(c,
          has(c.resources) &&
          has(c.resources.limits) &&
          has(c.resources.limits.memory))
      message: "All containers must have memory limits"
```

---

## 🔄 E2E Flow: Mutating Webhook

```
kubectl apply -f pod.yaml
  → API Server: authenticate → authorize
  → Mutating admission:
      → Send AdmissionReview to MutatingWebhookConfiguration services
      → Sidecar injector adds envoy container
      → JSON patch applied to pod spec
  → Schema validation
  → Validating admission:
      → Check resource limits present (Gatekeeper)
      → Check image from approved registry (Kyverno)
  → Persist to etcd (with sidecar already injected)
  → kubelet sees pod → creates containers including sidecar
```

---

## ⚖️ Comparison Table

|                      | Built-in Controller | Webhook                 | CEL Policy        |
| -------------------- | ------------------- | ----------------------- | ----------------- |
| **Custom logic**     | ❌ Fixed behavior   | ✅ Full code            | ✅ Expressions    |
| **Performance**      | Fast (in-process)   | Network RTT             | Fast (in-process) |
| **Maintenance**      | None                | Deploy/maintain service | Declarative YAML  |
| **Failure handling** | N/A                 | failurePolicy           | failurePolicy     |
| **K8s version**      | All                 | 1.9+                    | 1.26+             |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                               |
| ---------------------------------------- | ------------------------------------------------------------------------------------- |
| "Admission controllers replace RBAC"     | RBAC controls access; admission controllers control content - both needed             |
| "Mutating webhook changes are permanent" | Only for that object; template must be updated to persist changes                     |
| "failurePolicy: Ignore is safer"         | Ignore can be a security bypass - if the policy webhook is down, objects pass through |
| "Validating always runs after mutating"  | Yes, always - but each phase runs all applicable webhooks in parallel                 |

---

## 🚨 Failure Modes

| Failure                                    | Symptom                                              | Fix                                                                 |
| ------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------- |
| Webhook service down + failurePolicy: Fail | All Pods rejected                                    | Ensure webhook Deployment is HA; set appropriate failurePolicy      |
| Webhook loop                               | Webhook Pod triggers its own webhook → infinite loop | Use `namespaceSelector` to exclude webhook's own namespace          |
| Self-signed cert                           | `x509: certificate signed by unknown authority`      | Mount CA bundle in webhook config or use cert-manager               |
| Slow webhook                               | API Server times out (10s default)                   | Optimize webhook; set `timeoutSeconds`; use CEL for simple policies |

---

## 🔗 Related Keywords

- [API Server](/kubernetes/api-server/) - runs admission pipeline
- [RBAC (K8s)](/kubernetes/rbac-k8s/) - runs before admission controllers
- [Pod Security Standards](/kubernetes/pod-security-standards/) - built-in admission policy
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) - admission controllers are key

---

## 📌 Quick Reference Card

```bash
# List enabled admission plugins
kube-apiserver --help | grep admission-plugins

# Check webhook configs
kubectl get mutatingwebhookconfigurations
kubectl get validatingwebhookconfigurations

# Describe a webhook
kubectl describe mutatingwebhookconfiguration istio-sidecar-injector

# Policy engines using admission webhooks
# OPA/Gatekeeper: kubectl get constrainttemplate
# Kyverno: kubectl get clusterpolicy
# Falco: runtime security (not admission, but related)

# CEL policies (K8s 1.26+)
kubectl get validatingadmissionpolicies
kubectl get validatingadmissionpolicybindings
```

---

## 🧠 Think About This

`failurePolicy` is the key security decision for admission webhooks. `failurePolicy: Fail` (default) means if your webhook is down, ALL matching objects are rejected - secure but risky for availability. `failurePolicy: Ignore` means objects pass through if webhook fails - available but potentially insecure. The production pattern: use `Ignore` for non-security-critical mutation (sidecar injection), `Fail` for security policies, and make security webhook Deployments highly available (multiple replicas, PodDisruptionBudget, priority class).
