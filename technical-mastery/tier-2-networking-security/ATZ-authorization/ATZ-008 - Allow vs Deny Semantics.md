---
id: ATZ-008
title: "Allow vs Deny Semantics"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-007
used_by: ATZ-009, ATZ-013, ATZ-015, ATZ-026, ATZ-027
related: ATZ-007, ATZ-009, ATZ-026
tags:
  - security
  - authorization
  - allow
  - deny
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/authorization/allow-vs-deny-semantics/
---

⚡ **TL;DR** - Every authorization system must answer: what happens
when no rule matches? The answer defines the baseline security posture.
Default-deny (implicit deny) means: if no rule explicitly allows, the
request is denied. Default-allow means: if no rule explicitly denies,
the request is allowed. Default-deny is the secure baseline. Explicit
deny (a Deny rule present) always overrides any Allow - this is the
most important evaluation rule in AWS IAM, Cedar, and OPA.

---

### 📊 Entry Metadata

| #008 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-007 Permissions and Policies | |
| **Used by:** | ATZ-009, ATZ-013, ATZ-015, ATZ-026, ATZ-027 | |
| **Related:** | ATZ-007, ATZ-009 Policy Types, ATZ-026 PBAC | |

---

### 📘 Textbook Definition

In authorization systems, allow/deny semantics define how
conflicting or missing rules are resolved. The evaluation
model has three concepts: implicit deny (default behavior
when no rule matches), explicit allow (a rule that grants
access), and explicit deny (a rule that blocks access).
In systems following the NIST PoLP model, the evaluation
order is: explicit deny takes precedence over explicit allow,
which takes precedence over implicit deny. This ensures that
safety rules cannot be accidentally overridden.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Default-deny means silence = blocked; explicit deny means
no allow-rule can ever override it.

**One analogy:**
> A nightclub with two policies. Default-deny: you are not
> on the list = you do not get in, regardless of what you
> say. Explicit deny (blacklist): even if you are on the
> guest list, if you are on the ban list, you are turned
> away - no exceptions, no negotiation.

---

### ⚙️ How It Works (Mechanism)

**AWS IAM evaluation logic:**

```
┌─────────────────────────────────────────────────────┐
│          Policy Evaluation Order (AWS IAM)          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  REQUEST ARRIVES:                                   │
│    Principal: alice                                 │
│    Action:    s3:DeleteObject                       │
│    Resource:  arn:aws:s3:::important-bucket/doc.pdf │
│                                                     │
│  STEP 1: Is there an explicit DENY?                 │
│    - Check SCPs (org-level) for Deny                │
│    - Check identity policies for Deny               │
│    - Check resource policies for Deny               │
│    If ANY Deny found → DENY (stop, no override)     │
│                                                     │
│  STEP 2: Is there an explicit ALLOW?                │
│    - Check identity policies for Allow              │
│    - Check resource policies for Allow              │
│    - Check permission boundaries                    │
│    If Allow found AND no prior Deny → ALLOW         │
│                                                     │
│  STEP 3: No matching rule                           │
│    → IMPLICIT DENY (default-deny baseline)          │
│                                                     │
│  RESULT: Deny wins over Allow, always.              │
│          No rule = Deny.                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Default-deny vs default-allow:**

| Approach | No rule = | Security posture |
|---|---|---|
| **Default-deny** | Blocked | Secure; must explicitly grant |
| **Default-allow** | Allowed | Unsafe; must explicitly block |

Every production authorization system should use default-deny.
Default-allow is used only in backward-compatible legacy systems
where the cost of enumerating all needed denies is prohibitive.

---

### 💻 Code Examples

**Example - BAD vs GOOD: default posture**

```java
// BAD: default-allow in a custom authorization check
public boolean isAuthorized(User user, String action) {
    List<Rule> rules = policyEngine.getRules(user, action);
    for (Rule rule : rules) {
        if (rule.effect == Effect.DENY) return false;
    }
    // If no rule found: ALLOW (default-allow)
    // Problem: a missing policy = access granted
    return true; // BUG: should be false (default-deny)
}

// GOOD: default-deny
public boolean isAuthorized(User user, String action) {
    List<Rule> rules = policyEngine.getRules(user, action);
    boolean anyAllow = false;
    for (Rule rule : rules) {
        if (rule.effect == Effect.DENY) return false;
        if (rule.effect == Effect.ALLOW) anyAllow = true;
    }
    // Must find an explicit allow; no rule = deny
    return anyAllow;
}
```

**Example - Explicit deny in OPA (Rego)**

```rego
# In OPA, the default is deny (Rego is default-deny)
# You must explicitly define allow rules.
# Explicit deny overrides allow:

default allow = false   # implicit deny baseline

# Allow rule: users can read their own data
allow {
    input.method == "GET"
    input.path == ["users", input.user.id]
}

# Explicit deny: even allowed users cannot access admin
# (explicit deny, cannot be overridden by allow rules)
deny {
    input.path[0] == "admin"
    not input.user.roles[_] == "ADMIN"
}

# Final decision: allow AND NOT deny
authorized {
    allow
    not deny
}
```

**Example - AWS SCP (deny at org level, cannot be overridden)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": ["s3:DeleteBucket", "s3:DeleteBucketPolicy"],
      "Resource": "*"
    }
  ]
}
```

```
This SCP attaches to the entire AWS organization.
Even if an IAM role in any account has:
  "Effect": "Allow", "Action": "s3:DeleteBucket"
The SCP Deny WINS. No account-level policy can override
an organization-level explicit Deny. This is the
architectural power of explicit deny semantics.
```

---

### ⚠️ Common Failure Modes

**Implicit allow due to evaluation short-circuit:**

```
Symptom:
  A new API endpoint added without authorization checks.
  No explicit allow rule exists; no framework annotation.
  The endpoint is accessible to all authenticated users.

Root cause:
  Framework default is "authenticated = authorized" with
  no method-level security configured.

Fix in Spring Security:
  // Require explicit authorization for every endpoint:
  http.authorizeHttpRequests(auth -> auth
      .anyRequest().authenticated() // base requirement
  );
  // Then add explicit allow at method level:
  // @PreAuthorize("hasRole('ADMIN')")
  // If no annotation: access requires authentication only
  // (which is better than no auth, but not role-checked)
  
  // Stronger: require explicit role on every endpoint
  http.authorizeHttpRequests(auth -> auth
      .anyRequest().denyAll() // default-deny all
  );
  // Now every endpoint MUST have explicit @PreAuthorize
```

---

*Authorization category: ATZ | Entry: ATZ-008 | v5.0*