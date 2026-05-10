---
version: 1
layout: default
title: "kubectl"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /kubernetes/kubectl/
id: K8S-025
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Kubernetes Architecture", "API Server", "Cluster"]
used_by: ["Deployment", "Pod", "Service (K8s)", "ConfigMap"]
related: ["API Server", "Cluster", "RBAC (K8s)", "Helm", "Kustomize"]
tags: [kubernetes, kubectl, cli, kubeconfig, k8s, command-line]
---

# kubectl

## ⚡ TL;DR

`kubectl` is the **Kubernetes command-line tool**. It communicates with the API Server via REST to create, read, update, and delete Kubernetes resources. It reads cluster credentials from `~/.kube/config`. Mastering kubectl is fundamental to working with Kubernetes.

---

## 🔥 Problem This Solves

You need to interact with the Kubernetes cluster: deploy apps, debug Pods, check logs, manage resources. kubectl provides a consistent CLI interface to the Kubernetes API for humans and automation scripts.

---

## 📘 Textbook Definition

kubectl is the Kubernetes command-line tool that allows you to run commands against Kubernetes clusters. You can use kubectl to deploy applications, inspect and manage cluster resources, and view logs.

---

## ⏱️ 30 Seconds

```bash
# Apply declarative manifest
kubectl apply -f deployment.yaml

# Get resources
kubectl get pods -n my-namespace -o wide
kubectl get all --all-namespaces

# Describe (detailed info + events)
kubectl describe pod my-pod-abc

# Logs
kubectl logs my-pod -c my-container -f --tail=100

# Exec into container
kubectl exec -it my-pod -- /bin/bash

# Port forward
kubectl port-forward svc/my-service 8080:80

# Delete
kubectl delete pod my-pod
kubectl delete -f deployment.yaml
```

---

## 🔩 First Principles

- kubectl translates commands to REST API calls to `kube-apiserver`
- kubeconfig (`~/.kube/config`) stores cluster URLs, credentials, and context settings
- `kubectl apply` = declarative (reconcile to desired state)
- `kubectl create/replace` = imperative (may fail if already exists)
- `--dry-run=client` = validate without sending to API Server
- `-o yaml` = get raw YAML; `-o json` = JSON; `-o jsonpath` = extract fields

---

## 🧪 Thought Experiment

You run `kubectl get pods` and see `CrashLoopBackOff`. Pipeline: `kubectl describe pod` → Events section → last restart reason. Then `kubectl logs --previous` → crash logs from last container run. Then `kubectl exec -it` to poke around in a running Pod. Three commands to diagnose most production issues.

---

## 🧠 Mental Model / Analogy

kubectl is the **remote control** for your Kubernetes cluster. Every button press (command) goes via Wi-Fi (HTTPS to API Server) to make the cluster do something. The kubeconfig is the TV guide (tells you which cluster = which "TV" to control).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: kubectl apply, get, describe, logs, delete. These five commands cover 80% of daily use.

**Level 2 - Practitioner**: `-n <namespace>`, `-A` (all namespaces), `-o yaml/json/wide`, `--watch/-w`, `--selector/-l`. Context switching: `kubectl config use-context`.

**Level 3 - Advanced**: JSONPath: `kubectl get pods -o jsonpath='{.items[*].metadata.name}'`. Custom columns: `-o custom-columns=NAME:.metadata.name,STATUS:.status.phase`. Diff: `kubectl diff -f` (preview changes). Server-side apply: `kubectl apply --server-side`.

**Level 4 - Expert**: kubectl plugins via krew. `kubectl neat` (clean up YAML), `kubectl tree` (resource ownership), `kubectl stern` (multi-pod logs). `kubectl debug` for ephemeral containers. Exec API: `kubectl exec` uses SPDY protocol over WebSocket. `kubectl cp` uses exec+tar for file transfers.

---

## ⚙️ How It Works

### kubeconfig Structure

```yaml
apiVersion: v1
kind: Config
clusters:
  - name: prod-cluster
    cluster:
      server: https://k8s-api.prod.example.com:6443
      certificate-authority-data: <base64-ca>
users:
  - name: admin
    user:
      client-certificate-data: <base64-cert>
      client-key-data: <base64-key>
contexts:
  - name: prod-admin
    context:
      cluster: prod-cluster
      user: admin
      namespace: default
current-context: prod-admin
```

