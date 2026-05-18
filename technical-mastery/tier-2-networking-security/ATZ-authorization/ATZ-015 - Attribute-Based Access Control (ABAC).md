---
id: ATZ-015
title: "Attribute-Based Access Control (ABAC)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-006, ATZ-007, ATZ-008
used_by: ATZ-026, ATZ-027, ATZ-035, ATZ-036, ATZ-050
related: ATZ-006, ATZ-013, ATZ-016
tags:
  - security
  - authorization
  - abac
  - attribute-based
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/authorization/attribute-based-access-control-abac/
---

⚡ **TL;DR** - ABAC evaluates access based on attributes of the subject
(user), the resource, the action, and the environment (time, location,
device). Unlike RBAC (role membership determines access), ABAC policies
express conditions: "employees can read documents if their clearance
level >= document classification AND they are in the office OR on VPN."
ABAC is more expressive than RBAC but more complex to implement and
reason about. It is used when RBAC role count would explode.

---

### 📊 Entry Metadata

| #015 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-006, ATZ-007, ATZ-008 | |
| **Used by:** | ATZ-026, ATZ-027, ATZ-035, ATZ-036, ATZ-050 | |
| **Related:** | ATZ-006 RBAC, ATZ-013 RBAC Impl, ATZ-016 Claims-Based | |

---

### 🔥 The Problem This Solves

**WHEN RBAC BREAKS DOWN:**

RBAC fails when access depends on object attributes rather
than the subject's role. Examples:

- "Doctors can see patient records - but only their own patients"
  → RBAC cannot express "own patients"; would need one role per patient
- "Analysts can access data classified as CONFIDENTIAL or below"
  → RBAC would need one role per classification level
- "No access to financial data outside business hours"
  → RBAC has no time dimension
- "Senior staff can access large transactions; junior staff only small"
  → RBAC would need roles for every transaction size tier

ABAC handles all of these naturally.

---

### 📘 Textbook Definition

Attribute-Based Access Control (ABAC) is a fine-grained
authorization model where access decisions are based on
evaluating policies against attributes of four entities:
the subject (user attributes: role, department, clearance),
the resource (data sensitivity, owner, classification),
the action (read, write, approve), and the environment
(time of day, IP address, device trust level). ABAC policies
are Boolean expressions over these attributes. XACML (eXtensible
Access Control Markup Language) is the formal standard for
ABAC policy expression; NIST SP 800-162 defines the ABAC model.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of "what role do you have?", ABAC asks "what are
your attributes, the resource's attributes, and the context?"

**RBAC vs ABAC:**

```
RBAC question:
  "Is Alice a DOCTOR?"
  → YES: access granted

ABAC question:
  "Is Alice a DOCTOR?
   AND is this a patient record assigned to Alice?
   AND is Alice accessing from within hospital network?
   AND is the current time between 06:00 and 22:00?"
  → ALL TRUE: access granted
  → ANY FALSE: denied

ABAC policies express intent directly; RBAC approximates it
via roles (sometimes requiring hundreds of roles to approximate
what ABAC expresses in one policy).
```

---

### ⚙️ How It Works (Mechanism)

**ABAC evaluation model (NIST XACML flow):**

```
┌────────────────────────────────────────────────────────┐
│              ABAC Policy Evaluation                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PEP (Policy Enforcement Point)                        │
│    receives: access request (who? what? on what?)      │
│    forwards to PDP                                     │
│                                                        │
│  PIP (Policy Information Point)                        │
│    enriches request with attributes:                   │
│      subject:   user.role, user.clearance,             │
│                 user.department, user.location         │
│      resource:  doc.classification, doc.owner,         │
│                 doc.created_at                         │
│      environ:   current_time, ip_address, device_trust │
│                                                        │
│  PDP (Policy Decision Point) - evaluates policies:     │
│    Policy: "ALLOW if user.role == 'DOCTOR'             │
│             AND resource.patient_id IN user.patients   │
│             AND env.network_zone IN ['hospital','vpn']"│
│    → ALLOW or DENY                                     │
│                                                        │
│  PEP enforces decision: allow or block request         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - ABAC policy evaluation in OPA (Rego)**

```rego
# ABAC: doctors can access their own patients' records
# Policy checks subject, resource, and environment attributes

default allow = false

allow {
    # Subject attribute: user must be a doctor
    input.subject.role == "DOCTOR"
    
    # Resource attribute: patient is assigned to this doctor
    input.resource.assigned_doctor_id == input.subject.id
    
    # Environment attribute: must be during business hours
    # or emergency override is active
    business_hours_or_emergency
}

business_hours_or_emergency {
    # Business hours: 6am - 10pm (UTC)
    hour := time.clock([time.now_ns(), "UTC"])[0]
    hour >= 6
    hour < 22
}

business_hours_or_emergency {
    # Emergency override for on-call physicians
    input.subject.on_call == true
}
```

**Example - BAD vs GOOD: RBAC explosion vs ABAC**

```java
// BAD: RBAC explosion trying to model document sensitivity
// Creates a role for each combination
@PreAuthorize("hasAnyRole(" +
    "'CAN_READ_PUBLIC', " +
    "'CAN_READ_INTERNAL', " +
    "'CAN_READ_CONFIDENTIAL', " +
    "'CAN_READ_SECRET')")
public Document getDocument(Long docId) { ... }
// Still doesn't prevent: a CONFIDENTIAL user
// reading a SECRET document. Would need even more roles.
// 4 sensitivity levels x 5 departments = 20 roles minimum

// GOOD: ABAC policy - user clearance >= doc classification
@Service
public class DocumentAuthzService {
    public boolean canRead(User user, Document doc) {
        // ABAC: compare numeric clearance levels
        // user.clearance: 0=PUBLIC, 1=INTERNAL,
        //                 2=CONFIDENTIAL, 3=SECRET
        if (user.getClearanceLevel() <
                doc.getClassificationLevel()) {
            return false;
        }
        // Additional attribute: same department
        if (doc.isDepartmentRestricted()
                && !user.getDepartment().equals(
                    doc.getDepartment())) {
            return false;
        }
        return true;
    }
}
// One policy handles all combinations
// No role explosion; easy to extend
```

---

### 📏 RBAC vs ABAC Decision Guide

| Use RBAC when | Use ABAC when |
|---|---|
| Access is job-function-based | Access depends on resource attributes |
| Small/stable role set works | Roles would explode (100+) |
| No object-level variation | Same role needs different access to records |
| Simple audit trail needed | Time/location/context affects access |
| Team size < 500 users | Healthcare, government, financial data |

---

*Authorization category: ATZ | Entry: ATZ-015 | v5.0*