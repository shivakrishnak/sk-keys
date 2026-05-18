---
id: ATZ-038
title: "SpiceDB and OpenFGA (Zanzibar Implementations)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-036, ATZ-037
used_by: ATZ-046, ATZ-047, ATZ-050
related: ATZ-036, ATZ-037, ATZ-046
tags:
  - security
  - authorization
  - spicedb
  - openfga
  - zanzibar
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/authorization/spicedb-and-openfga-zanzibar-implementations/
---

⚡ **TL;DR** - SpiceDB (Authzed) and OpenFGA (Auth0/Okta) are the
two leading open-source Zanzibar-inspired authorization systems.
SpiceDB has the most complete Zanzibar feature set including
caveats (conditional relationships) and is backed by Authzed.
OpenFGA has a simpler API and strong Auth0/Okta ecosystem
integration. Both store relationship tuples, expose check/read/
write APIs, and support schema definition. Use them when RBAC or
ABAC is insufficient for your sharing model (nested resources,
group inheritance, user-to-user delegation).

---

### 📊 Entry Metadata

| #038 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-036 ReBAC, ATZ-037 Zanzibar | |
| **Used by:** | ATZ-046, ATZ-047, ATZ-050 | |
| **Related:** | ATZ-036 ReBAC, ATZ-037 Zanzibar, ATZ-046 Perf at Scale | |

---

### 📘 Textbook Definition

SpiceDB and OpenFGA are open-source, production-grade
relationship-based authorization systems implementing the Google
Zanzibar model. Both provide: a relationship store (write and
read access control tuples), a schema language (define object
types and permissions), a check API (is user X authorized for
action Y on resource Z?), and a consistency model (configurable
between minimum-latency and fully-consistent). SpiceDB uses a
custom Zed schema language with caveats for conditional
relationships; OpenFGA uses a JSON-based authorization model
with close alignment to Auth0's product offerings. Both expose
gRPC and HTTP APIs.

---

### ⚙️ How It Works (Mechanism)

**SpiceDB vs OpenFGA comparison:**

```
┌────────────────────────────────────────────────────────┐
│         SpiceDB vs OpenFGA                             │
├───────────────────┬──────────────┬─────────────────────┤
│  Feature          │ SpiceDB      │ OpenFGA             │
├───────────────────┼──────────────┼─────────────────────┤
│  Schema language  │ Zed (Zanzibar│ JSON authorization  │
│                   │  native)     │ model               │
│  Caveats          │ YES          │ Conditions (v1.4+)  │
│  Consistency      │ Zookies +    │ Consistency tokens  │
│                   │ 4 modes      │                     │
│  gRPC API         │ YES          │ YES                 │
│  HTTP API         │ YES          │ YES                 │
│  Managed cloud    │ Authzed.com  │ Auth0 FGA           │
│  Backing store    │ Postgres,    │ Postgres,           │
│                   │ CockroachDB  │ MySQL, SQLite        │
│  Kubernetes       │ Helm chart   │ Helm chart          │
│  Batch check      │ YES          │ YES                 │
│  Schema validation│ CLI tool     │ SDK + CLI           │
└───────────────────┴──────────────┴─────────────────────┘

WHEN TO CHOOSE:
SpiceDB: full Zanzibar model needed, caveats required,
  complex permission schemas with many relations
OpenFGA: Auth0/Okta ecosystem, simpler model,
  ABAC conditions on relationships needed
Neither: if RBAC + row-level security covers your needs
  (simpler, less operational overhead)
```

---

### 💻 Code Examples

**Example - OpenFGA authorization check (Java)**

```java
@Service
public class OpenFgaAuthorizationService {

    private final OpenFgaApi fgaApi;
    private final String storeId;
    private final String authModelId;

    public boolean canUserPerformAction(
            String userId, String action,
            String objectType, String objectId)
            throws FgaInvalidParameterException,
                   ApiException {
        CheckRequest checkRequest = new CheckRequest()
            .authorizationModelId(authModelId)
            .tupleKey(new CheckRequestTupleKey()
                .user("user:" + userId)
                .relation(action)
                ._object(objectType + ":" + objectId));

        CheckResponse response = fgaApi
            .check(storeId, checkRequest);
        return Boolean.TRUE.equals(response.getAllowed());
    }

    public void writeRelationship(
            String userId, String relation,
            String objectType, String objectId)
            throws Exception {
        WriteRequest write = new WriteRequest()
            .authorizationModelId(authModelId)
            .writes(new WriteRequestWrites()
                .tupleKeys(List.of(
                    new TupleKey()
                        .user("user:" + userId)
                        .relation(relation)
                        ._object(objectType + ":" + objectId)
                )));
        fgaApi.write(storeId, write);
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-038 | v5.0*