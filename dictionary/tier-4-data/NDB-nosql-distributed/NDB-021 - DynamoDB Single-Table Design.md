---
version: 2
layout: default
title: "DynamoDB Single-Table Design"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /nosql/dynamodb-single-table-design/
id: NDB-024
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: DynamoDB Data Modeling Patterns, DynamoDB, NoSQL
used_by: AWS, Microservices
related: DynamoDB Data Modeling Patterns, Access Patterns, NoSQL Data Modeling
tags:
  - database
  - aws
  - distributed
  - advanced
  - pattern
---

# NDB-021 - DynamoDB Single-Table Design

⚡ TL;DR - Single-table design co-locates multiple entity types in one DynamoDB table using overloaded PK/SK attributes, enabling hierarchical queries and reducing network roundtrips - at the cost of schema opacity.

| Relation | Keywords |
|---|---|
| Depends on | DynamoDB Data Modeling Patterns, DynamoDB, NoSQL |
| Used by | AWS, Microservices |
| Related | DynamoDB Data Modeling Patterns, Access Patterns, NoSQL Data Modeling |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A DynamoDB-based order management system has five tables: `users`, `orders`, `orderItems`, `products`, `addresses`. Rendering an order detail page requires five separate DynamoDB API calls - one per table. At 10 000 concurrent order pages, that's 50 000 DynamoDB requests per second instead of 10 000. AWS API Gateway and Lambda invocations multiply. Latency is the sum of five sequential or parallel requests rather than one. Cross-entity transactions require DynamoDB Transactions across multiple tables - which adds latency and cost (2× WCU).

**THE BREAKING POINT:** The "one table per entity" design also prevents certain access patterns. "Get a user's profile, their 5 most recent orders, and the first item of each order" requires three query operations minimum. DynamoDB has no join operation - each fetch is independent. The team writes N+1 query code patterns in Lambda that the relational-trained engineers kept promising they would fix in SQL.

**THE INVENTION MOMENT:** Alex DeBrie and Rick Houlihan popularized the **single-table design** pattern: co-locate multiple entity types in one DynamoDB table by overloading the PK and SK attributes with entity-type prefixes (`USER#123`, `ORDER#456`, `ITEM#789`). Related entities for the same parent share the same PK, enabling a single `Query` call to return a user's profile, all their orders, and all order items in one round-trip. The access pattern matrix replaces the entity-relationship diagram as the primary design artifact.

---

### 📘 Textbook Definition

**DynamoDB Single-Table Design** is a data modeling technique in which all entity types for an application (users, orders, products, sessions, etc.) are stored in a single DynamoDB table. Entities are distinguished by a **type attribute** (e.g., `entityType: "USER"`). **Composite sort keys** (e.g., `SK = "ORDER#2024-01-15#ORD-001"`) enable hierarchical range queries within a partition. **Overloaded GSI attributes** (e.g., `GSI1PK` and `GSI1SK`) carry entity-type-specific values to support multiple query dimensions with one GSI. An **access pattern matrix** documents every query the application needs and the specific DynamoDB operation (GetItem/Query/GSI query) that serves it. The pattern maximizes use of DynamoDB's single-operation read capabilities, minimizing roundtrips and enabling atomic single-partition operations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Single-table design stores every entity type in one table - one `Query` by PK returns a user's profile, their orders, and order items simultaneously.

> Think of a single-table design like a bank's general ledger vs. separate department ledgers. A separate ledger per department (multi-table) requires looking up three books to reconcile a transaction. The general ledger (single table) has all entries in one place - encoded by account type prefix (`ASSET-001`, `LIABILITY-002`) - one scan of the relevant entries tells the whole story.

