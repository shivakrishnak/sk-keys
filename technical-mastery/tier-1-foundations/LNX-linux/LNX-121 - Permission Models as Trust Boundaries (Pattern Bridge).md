---
id: LNX-121
title: "Permission Models as Trust Boundaries (Pattern Bridge)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-048, LNX-050, LNX-116, LNX-117, LNX-119
used_by: []
related: LNX-048, LNX-050, LNX-116, LNX-117, LNX-118, LNX-119, LNX-120
tags: [trust-boundaries, permission-model, access-control, subject-action-object, rbac, acl, oauth-scopes, kubernetes-rbac, aws-iam, database-grants, zero-trust, allowlist-vs-denylist, seccomp-allowlist, selinux-type-enforcement, linux-permissions, rwx, posix-acl, capabilities, principle-least-privilege, default-deny, default-allow, confused-deputy, trust-model, security-patterns, authorization, principle-of-least-authority, pola, discretionary-access, mandatory-access, attestation, trust-hierarchy, access-matrix, bell-lapadula]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 121
permalink: /technical-mastery/lnx/permission-models-as-trust-boundaries/
---

## TL;DR

**Meta-insight**: Every permission system - from Unix file permissions to AWS IAM
to Kubernetes RBAC to OAuth scopes - answers the same three-part question:
**who** (subject) can do **what** (action) to **which** (object). Unix
permissions: (owner/group/others) can (read/write/execute) on (file/directory).
AWS IAM: (Principal) can (action: s3:GetObject) on (resource: arn:aws:s3:::bucket/*).
Kubernetes RBAC: (ServiceAccount) can (verb: get,list) on (resource: pods).
OAuth: (client app) can (scope: read:email) on (user's email).
Database GRANT: (user) can (SELECT, INSERT) on (table). The pattern is
**universal**. The critical design choice: **allowlist** (default-deny:
enumerate what IS allowed) vs **denylist** (default-allow: enumerate what
IS NOT allowed). **Allowlist = secure by default** (seccomp, SELinux,
Kubernetes RBAC all use allowlist). **Denylist = convenient but insecure by
default** (traditional firewalls blocking specific ports). The principle:
**principle of least privilege** - grant the minimum necessary, default-deny,
time-limit privileges. This framework applies to EVERY authorization system.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-121 |
| **Difficulty** | ★★★ Advanced (Pattern recognition) |
| **Category** | Linux |
| **Tags** | trust boundaries, permission model, RBAC, IAM, OAuth, allowlist, least privilege, confused deputy |
| **Prerequisites** | LNX-048 (SELinux), LNX-050 (capabilities), LNX-116 (LSM theory), LNX-117 (namespace pattern) |

---

### The Problem This Solves

**The security design gap**: Engineers implement authorization in each system
independently - Unix permissions, IAM policies, RBAC, OAuth - without seeing
they're all the same abstraction. Recognizing the unified model provides:
(1) immediate intuition about ANY authorization system, (2) ability to identify
security holes by asking "what's the subject/action/object here?", (3) cross-domain
transfer of security design patterns (seccomp allowlist = API gateway allowlist = IAM
allowlist). The fundamental question is always: "Is this default-allow or default-deny?
And have I enumerated exactly the minimum necessary?"

---

### Textbook Definition

**Trust boundary**: A logical boundary between system components that operate at
different levels of trust. Communication crossing a trust boundary requires explicit
authorization. Examples: kernel/user space, internal network/public internet,
user process/privileged process, authenticated user/anonymous user.

**Access Control Matrix**: The theoretical model of authorization: a matrix where
rows = subjects (principals), columns = objects (resources), cells = allowed
operations. Practical implementations: Access Control Lists (ACL, per-object lists),
Capability Lists (per-subject lists), Role-Based Access Control (RBAC, group
subjects into roles).

**Principle of Least Privilege (PoLP) / Principle of Least Authority (POLA)**:
Every subject should have access to only the minimum resources necessary for its
legitimate purpose, and only for the minimum time required.

---

### Understand It in 30 Seconds

```bash
# === The universal permission model: who, what, which? ===

# Unix file permissions:
# ls -la /etc/shadow
# ---------- root shadow /etc/shadow
# WHO: root (owner), shadow (group), others
# WHAT: read(-), write(-), execute(-) for each WHO
# WHICH: /etc/shadow (the object)

# "shadow group members can read the file"
# -> WHO=shadow_group, WHAT=read, WHICH=/etc/shadow
# -> chmod g+r /etc/shadow  (GRANT read to group)

# ===== Allowlist vs Denylist (THE critical design choice) =====

# DENYLIST (default-allow): "allow everything EXCEPT the bad list"
# Traditional firewall:
iptables -A INPUT -p tcp --dport 23 -j DROP  # deny telnet
iptables -A INPUT -p tcp --dport 21 -j DROP  # deny ftp
# Problem: attacker uses port 8080 (not in denylist) -> allowed!
# Every new attack vector requires a NEW denylist rule
# Security: constantly chasing attackers

# ALLOWLIST (default-deny): "deny everything EXCEPT the allowed list"
# Kubernetes NetworkPolicy:
# apiVersion: networking.k8s.io/v1
# kind: NetworkPolicy
# spec:
#   podSelector: {}              <- applies to all pods
#   policyTypes: [Ingress, Egress]
#   ingress:
#     - from: [{podSelector: {matchLabels: {app: frontend}}}]
#       ports: [{port: 8080}]   <- ONLY frontend on port 8080 allowed
# Everything else: DENIED by default
# New attack vector on port 9999: ALREADY DENIED (not in allowlist)

# Seccomp (syscall allowlist):
cat syscalls.json
# {"defaultAction": "SCMP_ACT_ERRNO",  <- DEFAULT: deny ALL syscalls
#  "syscalls": [{"names": ["read","write","open","close","epoll_wait"],
#                "action": "SCMP_ACT_ALLOW"}]}  <- ALLOWLIST: only these 5
# Any new exploit using a syscall not in the list: already blocked!

# ===== Every permission system uses subject-action-object =====

# AWS IAM policy:
cat iam-policy.json
# {"Statement": [{
#   "Effect": "Allow",
#   "Principal": {"AWS": "arn:aws:iam::123:role/app-role"}, <- WHO
#   "Action": ["s3:GetObject", "s3:ListBucket"],            <- WHAT
#   "Resource": "arn:aws:s3:::myapp-bucket/*"              <- WHICH
# }]}
# WHO: app-role (subject)
# WHAT: GetObject, ListBucket (actions)
# WHICH: myapp-bucket/* (object)

# Kubernetes RBAC:
cat rbac.yaml
# kind: ClusterRole
# rules:
# - apiGroups: [""]             <- WHICH (core API group)
#   resources: ["pods"]         <- WHICH (pods)
#   verbs: ["get", "list"]      <- WHAT
# ---
# kind: ClusterRoleBinding
# subjects:
# - kind: ServiceAccount        <- WHO
#   name: myapp-sa
# roleRef:
#   name: pod-reader            <- binds WHO to WHAT+WHICH

# OAuth 2.0 scope:
# access_token claims: {"sub": "user123", "scope": "read:email write:profile"}
# WHO: user123 (subject = resource owner)
# WHAT: read (action on email), write (action on profile)
# WHICH: email data, profile data (objects)
# WHO uses on behalf of: the OAuth client application

# All the same question: WHO can do WHAT to WHICH?

# ===== Trust boundary crossing requires explicit authorization =====

# User space -> kernel space (every syscall crosses this boundary)
# Authorization: seccomp filter (allowlist of permitted syscalls)
# Denied syscall -> SIGSYS or EPERM -> attack contained

# Container -> host (namespace boundary)
# Authorization: capability bounding set + seccomp + AppArmor/SELinux
# Each is a separate authorization layer at the same trust boundary

# Microservice A -> microservice B (service trust boundary)
# Authorization: mTLS client certificate + service mesh authorization policy
# Istio AuthorizationPolicy: source.namespace == "frontend" && 
#                            destination.port == 8080 (same model!)
```

---

### First Principles

```
THE UNIFIED PERMISSION MODEL (Access Control Matrix theory)

Lampson (1974): Access Control Matrix
  Subjects: {user1, user2, process1, role_admin}
  Objects:  {file1, socket1, database_table1, api_endpoint1}
  Matrix cell [subject, object] = set of permitted operations
  
  e.g., matrix[user1][file1] = {read, write}
       matrix[user2][file1] = {read}
       matrix[user1][socket1] = {}  <- no access
  
  Operations: read, write, execute, create, delete, append, own, grant
  
  Every practical authorization system = a compact representation of this matrix

REPRESENTATION STRATEGIES:

ACL (Access Control List):
  Store COLUMN-WISE: for each object, list who can do what
  /etc/shadow: [(root, rw), (shadow_group, r)]
  Advantage: easy to see "who has access to THIS object"
  Disadvantage: hard to see "what can THIS user access" (check every ACL)
  Used in: POSIX file permissions, Windows NTFS ACLs, AWS S3 bucket policies

Capability List:
  Store ROW-WISE: for each subject, list what they can access
  user1: [(file1, rw), (socket1, r), (db_table, none)]
  Advantage: easy to see "what can THIS user do"
  Disadvantage: hard to see "who has access to THIS resource"
  Used in: OAuth tokens (the token = capability list for the bearer),
           Kubernetes ServiceAccount tokens (claims = capability list),
           AWS temporary credentials (list of allowed actions)

RBAC (Role-Based Access Control):
  Intermediate representation: Subject -> Role -> Permissions
  user1 -> role_admin -> {read:*, write:*, delete:*}
  user2 -> role_viewer -> {read:*}
  Advantage: simpler management (manage roles, not individual users)
  Used in: Kubernetes RBAC (Role, ClusterRole), AWS IAM roles,
           database roles, Spring Security role annotations

ABAC (Attribute-Based Access Control):
  Policy based on attributes of subject, object, action, environment
  "If subject.department == 'finance' AND object.classification == 'sensitive'
   AND action == 'read' AND environment.time in working_hours: ALLOW"
  More expressive than RBAC, more complex
  Used in: AWS IAM with condition keys, OPA (Open Policy Agent),
           Azure ABAC (preview), Kubernetes Admission Webhooks

THE ALLOWLIST VS DENYLIST PRINCIPLE (non-negotiable for security):

DEFAULT-ALLOW (denylist model):
  Start: everything allowed
  Add: deny rules for specific known-bad things
  
  Problems:
  1. Completeness: you must enumerate ALL bad things (impossible!)
  2. New threats: every new attack requires a new deny rule
  3. Zero-day: unknown attacks bypass all deny rules
  4. The asymmetry: attackers need ONE unblocked path; defenders need
     to block ALL paths
  
  Example: traditional firewall (block known-bad ports)
  Attacker moves to port 8080 -> allowed!
  
  WHERE DENYLIST IS OK:
  Rate limiting (allow all IPs but rate-limit each)
  Anti-spam (allow all email but flag known-spam patterns)
  WAF (allow all requests but block known-attack patterns)
  These are "defense in depth" additions, not PRIMARY security

DEFAULT-DENY (allowlist model):
  Start: everything denied
  Add: allow rules for specific known-good things
  
  Benefits:
  1. Completeness: unknown threats denied by default
  2. New threats: already blocked (not in allowlist)
  3. Zero-day: most zero-days require new syscalls or network paths
     (already denied by default-deny policies)
  4. The asymmetry REVERSES: attacker must find a path WITHIN the allowlist;
     defender only needs to audit the allowlist (smaller surface)
  
  WHERE ALLOWLIST IS USED:
  seccomp: defaultAction=SCMP_ACT_ERRNO, then allowlist syscalls
  SELinux: no-access-by-default, then allow rules per type pair
  Kubernetes NetworkPolicy: no traffic by default (once policy applied)
  AWS IAM: implicit deny on all actions, explicit allow needed
  Zero-trust networking: no connection allowed unless explicitly authorized

THE CONFUSED DEPUTY PROBLEM (classic security bug):

  The "confused deputy" scenario:
  Process A (compiler) has privilege to read all source files.
  Process A (compiler) has privilege to write to billing records.
  (Two separate legitimate authorities, both held by A simultaneously)
  
  Attacker: tricks the compiler to compile "/etc/billing/rates.c"
  Compiler: reads the file (using its read-all privilege) and writes output
  But the output goes to billing database (using its write-billing privilege)!
  
  The compiler was a "confused deputy": it held two authorities and confused
  which authority it was exercising.
  
  In Unix: the SUID bit is a classic confused deputy source
  /usr/bin/passwd: owned by root, has SUID bit
  When user runs passwd: process runs as ROOT (not user's uid)
  If passwd has a buffer overflow: attacker gains root
  passwd was "confused" about which authority (user-mode or root-mode) to use
  
  Solution: capability-based security
  Split authorities into separate objects
  passwd: only has capability to write /etc/shadow (NOT root = write everything)
  If passwd is exploited: attacker gets only /etc/shadow-write capability
  Not general root!
  
  Manifestations in modern systems:
  - SSRF (Server-Side Request Forgery): web server has network access to internal
    services. Attacker confuses the web server into making requests to
    internal metadata APIs (AWS: 169.254.169.254) on their behalf
    Solution: IMDSv2 (require explicit PUT request before GET = proves request
    originated from legitimate application, not confused deputy)
  
  - SQL injection: database has privilege to read all tables
    Attacker injects SQL to access tables the application shouldn't query
    Solution: separate DB users per operation (read-only user for SELECT queries)
  
  - Privilege escalation via SUID: application has SUID root
    Attacker exploits app to gain root
    Solution: use capabilities instead of SUID root (limited blast radius)

TRUST HIERARCHY IN LINUX:

The hierarchy (most trusted to least trusted):
  1. Hardware/firmware (UEFI, secure boot)
  2. Linux kernel (ring 0)
  3. Privileged user-space (uid=0, CAP_SYS_ADMIN)
  4. System services (systemd, udev - specific capabilities)
  5. Regular users (uid > 0, no special capabilities)
  6. Containerized processes (within namespace, cgroup limits)
  7. Browser sandbox (Chromium renderer: seccomp + namespaces)
  8. WASM sandbox (WebAssembly: capability-based isolation)
  
  Each level: trusts levels ABOVE it (kernel trusts hardware)
  Each level: does NOT automatically trust levels BELOW it
  Communication DOWNWARD: no authorization needed (kernel can do anything)
  Communication UPWARD: requires explicit authorization (syscall = request to kernel)
  Communication ACROSS (same level): requires explicit authorization (file permissions)
  
  Trust boundary crossing = crossing a level in this hierarchy
  Every crossing: must have an authorization check

ZERO-TRUST ARCHITECTURE (modern application of the model):

  Traditional network trust model:
  Inside firewall = trusted. Outside = untrusted.
  ("castle and moat" model)
  Problem: if attacker gets inside the firewall: trusted everywhere!
  Lateral movement: attacker compromises machine A -> accesses machine B
  (because A and B are both "inside" = both trusted)
  
  Zero-trust model:
  NO implicit trust based on network location
  Every connection: subject must authenticate AND be authorized
  "Never trust, always verify"
  
  Implementation:
  mTLS everywhere (both sides present certificates)
  Service mesh authorization policy (Istio, Linkerd):
    allow source.namespace="frontend" to destination.service="api" 
    on destination.port=8080
  This is EXACTLY the Linux permission model:
    subject (source service) -> action (HTTP method + port) -> object (target service)
  
  Kubernetes Network Policy = zero-trust for pod networking:
  Without NetworkPolicy: all pods can reach all other pods
  With NetworkPolicy: only explicitly allowed paths work
  Same default-deny allowlist model as seccomp, SELinux, AWS IAM
```

---

### Thought Experiment

Designing a minimal-trust production system:

```bash
# === Audit the trust model of a containerized microservice ===

# The question: "Who can do what to what?"
# Enumerate ALL trust boundaries and authorization at each:

# --- 1. Network trust boundary ---
# Who can connect to my service?
kubectl get networkpolicy -n myapp -o yaml | \
  python3 -c "import yaml,sys; 
  for doc in yaml.safe_load_all(sys.stdin.read()):
    if doc: print(yaml.dump(doc, default_flow_style=False))"
# If no NetworkPolicy: default-allow (all pods can reach all pods = BAD)
# Goal: NetworkPolicy with explicit allowlist (only frontend -> api)

# --- 2. API trust boundary ---
# Who can call which API endpoint?
# Istio AuthorizationPolicy:
# spec:
#   rules:
#   - from:
#     - source:
#         principals: ["cluster.local/ns/frontend/sa/frontend-sa"]
#     to:
#     - operation:
#         methods: ["GET"]
#         paths: ["/api/products/*"]
# WHO: frontend-sa (ServiceAccount)
# WHAT: GET (HTTP method)
# WHICH: /api/products/* (URL path)
# ALLOWLIST: only these specific calls permitted

# --- 3. Kubernetes RBAC trust boundary ---
# What can the service's ServiceAccount do?
kubectl get clusterrolebinding -o json | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for crb in data['items']:
    for subj in crb.get('subjects',[]):
        if subj['kind']=='ServiceAccount' and 'myapp' in subj.get('name',''):
            print(f\"SA: {subj['name']} -> Role: {crb['roleRef']['name']}\")
"
# If ServiceAccount has: cluster-admin role -> TOO MUCH PRIVILEGE
# Goal: custom role with ONLY what's needed:
# - get, list pods in own namespace (for health checks)
# - read own ConfigMap
# NOTHING ELSE

# --- 4. Container process trust boundary ---
# What can the container process do?
kubectl get pod myapp-pod -o json | python3 -c "
import json, sys
pod = json.load(sys.stdin)
containers = pod['spec']['containers']
for c in containers:
    sc = c.get('securityContext', {})
    print(f\"Container: {c['name']}\")
    print(f\"  runAsNonRoot: {sc.get('runAsNonRoot', 'NOT SET')}\")
    print(f\"  readOnlyRootFilesystem: {sc.get('readOnlyRootFilesystem', 'NOT SET')}\")
    print(f\"  allowPrivilegeEscalation: {sc.get('allowPrivilegeEscalation', 'NOT SET')}\")
    print(f\"  capabilities.drop: {sc.get('capabilities',{}).get('drop', 'NOT SET')}\")
"
# Goal: runAsNonRoot=true, readOnlyRootFilesystem=true,
#       allowPrivilegeEscalation=false, capabilities.drop=["ALL"]

# --- 5. Filesystem trust boundary ---
# What files can the process access?
kubectl exec myapp-pod -- cat /proc/self/status | grep "^Cap"
# CapEff: 0000000000000000  <- zero capabilities (correct!)

# What AppArmor/SELinux profile is applied?
kubectl get pod myapp-pod -o jsonpath=\
  '{.metadata.annotations.container\.apparmor\.security\.beta\.kubernetes\.io/*}'
# Should show: runtime/default or custom profile

# --- Summary: trust model audit results ---
# For each trust boundary: is it allowlist or denylist?
# Is least privilege applied (minimum necessary granted)?
# Is there a confused deputy vulnerability (holding two authorities)?
echo "Trust Model Audit:"
echo "1. Network: NetworkPolicy applied? YES/NO"
echo "2. API: Istio AuthorizationPolicy? YES/NO"
echo "3. RBAC: minimal ServiceAccount permissions? YES/NO"
echo "4. Container: non-root, no caps, read-only fs? YES/NO"
echo "5. Host: seccomp profile applied? YES/NO"
echo "Red flags: any NO = default-allow or excess privilege"
```

---

### Mental Model / Analogy

```
Permission model = a physical building's security system

The "trust boundary" = the locked door between areas

Trust levels in the building:
  Public lobby: anyone enters (no authentication)
  Employee areas: keycard required (authentication = identity verification)
  Finance floor: finance team keycard only (authorization = role check)
  Server room: IT operations + security team (specific role, specific need)
  CEO office: CEO + authorized visitors only
  Safe room: CEO + CFO + multi-factor authorization

The permission model at each door:
  WHO: employee badge (subject = "carrier of badge")
  WHAT: open door, enter room (action = "unlock", "enter")
  WHICH: finance floor door (object = specific door)
  
  Badge + Door + Permission = the access control matrix row
  
  ALLOWLIST approach:
  The door has a list: "Finance badges: {badge_1001, badge_1234, badge_5678}"
  A new person: not in the list -> DENIED
  A new attack: someone without a finance badge -> DENIED automatically
  (Default-deny: only listed badges work)
  
  DENYLIST approach:
  The door has a list: "Blocked badges: {badge_FIRED_001, badge_SUSPENDED_002}"
  A new person: not in the denylist -> ALLOWED
  Problem: any new unauthorized person slips through before being added to denylist!

The Confused Deputy in a building:
  The janitor has: master key (opens all rooms) AND cleaning supplies access
  The janitor is confused into "cleaning" the CEO's desk (accessing confidential docs)
  The janitor was using the wrong authority: cleaning authority != file access authority
  
  Solution: separate keys
  Cleaning key: opens supply closets and public areas
  CEO key: only for authorized access by CEO/security
  Janitor: gets cleaning key only, not CEO key
  = Principle of Least Authority (POLA)

Zero-trust in the building analogy:
  Traditional: "inside the building = trusted"
  Employee walks in once (single badge scan) -> trusted everywhere
  Problem: if badge is stolen or visitor sneaks in -> trusted everywhere
  
  Zero-trust building:
  EVERY door requires badge scan
  Even after entering: each door = new authorization check
  Visitor: can enter lobby (authorized), cannot enter finance floor (not authorized)
  Compromised employee: access limited to THEIR authorized rooms
  Lateral movement: impossible (each room requires explicit authorization)
  
  This is exactly Kubernetes zero-trust networking:
  Every pod-to-pod connection: requires explicit NetworkPolicy authorization
  Even if already "inside" the cluster: default-deny
  Service mesh mTLS: every call requires mutual TLS authentication
  = badge scan at every door

The three-layer model for containers:
  Outer door: Kubernetes NetworkPolicy (who can reach the service?)
  Middle door: Kubernetes RBAC / Istio AuthorizationPolicy (who can call what?)
  Inner door: seccomp + capabilities + AppArmor (what can the process do?)
  
  Defense in depth = multiple locked doors
  Attacker must get through ALL doors, not just one
  Even if outer door is compromised: inner doors still protect
```

---

### Gradual Depth - Five Levels

**Level 1:**
What a trust boundary is. The subject-action-object model. Unix file permissions
as the simplest permission model. allowlist vs denylist and why allowlist is more
secure. The principle of least privilege. Why default-deny is the secure default.

**Level 2:**
ACL vs capability list vs RBAC representations. Linux capabilities as permission
decomposition. SELinux type enforcement (allow rules = explicit allowlist).
Kubernetes RBAC: Role, ClusterRole, RoleBinding, ClusterRoleBinding.
AWS IAM: principal, action, resource, condition. The confused deputy problem.

**Level 3:**
ABAC (attribute-based access control). OAuth 2.0 scopes and the capability model.
Zero-trust networking: mTLS + authorization policy. Service mesh authorization
(Istio AuthorizationPolicy = subject-action-object model). POSIX ACLs (extended
permissions beyond owner/group/other). Mandatory vs discretionary access control
(MAC vs DAC) applied to the trust boundary model.

**Level 4:**
The Bell-LaPadula model (confidentiality: no read up, no write down). The Biba model
(integrity: no read down, no write up). How these formal models relate to MLS/MCS
in SELinux (multi-level security). The Principle of Least Authority (POLA) vs
Principle of Least Privilege (PoLP) distinction. Capability-based security systems
(Capsicum, Fuchsia capabilities, WebAssembly capabilities). IMDSv2 as a confused
deputy prevention. SSRF vulnerabilities as confused deputy attacks.

**Level 5:**
The fundamental incompleteness of access control: any real system has implicit
authorities (side channels, timing attacks, covert channels) that bypass explicit
authorization. The "confused deputy" is the tip of an iceberg. The information-
theoretic limit: if an authorized subject can observe system behavior (timing, power,
EM emissions), it can leak information to unauthorized subjects regardless of access
control. Proof-carrying code (PCC) and verified security properties: proving formally
that no information flow violations exist. The relationship between access control
(who can access what) and information flow control (what information can reach where):
SELinux prevents the first but not the second (a high-security process can signal to
a low-security process via timing side channels even with no SELinux rule violations).
Declassification policies and how they relate to the confused deputy in multi-level
security systems.

---

### Code Example

**BAD - default-allow with excessive permissions:**
```yaml
# BAD: Kubernetes RBAC - overly permissive ServiceAccount
# This is the "cluster-admin for everything" antipattern

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: myapp-cluster-admin  # BAD name hint: cluster-admin!
roleRef:
  kind: ClusterRole
  name: cluster-admin        # cluster-admin = EVERYTHING in cluster
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: myapp-sa
  namespace: default
# WHO: myapp-sa
# WHAT: every verb (get, list, watch, create, update, delete, escalate)
# WHICH: every resource in every namespace
# This violates PoLP: a web service doesn't need to
# create/delete nodes, read secrets in all namespaces, etc.
# If myapp is compromised: attacker has full cluster access!
```

```yaml
# GOOD: Kubernetes RBAC - minimal permissions per PoLP

# Step 1: What does myapp actually NEED?
# - Read its own ConfigMap (for config)
# - List pods in its OWN namespace (for health dashboard)
# - Create/delete Jobs in its own namespace (for batch work)
# NOTHING ELSE

apiVersion: rbac.authorization.k8s.io/v1
kind: Role  # <- Role (not ClusterRole) = namespace-scoped only
metadata:
  name: myapp-minimal-role
  namespace: myapp-namespace  # <- ONLY this namespace
rules:
# Permission 1: read own config
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["myapp-config"]  # <- ONLY this specific ConfigMap!
  verbs: ["get"]                    # <- ONLY get (not list/watch/update)
# Permission 2: list pods in own namespace
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]  # no create/delete/update
# Permission 3: manage jobs (for batch processing)
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["create", "delete", "get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: myapp-role-binding
  namespace: myapp-namespace
subjects:
- kind: ServiceAccount
  name: myapp-sa
  namespace: myapp-namespace
roleRef:
  kind: Role
  name: myapp-minimal-role
  apiGroup: rbac.authorization.k8s.io

# Verify: what CAN myapp-sa do?
# kubectl auth can-i list pods --as=system:serviceaccount:myapp-ns:myapp-sa
# -> yes (granted)
# kubectl auth can-i delete nodes --as=system:serviceaccount:myapp-ns:myapp-sa
# -> no (not granted)
# kubectl auth can-i get secrets --as=system:serviceaccount:myapp-ns:myapp-sa
# -> no (not granted)
# kubectl auth can-i list pods -n other-namespace \
#   --as=system:serviceaccount:myapp-ns:myapp-sa
# -> no (Role is namespace-scoped!)
```

---

### Comparison Table

| System | Who (Subject) | What (Action) | Which (Object) | Default |
|--------|--------------|---------------|----------------|---------|
| Unix permissions | owner/group/other | r/w/x | file/dir | deny (no bits set) |
| SELinux | type (httpd_t) | operation class | type (shadow_t) | deny |
| Kubernetes RBAC | ServiceAccount/User | verb | API resource | deny |
| AWS IAM | Principal (role/user) | Action (s3:Get*) | Resource (ARN) | deny |
| OAuth 2.0 | Client app (bearer token) | scope (read:email) | user's data | deny |
| Database GRANT | User/Role | privilege (SELECT) | table/schema | deny |
| seccomp | process | syscall number | (none, syscall itself) | deny |
| Istio AuthPolicy | service principal | HTTP method | URL path | deny |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Network firewall rules are sufficient access control" | Network firewall rules are a PERIMETER defense and implement a denylist model (block specific ports/IPs). They are necessary but not sufficient. Problems with firewall-only security: (1) They don't control WHAT an authorized connection can DO (port 443 is allowed to your web service: what SQL can the caller inject?). (2) They don't control lateral movement (if firewall allows host A to reach host B: A compromised = B reachable). (3) They can't authorize based on APPLICATION-LEVEL identity (port 443 to /api/users vs /api/admin: same firewall rule). Modern defense requires authorization at EVERY layer: network (NetworkPolicy), API (mTLS + authz policy), application (RBAC), OS (seccomp + capabilities), filesystem (SELinux/AppArmor). Firewall = outer perimeter. Inner defense: assume perimeter is breached, apply zero-trust at every layer. |
| "RBAC roles eliminate the need for per-resource permissions" | RBAC simplifies management (manage roles, not users) but doesn't replace per-resource authorization. The difference: RBAC `get pods` grants the right to GET ANY pod in the namespace. ACL-style `resourceNames: ["specific-pod"]` restricts to a SPECIFIC pod. This matters when: (1) A service should only access ITS OWN secrets (not any secret in the namespace). RBAC role `get secrets` without resourceNames = can read ALL secrets (including other services' credentials). With resourceNames = only its own secrets. (2) Multi-tenant systems: each tenant's data in the same namespace. RBAC can restrict by role, but cannot restrict ONE tenant from reading ANOTHER tenant's data without namespace separation OR per-resource ACLs. The complete model: RBAC for role-based coarse-grained permissions + per-resource ACLs for fine-grained restrictions + ABAC for dynamic conditions (time of day, request origin, data classification). |
| "Allowlist is too restrictive and creates operational overhead" | The operational overhead argument for denylist is that allowlists require enumerating all legitimate operations upfront. This is true but the argument proves too much: if you can't enumerate the legitimate operations, how do you know what your system is supposed to do? The inability to enumerate legitimate operations is itself a security smell. In practice: (1) Start with existing behavior: run your application and log what it does (strace, seccomp audit mode, SELinux permissive mode, network policy audit). This generates the allowlist automatically. (2) Use tooling: `audit2allow` (SELinux), `docker run --security-opt seccomp=trace` (seccomp profiling), Kubernetes NetworkPolicy Advisor (suggests policies from existing traffic). (3) Accept some maintenance: legitimate behavior changes require updating allowlists. This is DESIRABLE: unauthorized new behavior (attacker adding a new syscall or network path) is DENIED automatically until explicitly approved. The security-operational tradeoff is: allowlist requires more upfront work but provides stronger guarantees. Denylist is lower friction but weaker. For production systems: allowlist for security controls; denylist for rate limiting and spam. |
| "Service accounts should have admin privileges for simplicity" | Service accounts with admin privileges are the most common Kubernetes security misconfigurations. The "simplicity" cost is: if the service is compromised, the attacker has full cluster control. Common pattern in the wild: a monitoring service with cluster-admin "because it needs to read everything." The correct approach: create a Role with only `get`, `list`, `watch` on required resources. The setup cost: 30 minutes to define the minimal Role. The security benefit: compromise of the monitoring service cannot modify resources (deploy malicious pods, read secrets from other namespaces). The operational principle: "minimum necessary privilege is not a restriction, it is a specification." The role specification IS the documentation of what the service needs. When the service needs more: update the role explicitly (which is an authorization review). Without PoLP: a service's actual access is unknown (has everything = unclear what it actually uses). With PoLP: the service's access is exactly documented in its Role. |

---

### Failure Modes & Diagnosis

```bash
# === Audit Kubernetes RBAC for privilege violations ===

# Find ServiceAccounts with excessive permissions:
kubectl get clusterrolebindings -o json | python3 -c "
import json, sys
data = json.load(sys.stdin)
dangerous_roles = ['cluster-admin', 'edit', 'admin']
for crb in data['items']:
    role = crb['roleRef']['name']
    if any(r in role for r in dangerous_roles):
        for subj in crb.get('subjects', []):
            if subj['kind'] == 'ServiceAccount':
                print(f'DANGER: {subj[\"namespace\"]}/{subj[\"name\"]} -> {role}')
"
# Output: any ServiceAccount with cluster-admin/edit/admin role
# These are PRIVILEGE VIOLATIONS: application SAs don't need these

# Check what a specific SA can do:
kubectl auth can-i --list --as=system:serviceaccount:default:my-sa
# Lists ALL permissions: review for excess

# === Check for overly broad network access ===

# No NetworkPolicies = default-allow (all pods can reach all pods):
kubectl get networkpolicies --all-namespaces | wc -l
# If this is 0: no network isolation at all!

# Check which namespaces lack NetworkPolicy:
for ns in $(kubectl get ns -o jsonpath='{.items[*].metadata.name}'); do
  count=$(kubectl get networkpolicies -n $ns 2>/dev/null | wc -l)
  if [ "$count" -le 1 ]; then
    echo "WARNING: namespace $ns has no NetworkPolicy (default-allow!)"
  fi
done

# === Diagnose container running as root ===

kubectl get pods --all-namespaces -o json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for pod in data['items']:
    ns = pod['metadata']['namespace']
    name = pod['metadata']['name']
    for c in pod['spec']['containers']:
        sc = c.get('securityContext', {})
        if (sc.get('runAsUser', 0) == 0 or 
            not sc.get('runAsNonRoot', False)):
            print(f'WARN: {ns}/{name}/{c[\"name\"]} may run as root')
"

# === Check for AWS IAM over-permission ===

# Find all IAM policies with wildcard actions:
aws iam list-policies --scope Local --query 'Policies[*].Arn' \
  --output text | \
  while read arn; do
    policy=$(aws iam get-policy-version \
      --policy-arn "$arn" \
      --version-id $(aws iam get-policy \
        --policy-arn "$arn" --query 'Policy.DefaultVersionId' --output text) \
      --query 'PolicyVersion.Document')
    if echo "$policy" | python3 -c "
import json,sys
doc = json.load(sys.stdin)
for s in doc.get('Statement',[]):
    actions = s.get('Action',[])
    if isinstance(actions, str): actions = [actions]
    if any(a in ['*','*:*'] for a in actions):
        print('WILDCARD')
        break
" 2>/dev/null | grep -q "WILDCARD"; then
      echo "DANGER: $arn has wildcard (*) action"
    fi
  done
```

---

### Related Keywords

**Foundational:**
LNX-048 (SELinux), LNX-050 (capabilities), LNX-116 (LSM design theory)

**Pattern context:**
LNX-117 (namespace pattern), LNX-119 (Unix philosophy)

**Related:**
LNX-118 (cgroup resource model), LNX-120 (performance reasoning)

---

### Quick Reference Card

| Permission system | Subject | Action | Object | Default |
|-------------------|---------|--------|--------|---------|
| Unix chmod | user/group/other | rwx | file | varies |
| SELinux | type (domain) | operation | type (label) | DENY |
| seccomp | process | syscall | kernel function | DENY |
| K8s RBAC | ServiceAccount | verb | resource | DENY |
| AWS IAM | Principal | Action | Resource | DENY |
| OAuth 2.0 | Client/user | scope | user data | scope-based |
| Database GRANT | user/role | privilege | table/function | DENY |
| Istio AuthPolicy | service principal | HTTP method | path | DENY |

**3 things to remember:**
1. Universal model: WHO (subject) can do WHAT (action) to WHICH (object). Every authorization system answers this. Unix permissions, SELinux, RBAC, IAM, OAuth - all the same question with different vocabulary. Recognizing this pattern: immediate intuition about any new permission system.
2. Allowlist = secure default. Default-deny + enumerate what IS allowed. SELinux, seccomp, Kubernetes RBAC, AWS IAM all use allowlist model. Denylist = default-allow, enumerate what is NOT allowed. Weaker: unknown/new operations bypass the denylist. Use allowlist for all security controls.
3. Principle of least privilege: minimum necessary, time-limited, audited. The confused deputy problem: a process that holds two authorities can be tricked into using the wrong one (SUID programs, SSRF attacks, SQL injection). Solution: separate authorities, grant only the single specific authority needed per operation.

---

### Transferable Wisdom

The subject-action-object permission model is universal in computer science and
appears at every layer of the stack: CPU ring privilege levels (ring 0/3 = subject
privilege, instruction = action, hardware = object), memory protection (process =
subject, read/write/execute = action, memory page = object), network (source IP/port =
subject, TCP connection = action, destination IP/port = object), database (connection
user = subject, DML statement = action, table = object), microservices (service identity
= subject, HTTP method + path = action, target service = object), API gateway (API key =
subject, rate-limited endpoint = action, backend service = object). The design principle
that unifies them: ALLOWLIST + LEAST PRIVILEGE + DEFAULT-DENY. Apply this to any new
security design: (1) Define the subject types (who are the principals?), (2) Define
the action types (what operations exist?), (3) Define the object types (what resources
exist?), (4) Default to DENY for all (subject, action, object) combinations, (5) Add
explicit ALLOW rules for the minimum necessary set. This framework, when applied
consistently at every layer, provides defense in depth: an attacker must bypass the
authorization check at EVERY layer (network, API, service, OS, filesystem) to reach
the target resource. The cost model: each additional layer = multiplicative protection
(not additive), because the attacker must bypass ALL layers independently.

---

### The Surprising Truth

The "confused deputy" problem, which is at the root of SUID exploits, SSRF attacks,
SQL injection, and many other vulnerability classes, was first described in 1988 by
Norm Hardy in a paper titled "The Confused Deputy (or why capabilities might have
been invented)." The paper describes a compiler (called the "deputy") that holds two
authorities simultaneously and can be confused into using the wrong one. Hardy's
solution: capability-based security (each authority = a separate unforgeable token,
passed explicitly rather than held implicitly). The surprise: Hardy described the
solution 36 years ago, and yet confused deputy attacks remain in the OWASP Top 10
today (as SSRF, broken access control, etc.). Modern solutions - OAuth tokens as
capabilities, Kubernetes ServiceAccount tokens as capability lists, AWS STS temporary
credentials as time-limited capabilities, Landlock as self-imposed capability
restriction - are all implementations of Hardy's 1988 insight. The most-exploited
class of vulnerabilities in modern software (SSRF, privilege escalation) would be
prevented by applying a 36-year-old design pattern. The lesson: security principles
don't expire. Understanding the confused deputy, allowlist vs denylist, and principle
of least privilege eliminates entire classes of vulnerabilities, not just specific bugs.

---

### Mastery Checklist

- [ ] Can map any permission system to the subject-action-object model (Unix, RBAC, IAM, OAuth)
- [ ] Understands allowlist vs denylist and can explain why allowlist is more secure by default
- [ ] Can identify the confused deputy problem in code/system designs (SUID, SSRF, SQL injection)
- [ ] Can audit Kubernetes RBAC for least privilege violations and fix them
- [ ] Can articulate zero-trust model and how it applies the permission model at every layer

---

### Think About This

1. OAuth 2.0 uses "scopes" to implement the permission model. A scope like `read:email`
   means "the application can read the user's email." But scopes are defined by the
   AUTHORIZATION SERVER (Google, GitHub, etc.), not by the resource. This means: the
   granularity of permissions is limited to whatever scopes the auth server defined.
   Compare this to Kubernetes RBAC where any resource and verb combination can be defined.
   Analyze: what are the security implications of "pre-defined scope lists" vs "dynamic
   RBAC rules"? Design a permission model for a hypothetical API where users can grant
   specific permissions to third-party apps at the RESOURCE level (e.g., "this app can
   read only my document ID 12345, not all documents"). This is what Google Drive's
   per-file sharing does. How does this differ from standard OAuth scopes? What are the
   implementation challenges?

2. The Bell-LaPadula model defines a formal security model for confidentiality: "no read
   up, no write down." A TOP SECRET process cannot read information from UNCLASSIFIED
   (read down = declassification). A TOP SECRET process cannot write to UNCLASSIFIED
   (write down = information leaks). SELinux's MLS (Multi-Level Security) mode implements
   this. But: modern systems have a different problem - not military multi-level security
   but MULTI-TENANT ISOLATION. Analyze how the Bell-LaPadula rules map (or don't map)
   to Kubernetes multi-tenant isolation. When does "no read up, no write down" translate
   to "namespace A cannot read namespace B's secrets"? Where does the model break down
   for cloud multi-tenancy? Design a formal permission model for a SaaS application that
   handles both "tenant isolation" (tenant A cannot see tenant B) and "role-based access"
   (admin can see all, read-only user can only read).

3. The principle of least privilege (PoLP) and the principle of least authority (POLA)
   are often used interchangeably but have a subtle distinction. PoLP: grant minimum
   ACCESS (read/write) to minimum RESOURCES. POLA: grant minimum CAPABILITY (authority
   to cause effects). The distinction: a process might have READ access to a file that
   contains a private key. PoLP: "read permission to private key file = minimum." POLA:
   "the process should not hold an object that, when read, gives the ability to impersonate
   a server." POLA says: don't hold the private key AT ALL; instead, call a signing service
   that holds the key and exposes only a signing API. Analyze: how does the shift from
   PoLP to POLA change system design? Give three examples of systems redesigned for POLA
   instead of PoLP. (Hint: HSM instead of private key file, secrets management service
   instead of env var, certificate rotation service instead of long-lived cert).

---

### Interview Deep-Dive

**Foundational:**
Q: Explain the principle of least privilege and give three examples of how to apply it in a containerized microservice.
A: PRINCIPLE OF LEAST PRIVILEGE (PoLP): Every subject (user, process, service) should have access to only the MINIMUM resources and capabilities necessary for its legitimate purpose, for the MINIMUM time required. The principle reduces blast radius: if a minimally-privileged subject is compromised, the attacker can only access what that subject was legitimately allowed to access. THREE APPLICATIONS IN CONTAINERIZED MICROSERVICES: (1) PROCESS IDENTITY: Run the container as a NON-ROOT user. Default Docker: runs as root (uid=0). If the web app is exploited: attacker has root inside the container + all capabilities. Correct: `USER appuser` in Dockerfile (uid=1001). `--cap-drop ALL` in docker run (zero capabilities). `--security-opt no-new-privileges` (prevent setuid escalation). Blast radius of exploit: limited to what uid=1001 can do (only read its own files, no capability to bind to port < 1024, no access to host kernel modules). (2) FILESYSTEM ACCESS: Use read-only container filesystem + tmpfs for writes. `--read-only --tmpfs /tmp`. Application code is in /app (read-only): an exploit cannot modify the binary, inject new code, or write to system directories. Writes limited to /tmp (in-memory, lost on restart). (3) KUBERNETES RBAC: Create a minimal ServiceAccount with only the permissions the service actually needs. If the service reads a ConfigMap and creates Jobs: Role with `get configmaps [name=myapp-config]` + `create,delete jobs`. NOT cluster-admin, NOT edit, NOT any ClusterRole. `kubectl auth can-i --list --as=system:serviceaccount:ns:sa` shows exactly what the SA can do: should be a SHORT list. If it is a long list: it has excess privilege. THE LEAST PRIVILEGE PRINCIPLE IN PRACTICE: The test is: "If this service is fully compromised, what CAN the attacker do?" With PoLP: can read its ConfigMap, create/delete its own Jobs. CANNOT: read other secrets, delete pods, access other namespaces, use the host network. Without PoLP (cluster-admin): can do EVERYTHING in the cluster.

**Expert:**
Q: Describe the allowlist vs denylist models in security and where each is appropriate.
A: THE FUNDAMENTAL DIFFERENCE: DENYLIST (default-allow): Start with everything permitted. Add rules to BLOCK specific known-bad things. ALLOWLIST (default-deny): Start with everything denied. Add rules to ALLOW specific known-good things. WHY ALLOWLIST IS MORE SECURE: The security asymmetry: an attacker needs ONE unblocked path. A defender using denylist must block ALL bad paths. Defenders can never enumerate all bad things (unknown attacks, zero-days). With denylist: unknown = allowed (attacker wins automatically for any new technique). With allowlist: unknown = denied (attacker must find a path within the allowlist). THE EXAMPLES IN LINUX/CONTAINERS: Seccomp allowlist: defaultAction=SCMP_ACT_ERRNO (deny all syscalls). Then explicitly allow: read, write, open, close, epoll_wait (the ~30 syscalls the app actually uses). Any new attack technique using a novel syscall (e.g., a zero-day via io_uring or BPF): ALREADY DENIED. SELinux: no-access-by-default. Every allow rule is explicit (allow httpd_t httpd_content_t:file {read}). A new file type the policy doesn't mention: denied. AWS IAM: implicit deny on everything. Every Statement must explicitly Allow. Missing an action: denied automatically. Kubernetes NetworkPolicy: without policy, default-allow. With policy applied: default-deny for selected pods. Missing an ingress rule: connection refused. WHERE DENYLIST IS APPROPRIATE: Not as a primary security control, but as supplementary defense: Rate limiting (allow all users, but rate-limit excessive requesters). Anti-spam/WAF (allow all requests, flag known-bad patterns). Content filtering (allow all content, block known-malicious domains). These use denylist BECAUSE the legitimate set is too large to enumerate (every valid HTTP request) and the security impact of a missed-bad-thing is lower (spam gets through, but data isn't exfiltrated). THE OPERATIONAL CHALLENGE OF ALLOWLIST: You must enumerate legitimate operations upfront. Solution: run in audit mode first (SELinux permissive, seccomp log, NetworkPolicy audit). Observe all legitimate traffic. Generate the allowlist from observations. Tools: audit2allow (SELinux), strace (syscall capture), network policy advisor (Kubernetes). Then switch to enforce mode. The maintenance cost: when legitimate behavior changes (new syscall, new network path): update the allowlist explicitly. This is GOOD: unauthorized changes to behavior are denied and visible. OPERATIONAL PRINCIPLE: "Default deny, explicit allow" is the only security posture that doesn't require knowing about threats before blocking them. It blocks all threats - including ones not yet invented - by default.
