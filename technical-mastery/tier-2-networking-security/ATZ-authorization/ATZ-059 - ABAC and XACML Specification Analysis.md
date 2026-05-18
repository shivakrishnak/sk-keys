---
id: ATZ-059
title: "ABAC and XACML Specification Analysis"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-015, ATZ-026, ATZ-030, ATZ-057, ATZ-058
used_by: ATZ-060
related: ATZ-015, ATZ-026, ATZ-058
tags:
  - security
  - authorization
  - abac
  - xacml
  - specification
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/authorization/abac-and-xacml-specification-analysis/
---

**TL;DR:** XACML (eXtensible Access Control Markup Language)
is the OASIS standard XML specification for ABAC (Attribute-
Based Access Control). XACML 3.0 defines a complete PDP/PEP/PIP/
PAP architecture with request context, policy structure, decision
combining algorithms, and obligations. Its verbosity and XML
complexity drove development of simpler alternatives (OPA/Rego,
Cedar). However, XACML remains important in regulated industries
(healthcare, finance, government) where formal standards
compliance is required.

---

### Textbook Definition

XACML (eXtensible Access Control Markup Language) is the OASIS
standard (2003, 2013 XACML 3.0) for expressing access control
policies and decision requests in XML. It standardizes: policy
structure (PolicySet, Policy, Rule), request/response format,
decision combining algorithms (permit-overrides, deny-overrides,
first-applicable), attribute categories (subject, resource,
action, environment), obligations and advice (post-decision
actions), and the PAP/PDP/PEP/PIP component model. ABAC at
the conceptual level predates XACML; XACML is one
formalization of ABAC using attributes as the policy building
blocks.

---

### How It Works (Mechanism)

```
XACML Decision Flow:
PEP: intercepts request
     -> builds XACML Request (subject attrs, resource, action)
     -> sends to PDP

PDP: evaluates request against policies
     Policy structure:
     PolicySet
       Policy (target: who, what, where)
         Rule (condition: attribute expressions)
           Effect: Permit | Deny
           Obligation: (post-decision action)
     Combining algorithm:
       permit-overrides: ANY permit -> Permit
       deny-overrides: ANY deny -> Deny
       first-applicable: first matching rule wins
     Returns: Permit | Deny | NotApplicable | Indeterminate

PIP: attribute provider (fetches attrs PEP did not supply)
PEP: enforces decision + executes obligations
```

---

### Code Examples

**Example - XACML 3.0 request structure:**

```xml
<!-- XACML Request: "Can Alice read file.txt?" -->
<Request xmlns="urn:oasis:names:tc:xacml:3.0:core:schema:wd-17">
  <Attributes Category="urn:oasis:names:tc:xacml:1.0:
      subject-category:access-subject">
    <Attribute AttributeId="urn:oasis:names:tc:xacml:1.0:
        subject:subject-id">
      <AttributeValue DataType="string">alice</AttributeValue>
    </Attribute>
    <Attribute AttributeId="department">
      <AttributeValue DataType="string">finance</AttributeValue>
    </Attribute>
  </Attributes>
  <Attributes Category="urn:oasis:names:tc:xacml:3.0:
      attribute-category:resource">
    <Attribute AttributeId="resource-id">
      <AttributeValue DataType="string">
        file.txt
      </AttributeValue>
    </Attribute>
    <Attribute AttributeId="classification">
      <AttributeValue DataType="string">
        internal
      </AttributeValue>
    </Attribute>
  </Attributes>
  <Attributes Category="urn:oasis:names:tc:xacml:3.0:
      attribute-category:action">
    <Attribute AttributeId="action-id">
      <AttributeValue DataType="string">read</AttributeValue>
    </Attribute>
  </Attributes>
</Request>
<!-- XACML verbose XML vs. OPA/Cedar: smaller, faster -->
<!-- Modern systems: use OPA/Cedar unless XACML mandated -->
```

---

*Authorization category: ATZ | Entry: ATZ-059 | v5.0*