**One insight:** The power of single-table design is not just fewer tables - it is the ability to perform hierarchical queries ("give me everything related to this user in one operation") that would require 3–5 separate requests in a multi-table design. This maps directly to how DynamoDB's partition-local `Query` works.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A DynamoDB `Query` operation retrieves all items with a given PK (and optional SK condition) in one request - regardless of how many entity types those items represent, as long as they share the PK prefix.
2. **Composite sort keys** (e.g., `ORDER#2024-01-15T10:30:00#ORD-001`) enable prefix queries (`SK begins_with "ORDER#"`) and range queries (`SK between "ORDER#2024-01-01" and "ORDER#2024-12-31"`) within a partition.
3. The `entityType` attribute distinguishes items of different types within the same PK - application code filters after retrieval.
4. **Overloaded GSI attributes** (`GSI1PK`, `GSI1SK`) carry entity-specific values, allowing one GSI to support queries for multiple entity types - each entity type populates these attributes with different semantics.
5. A single-table design can retrieve a parent entity and all its children in a single `Query`, then split the results by `entityType` in application code - this is called the **aggregate** pattern.

**DERIVED DESIGN:**

- Always define `PK` and `SK` as generic attribute names (not `userId`, `orderId`) - they hold different logical values for different entity types.
- Use type prefixes consistently: `USER#`, `ORDER#`, `PRODUCT#`, `ITEM#` as PK or SK prefixes.
- Build the **access pattern matrix** before writing any code: columns are access patterns; rows document PK, SK condition, index used, and response entities.
- Validate every access pattern in the matrix is serviceable by a `GetItem` or `Query` - no pattern should require a `Scan`.

**THE TRADE-OFFS:**

**Gain:** Hierarchical queries in a single roundtrip; fewer network calls = lower latency; single-partition transactions (`TransactWriteItems`) work atomically across entity types that share a PK; operational simplicity (one table to monitor, backup, and restore).

**Cost:** Schema opacity - the table is nearly unreadable without the access pattern matrix documentation; debugging with the AWS Console requires knowing the key structure; all entity types share the same WCU/RCU provisioning (a busy entity type can throttle quieter ones unless on-demand mode is used); new access patterns require careful GSI design or a full table migration.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce order management system. Access patterns:
1. Get user profile by userId.
2. Get all orders for a user, newest first.
3. Get all items for an order.
4. Get all pending orders for fulfillment.
5. Get a user's profile AND their last 3 orders in one operation.

**WHAT HAPPENS WITH MULTI-TABLE DESIGN:**
- Tables: `users`, `orders`, `orderItems`.
- Access pattern 5: two separate `GetItem`/`Query` calls → 2 round-trips → higher latency, no atomicity.
- Access pattern 4: requires a GSI on the `orders` table with `PK=status`.
- Five separate tables to manage, monitor, backup.

**WHAT HAPPENS WITH SINGLE-TABLE DESIGN:**

Table: `ecommerce` - one table:
```
PK=USER#123, SK=PROFILE          → user entity
PK=USER#123, SK=ORDER#2024-12-01 → order entity
PK=USER#123, SK=ORDER#2024-11-15 → order entity
PK=ORDER#ORD-001, SK=ITEM#1      → order item entity
PK=ORDER#ORD-001, SK=ITEM#2      → order item entity
```

Access pattern 5: `Query(PK=USER#123, SK begins_with "ORDER#", ScanIndexForward=False, Limit=3)` - returns the user's profile AND last 3 orders in one call (by also querying `SK=PROFILE` or fetching it in the same call with `SK >= "PROFILE" AND SK <= "PROFILE~"`).

Access pattern 4: GSI1 with `GSI1PK = "STATUS#pending"` populated only on order entities - sparse GSI returns only pending orders.

**THE INSIGHT:** The single-table design collapses a parent + N children query from N+1 round-trips to exactly 1 `Query` call. This is only possible because DynamoDB's `Query` operation is partition-local - all items with the same PK are co-located on the same physical partition, regardless of entity type.

---

### 🧠 Mental Model / Analogy

> Single-table design is like a hospital's unified patient record system. Instead of separate filing cabinets for lab results, prescriptions, surgery notes, and insurance records, all records for one patient are in one folder under the patient's ID. Each record type is tagged (LAB-2024-01-15, RX-METFORMIN, SURGERY-2023-06-10). A doctor who needs a full patient history pulls one folder and finds everything sorted by type and date - instead of visiting four filing rooms.

