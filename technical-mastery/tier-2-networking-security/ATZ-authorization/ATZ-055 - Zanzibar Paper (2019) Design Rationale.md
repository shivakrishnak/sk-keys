---
id: ATZ-055
title: "Zanzibar Paper (2019) Design Rationale"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-036, ATZ-037, ATZ-038, ATZ-039
used_by: ATZ-056, ATZ-057, ATZ-060
related: ATZ-036, ATZ-037, ATZ-038
tags:
  - security
  - authorization
  - zanzibar
  - google
  - research
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/authorization/zanzibar-paper-2019-design-rationale/
---

⚡ **TL;DR** - The Zanzibar paper (Google, 2019) describes a global
authorization system that evaluates trillions of ACL checks per
second with p99 latency under 10ms across millions of services.
Its key innovations: (1) a uniform namespace-based tuple model
for expressing any relationship (user:alice, viewer, document:doc1),
(2) a "zookie" (consistency token) that prevents new-enemy
problems (denying access because a replica hasn't seen a recent
permission grant), and (3) aggressive caching with namespace
configs. These design decisions are the basis for SpiceDB,
OpenFGA, and other open-source Zanzibar implementations.

---

### 📊 Entry Metadata

| #055 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-036 ReBAC, ATZ-037 Zanzibar, ATZ-038 SpiceDB/OpenFGA, ATZ-039 Policy Eval | |
| **Used by:** | ATZ-056, ATZ-057, ATZ-060 | |
| **Related:** | ATZ-036 ReBAC, ATZ-037 Zanzibar, ATZ-038 SpiceDB | |

---

### 📘 Textbook Definition

"Zanzibar: Google's Consistent, Global Authorization System"
(2019, USENIX ATC) describes a distributed authorization service
designed for Google-scale access control. Zanzibar's core data
model: relationship tuples `(object:id#relation@user:id)` - e.g.,
`document:doc1#viewer@user:alice`. Check queries traverse the
tuple graph: "is alice a viewer of doc1?" resolves by checking
direct tuples and indirect paths (e.g., "alice is a member of
group:editors, and editors are viewers of doc1"). The zookie
(Zanzibar Object Consistency Token) is a timestamp-encoded token
issued with each tuple write, which clients pass back on reads to
ensure they see the write and avoid the "new-enemy problem"
(where a user who was just granted access is still denied because
the read hit a stale replica).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Zanzibar Data Model and Check Algorithm        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  TUPLE MODEL:                                          │
│  (object_type:object_id#relation@user_type:user_id)    │
│  document:budget#owner@user:alice                      │
│  document:budget#viewer@group:finance                  │
│  group:finance#member@user:bob                         │
│                                                        │
│  CHECK QUERY: can alice view budget?                   │
│  -> direct check: document:budget#viewer@user:alice?   │
│     not found                                          │
│  -> indirect check: user alice is member of any group  │
│     that is a viewer of budget?                        │
│     group:finance#member@user:alice? not found         │
│  -> check: document:budget#owner@user:alice?           │
│     FOUND! owner implies viewer (namespace config)     │
│  -> ALLOW                                              │
│                                                        │
│  NEW-ENEMY PROBLEM:                                    │
│  1. Bob was denied access to doc                       │
│  2. Admin grants bob#viewer on doc (write to Zanzibar) │
│  3. Bob immediately retries access                     │
│  4. Read hits stale replica: grant not visible yet     │
│  5. Bob still denied (inconsistent)                    │
│                                                        │
│  ZOOKIE FIX:                                           │
│  - Write returns zookie (encoded timestamp)            │
│  - Client passes zookie on next read                   │
│  - Zanzibar: serves read from replica that has         │
│    applied up to zookie timestamp                      │
│  - Bob always sees his new permission                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Zanzibar check with zookie (consistency token)**

```python
# OpenFGA (Zanzibar implementation) Python SDK
import openfga_sdk
from openfga_sdk.models import (
    CheckRequest, TupleKey, ReadAuthorizationModelRequest
)

async def check_with_consistency():
    config = openfga_sdk.Configuration(
        api_scheme="https",
        api_host="api.fga.example"
    )
    client = openfga_sdk.OpenFgaClient(config)

    # After writing a tuple, save the response token
    write_resp = await client.write({
        "writes": {
            "tuple_keys": [{
                "object": "document:budget",
                "relation": "viewer",
                "user": "user:bob"
            }]
        }
    })
    # write_resp contains continuation_token (the "zookie")
    zookie = write_resp.writes[0].timestamp

    # Check with zookie: ensures read sees the write
    # Without zookie: might hit stale replica, deny Bob
    result = await client.check({
        "tuple_key": {
            "object": "document:budget",
            "relation": "viewer",
            "user": "user:bob"
        },
        # consistency_token = zookie ensures fresh read
        "consistency": "HIGHER_CONSISTENCY"
    })
    # allowed: True (bob sees new permission immediately)
    return result.allowed
```

---

*Authorization category: ATZ | Entry: ATZ-055 | v5.0*