### Essential Commands by Category

**Resource Management:**

```bash
kubectl apply -f file.yaml           # create or update
kubectl delete -f file.yaml
kubectl edit deployment my-app       # open editor
kubectl patch deployment my-app \
  -p '{"spec":{"replicas":5}}'
kubectl scale deployment my-app --replicas=5
```

**Inspection:**

```bash
kubectl get pods -A -o wide
kubectl describe pod/svc/deployment <name>
kubectl explain deployment.spec.replicas
kubectl api-resources
```

**Debugging:**

```bash
kubectl logs my-pod -c container --previous
kubectl exec -it my-pod -- bash
kubectl debug my-pod --image=busybox
kubectl port-forward pod/my-pod 8080:8080
kubectl top pods / kubectl top nodes
```

**Context/Auth:**

```bash
kubectl config get-contexts
kubectl config use-context prod
kubectl config set-context --current --namespace=staging
kubectl auth can-i create pods
```

---

## 🔄 E2E Flow: kubectl apply

```
kubectl apply -f deployment.yaml
  → Read kubeconfig → find current context → get cluster URL + credentials
  → Serialize YAML to JSON
  → HTTP PATCH /apis/apps/v1/namespaces/default/deployments/my-app
    (or POST if not exists)
  → API Server: auth + authz + admission
  → etcd: persist
  → Response: 200 OK (or 201 Created)
  → kubectl: print "deployment.apps/my-app configured"
```

---

## ⚖️ Comparison Table

|                      | kubectl apply       | kubectl create | kubectl replace |
| -------------------- | ------------------- | -------------- | --------------- |
| **If exists**        | Update (merge)      | Error          | Replace         |
| **If not exists**    | Create              | Create         | Error           |
| **GitOps friendly**  | ✅                  | ❌             | ❌              |
| **Tracks ownership** | Yes (field manager) | No             | No              |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| "`kubectl apply` is always safe"    | `apply` can drop fields not in your YAML; use `--server-side` for safer merging |
| "kubectl talks to kubelet directly" | kubectl always talks to API Server; never directly to kubelet                   |
| "`kubectl get pods` shows all pods" | Shows only current namespace; use `-A` for all namespaces                       |
| "kubectl delete is instant"         | Pods have `terminationGracePeriodSeconds` (default 30s)                         |

---

## 🚨 Failure Modes

| Failure              | Symptom                             | Fix                                     |
| -------------------- | ----------------------------------- | --------------------------------------- |
| Wrong context        | Commands hit wrong cluster          | `kubectl config current-context`        |
| Expired certs        | `x509: certificate has expired`     | Renew certs; regenerate kubeconfig      |
| RBAC denied          | `Error from server (Forbidden)`     | Check role and roleBinding              |
| API version mismatch | `no kind is registered for version` | Update kubectl to match cluster version |

---

## 🔗 Related Keywords

- [API Server](/kubernetes/api-server/) - kubectl's target
- [RBAC (K8s)](/kubernetes/rbac-k8s/) - controls what kubectl can do
- [Helm](/kubernetes/helm/) - package manager built on kubectl
- [Kustomize](/kubernetes/kustomize/) - kubectl-native overlay tool
- [kubeadm](/kubernetes/kubeadm/) - sets up clusters kubectl works with

---

## 📌 Quick Reference Card

```bash
# Must-know aliases
alias k=kubectl
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kdp='kubectl describe pod'

# Install plugins (krew)
kubectl krew install neat stern ctx ns

# Switch context fast (with kubectx plugin)
kubectx prod
kubens kube-system

# Show current context
kubectl config current-context

# Get resource YAML
kubectl get deployment my-app -o yaml | kubectl neat

# Watch events
kubectl get events --sort-by='.lastTimestamp' -A
```

---

## 🧠 Think About This

`kubectl apply --server-side` (SSA) is the future of kubectl apply. It moves field ownership tracking to the server, preventing the "last writer wins" problem where two automation tools clobber each other's changes. With SSA, each field manager (GitOps tool, operator, admission webhook) owns its specific fields, and conflicts are detected and reported explicitly. If you're using multiple tools to manage the same objects (ArgoCD + operators + manual kubectl), SSA prevents silent data loss.