- **One folder per patient** = one DynamoDB partition per parent entity (PK=PATIENT#123)
- **Record type tags** = entity type prefixes in SK (LAB#, RX#, SURGERY#)
- **Sorted by date within type** = composite SK with timestamp (LAB#2024-01-15)
- **Cross-patient queries** (all diabetes patients) = GSI on diagnosis attribute → separate "specialist index"

Where this analogy breaks down: a physical folder is sequential; DynamoDB can retrieve only items matching `SK begins_with "LAB#"` without scanning the entire patient folder - the sort key provides a binary-search capability within the partition that a physical folder cannot.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Single-table design means putting all your data types (users, orders, products) into one DynamoDB table, organized by smart labels, so that one request to the database can return everything related to one customer at once - instead of five separate requests.

**Level 2 - How to use it (junior developer):**
Name your PK and SK generically (`PK`, `SK`). Use type prefixes: users write `PK=USER#<id>, SK=PROFILE`; orders write `PK=USER#<id>, SK=ORDER#<date>#<orderId>`. Use `entityType` attribute for filtering in application code. Build the access pattern matrix first. Create GSIs with generic names (`GSI1PK`, `GSI1SK`) that different entity types populate for their own access patterns.

**Level 3 - How it works (mid-level engineer):**
When you issue `Query(PK=USER#123)`, DynamoDB returns all items in the `USER#123` partition - profile items, order items, address items - all sorted by SK ascending. Your application receives a mixed array and filters by `entityType` or SK prefix. This is a single partition read: one DynamoDB call, one network round-trip, billed at 1 RCU per 4 KB of returned data. The GSI overloading works because GSI1PK and GSI1SK are generic attributes that each entity type populates differently - user entities might set `GSI1PK=EMAIL#<email>`, while order entities set `GSI1PK=STATUS#<status>`. The GSI serves both entity types' alternate access patterns without needing separate GSIs.

**Level 4 - Why it was designed this way (senior/staff):**
Single-table design is a direct consequence of DynamoDB's partition-local Query semantics and its lack of JOIN operations. In a system designed for millisecond latency at unlimited scale, the only way to achieve a "get everything about this user" query in sub-10ms is to ensure all related data is in the same partition. The technique was not obvious at DynamoDB's launch - engineers spent years applying relational habits until the community (led by AWS hero Rick Houlihan) systematized the access-pattern-first approach and the single-table pattern. The trade-off between query power and schema readability is deliberate: DynamoDB is not a general-purpose database but a specialized high-performance OLTP engine. Single-table design accepts schema opacity as the price for partition-local queries. Whether this trade-off is correct for a given system depends entirely on whether query performance and scale requirements justify the operational complexity.

---

### ⚙️ How It Works (Mechanism)

**Access Pattern Matrix (the primary design artifact):**

```
Pattern             PK           SK Condition      Index   Returns
────────────────────────────────────────────────────────────────────
Get user by ID      USER#<id>    SK=PROFILE        -       User
Get user orders     USER#<id>    SK begins_w ORDER# -      Orders[]
Get order items     ORDER#<id>   SK begins_w ITEM#  -      Items[]
Get pending orders  -            -                 GSI2    Orders[]
Get user by email   -            -                 GSI1    User
Get order by ID     ORDER#<id>  SK=METADATA        -       Order
Get user+orders     USER#<id>    SK >= PROFILE      -      User+Orders[]
```

**Overloaded GSI Design:**

```
GSI1PK and GSI1SK populated per entity type:

User entity:
  GSI1PK = EMAIL#user@example.com
  GSI1SK = USER#<userId>
  → GSI1 query by email → get user

Order entity:
  GSI1PK = STATUS#pending
  GSI1SK = CREATED#2024-01-15
  → GSI1 query by status+date → get orders

Product entity:
  GSI1PK = CATEGORY#electronics
  GSI1SK = PRICE#149.99
  → GSI1 query by category, range on price
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Access Pattern Matrix defined (all queries listed)
          │
          ▼
Assign PK/SK patterns per entity type
Assign GSI1PK/GSI1SK overloaded values
          │
          ▼
Write user:
  PK=USER#123, SK=PROFILE
  GSI1PK=EMAIL#alice@example.com     ← YOU ARE HERE
  entityType=USER, ...user fields...
          │
          ▼
Write order:
  PK=USER#123, SK=ORDER#2024-12-15#ORD-001
  GSI2PK=STATUS#pending
  entityType=ORDER, ...order fields...
          │
          ▼
Query: PK=USER#123, SK begins_with ORDER#
  Returns all orders for user in one call
          │
          ▼
Application: filter results by entityType
  → user profile (SK=PROFILE)
  → order list (SK begins_with ORDER#)
```

**FAILURE PATH:**
- Accessing wrong entity type via same PK: application code must filter by `entityType` attribute or SK prefix; missing filter returns unexpected item types
- New access pattern after launch: requires either a new GSI (can add) or a table migration (if PK/SK design must change)
- Hot partition from overloaded PK: if one user has millions of orders in the same partition, that PK becomes a hot partition (same problem as before, different shape)
- GSI attribute naming collision: two entity types use `GSI1PK` with incompatible semantics → queries return mixed entity types requiring additional filtering

**WHAT CHANGES AT SCALE:**
- Partition size: single-table design co-locates entities → a user with millions of orders accumulates > 10 GB in one partition → DynamoDB auto-splits, but all splits remain under the same PK → throughput distribution is maintained, but monitoring becomes harder
- Observability: CloudWatch metrics are per-table, not per-entity-type → monitoring a single-table design requires application-layer metrics to distinguish entity-type throughput
- Migration: changing schema in a single-table design requires migrating all entity types simultaneously - a coordinated effort that is more complex than migrating one entity-specific table

---

### 💻 Code Example

**BAD - multi-table design, N+1 queries for order page:**
```python
# Five separate DynamoDB calls for one order detail page

async def get_order_page(user_id, order_id):
    user = await users_table.get_item(
        Key={'userId': user_id}
    )
    order = await orders_table.get_item(
        Key={'orderId': order_id}
    )
    items = await order_items_table.query(
        KeyConditionExpression=Key('orderId').eq(order_id)
    )
    # 3 separate round-trips; no atomicity
    return {**user, **order, 'items': items}
```

**GOOD - single-table design, one query per hierarchical read:**
```python
import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource('dynamodb').Table('ecommerce')

# Write user entity
table.put_item(Item={
    'PK': 'USER#user-123',
    'SK': 'PROFILE',
    'entityType': 'USER',
    'GSI1PK': 'EMAIL#alice@example.com',
    'GSI1SK': 'USER#user-123',
    'name': 'Alice Smith',
    'email': 'alice@example.com',
    'createdAt': '2024-01-01T00:00:00Z'
})

# Write order entity (co-located with user by same PK)
table.put_item(Item={
    'PK': 'USER#user-123',         # same PK as user!
    'SK': 'ORDER#2024-12-15T10:30#ORD-001',
    'entityType': 'ORDER',
    'GSI2PK': 'STATUS#pending',    # sparse GSI for fulfillment
    'GSI2SK': '2024-12-15T10:30:00Z',
    'orderId': 'ORD-001',
    'total': 99.99,
    'status': 'pending'
})

# Write order items (own partition by orderId)
table.put_item(Item={
    'PK': 'ORDER#ORD-001',
    'SK': 'ITEM#item-001',
    'entityType': 'ORDER_ITEM',
    'productId': 'prod-456',
    'qty': 2,
    'price': 49.99
})

# Access Pattern 1: get user profile + all orders in ONE call
def get_user_with_orders(user_id: str):
    response = table.query(
        KeyConditionExpression=(
            Key('PK').eq(f'USER#{user_id}')
        ),
        ScanIndexForward=False  # newest SK first
    )
    items = response['Items']

    # Split by entity type
    profile = next(
        (i for i in items if i['entityType'] == 'USER'),
        None
    )
    orders = [i for i in items if i['entityType'] == 'ORDER']

    return {'profile': profile, 'orders': orders}

# Access Pattern 2: get pending orders (sparse GSI)
def get_pending_orders(limit: int = 100):
    response = table.query(
        IndexName='GSI2',
        KeyConditionExpression=(
            Key('GSI2PK').eq('STATUS#pending')
        ),
        Limit=limit
    )
    return response['Items']

# Access Pattern 3: get user by email (GSI1)
def get_user_by_email(email: str):
    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression=(
            Key('GSI1PK').eq(f'EMAIL#{email}')
        ),
        Limit=1
    )
    items = response['Items']
    return items[0] if items else None
```

---

### ⚖️ Comparison Table

| Aspect | Single-Table Design | Multi-Table Design |
|---|---|---|
| Roundtrips for hierarchical read | 1 (Query by PK) | N+1 (one per entity type) |
| Schema readability | Low (opaque key encoding) | High (self-documenting tables) |
| GSI count | Fewer (overloaded for multiple entity types) | More (each table may need own GSIs) |
| Cross-table transactions | N/A (same table) | TransactWriteItems (multi-table, 2× WCU) |
| New access pattern cost | GSI addition or migration | GSI addition per affected table |
| Monitoring granularity | Table-level only | Per-table metrics |
| Best for | Highly relational, latency-critical workloads | Independent entities, separate scaling needs |
| Operational complexity | High (schema docs required) | Lower (tables are self-evident) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Single-table design is always better than multi-table" | Single-table design is optimal for access patterns that need hierarchical reads and transactional writes; multi-table design is simpler and appropriate for independent entities with separate lifecycle |
| "Single-table design eliminates all joins" | It eliminates DynamoDB-level joins; the application still performs entity separation (filtering by `entityType`), which is effectively a post-retrieval join |
| "All DynamoDB applications should use single-table design" | AWS documentation and community now acknowledges multi-table design as valid; single-table is a pattern, not a mandate - use it when the access patterns justify it |
| "One GSI per access pattern is required" | Overloaded GSIs allow one GSI to serve multiple entity types' access patterns by populating `GSI1PK`/`GSI1SK` with entity-specific values |
| "Single-table design prevents hot partitions" | It does not - a user with millions of orders in one partition is just as hot as any other hot partition; the pattern changes schema structure, not partition distribution physics |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Schema Rot - Undocumented Access Patterns**

**Symptom:** New engineers cannot understand the table structure; DynamoDB console shows cryptic key values (`USER#123`, `ORDER#2024-12-15#ORD-001`) with no explanation; a new feature breaks because a developer wrote a `Scan` not knowing a GSI existed.
**Root Cause:** The access pattern matrix was not created or not maintained; single-table design's schema opacity is invisible without documentation.
**Diagnostic:**
```bash
# Enumerate all GSI names and their index keys
aws dynamodb describe-table --table-name ecommerce \
  | jq '.Table.GlobalSecondaryIndexes[] |
    {IndexName, KeySchema, Projection}'

# Sample 10 items to understand PK/SK patterns
aws dynamodb scan \
  --table-name ecommerce \
  --max-items 10 \
  --projection-expression "PK,SK,entityType"
```
**Fix:** Create and maintain an access pattern matrix document co-located with the table infrastructure (IaC). Add it to code review checklist for any DynamoDB change.
**Prevention:** Treat the access pattern matrix as a first-class design artifact, version-controlled alongside schema code. Every new query must first be added to the matrix before being implemented.

---

**Failure Mode 2: GSI Attribute Collision Between Entity Types**

**Symptom:** A GSI query returns both user entities and order entities unexpectedly; application code assumes a `GSI1` query returns only users but receives mixed types; null pointer errors when accessing order-only fields on a returned user item.
**Root Cause:** Two entity types both set `GSI1PK` to semantically different values that happen to match in a query (e.g., user's `GSI1PK=EMAIL#user@example.com` and a product's `GSI1PK=EMAIL#newsletter` - both start with `EMAIL#`).
**Diagnostic:**
```python
# Sample GSI contents to find entity type distribution
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression=Key('GSI1PK').eq('EMAIL#user@example.com')
)
# Check entityType distribution in results
for item in response['Items']:
    print(item.get('entityType'), item.get('PK'))
```
**Fix:** Add `entityType` filter in all GSI queries that should return only one entity type. Use `FilterExpression=Attr('entityType').eq('USER')` on the query.
**Prevention:** In the access pattern matrix, document which entity types populate each GSI attribute and what values they use. Establish naming conventions that prevent overlap (e.g., entity type prefixes in GSI values: `USER#EMAIL#`, `PRODUCT#CAT#`).

---

**Failure Mode 3: Accidental Table Scan Due to Missing Access Pattern**

**Symptom:** Lambda function timeout; DynamoDB scan consuming massive RCUs; CloudWatch shows `ConsumedReadCapacityUnits` 100× normal; billing spike.
**Root Cause:** A new access pattern was added without a corresponding GSI; the developer used a `scan` with `FilterExpression` (equivalent to a SQL full table scan with WHERE clause on data, not key).
**Diagnostic:**
```bash
# Find scan operations in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name SuccessfulRequestLatency \
  --dimensions \
    Name=TableName,Value=ecommerce \
    Name=Operation,Value=Scan \
  --period 3600 --statistics SampleCount

# Also check: DynamoDB contributor insights
aws dynamodb describe-contributor-insights \
  --table-name ecommerce
```
**Fix:** Add a GSI for the new access pattern. Immediately disable or rate-limit the scan in application code while the GSI is being added (GSI backfill takes minutes to hours depending on table size).
**Prevention:** Code review policy: any `table.scan()` call without a documented access pattern exception requires architecture review. Consider adding a lint rule that flags `Scan` in production DynamoDB code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DynamoDB Data Modeling Patterns - the foundational patterns (composite keys, GSI/LSI, write sharding) that single-table design orchestrates
- DynamoDB - the underlying service mechanics: partition model, RCU/WCU, consistency models
- NoSQL - the design philosophy of access-pattern-driven schema design

**Builds On This (learn these next):**
- AWS - production operations: DynamoDB Streams for event sourcing, point-in-time recovery, global tables for multi-region replication
- Microservices - single-table design enables a microservice to own one DynamoDB table serving all its entity types with isolation

**Alternatives / Comparisons:**
- DynamoDB Data Modeling Patterns - the underlying patterns; single-table design is their opinionated orchestration
- Access Patterns - the first-class design artifact that single-table design is built around
- NoSQL Data Modeling - the broader discipline of which DynamoDB single-table is one specialized technique

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    All entity types in one DynamoDB  │
│               table; overloaded PK/SK/GSI keys  │
│ PROBLEM       Multi-table = N+1 roundtrips for  │
│               hierarchical reads; no atomicity  │
│ KEY INSIGHT   Same PK = same partition = one    │
│               Query returns parent + children   │
│ USE WHEN      Latency-critical hierarchical     │
│               reads; related entities transact  │
│ AVOID WHEN    Entities have independent scale;  │
│               team lacks DynamoDB expertise     │
│ TRADE-OFF     1-roundtrip reads vs schema       │
│               opacity and rigid access patterns │
│ ONE-LINER     Access pattern matrix first;      │
│               then PK→SK→GSI→entityType         │
│ NEXT EXPLORE  AWS (DynamoDB Streams, Global     │
│               Tables, Point-in-Time Recovery)   │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(C - Design Trade-off)** A startup uses single-table design for their entire application: users, orders, products, invoices, and audit logs - all in one table. Six months later, the audit log entity type is generating 10 000 WCUs/second, starving the order processing entity types. Describe the exact problem this creates under provisioned capacity mode and under on-demand mode, and explain whether single-table design was the correct choice for this mixed-workload scenario.

2. **(F - Comparison)** For an e-commerce order management system, compare single-table design vs multi-table design across five dimensions: query roundtrips, transactional atomicity, new team member onboarding time, adding a new entity type, and GSI cost. For each dimension, which design wins and under what specific conditions does the "loser" become the better choice?

3. **(A - System Interaction)** In a single-table design, you use DynamoDB Streams to trigger a Lambda function that maintains a materialized count of `pending` orders per user. The stream fires on every write to the table - across all entity types (user updates, product updates, order items). Describe the exact filtering logic required in the Lambda to avoid processing irrelevant events, the risk of Lambda cold starts under burst traffic, and how DynamoDB Streams' ordering guarantees interact with concurrent order status updates.
