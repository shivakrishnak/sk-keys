---
version: 1
layout: default
title: "DynamoDB"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /cloud-aws/dynamodb/
id: AWS-061
category: "Cloud - AWS"
difficulty: "★★★"
depends_on:
  ["AWS Global Infrastructure", "IAM (Identity and Access Management)"]
used_by: ["ElastiCache", "AWS Cost Optimization"]
related: ["RDS", "Aurora", "ElastiCache", "Kinesis"]
tags: [aws, dynamodb, nosql, key-value, document, database, cloud]
---

# DynamoDB

## ⚡ TL;DR

**DynamoDB** is AWS's fully managed, serverless NoSQL key-value and document database. Single-digit millisecond performance at any scale. Scales to 10 trillion requests/day. Two capacity modes: **On-Demand** (pay per request) and **Provisioned** (set RCU/WCU, cheaper at steady load). Key design rule: **single-table design** - model all entities in one table with composite keys. Wrong key design = scans + slow queries.

---

## 🔥 Problem This Solves

Relational DBs require schema upfront, vertical scaling, and complex sharding for web-scale. DynamoDB: schema-less (add attributes freely), horizontal scaling automatic, single-digit ms P99 at millions of requests/sec. Trade: no JOINs, no complex queries - design access patterns upfront.

---

## 📘 Textbook Definition

Amazon DynamoDB is a key-value and document database delivering single-digit millisecond performance at any scale. It is fully managed (no servers, no patching), multi-Region active-active available (Global Tables), and supports event-driven architectures via DynamoDB Streams. Items have a partition key (PK) and optional sort key (SK); secondary indexes (GSI/LSI) enable additional access patterns.

---

## ⏱️ 30 Seconds

```
Table structure:
  PK (partition key):  hash key; determines storage partition
  SK (sort key):       range key; enables sort/range queries
  Attributes:          any additional fields (flexible schema)

Capacity modes:
  On-Demand:    $1.25/million writes, $0.25/million reads
  Provisioned:  set RCU (read) and WCU (write) per second
                RCU: $0.00013/hr; WCU: $0.00065/hr

Secondary Indexes:
  GSI (Global Secondary Index): different PK+SK, own throughput
  LSI (Local Secondary Index):  same PK, different SK (must define at creation)

Important limits:
  Max item size: 400KB
  PK uniqueness determines partition; SK enables range queries
```

---

## 🔩 First Principles

- **Partition key hashing**: DynamoDB hashes PK to determine which storage partition holds item; hot partitions = throttling
- **Single-table design**: multiple entity types in one table using prefixed keys (e.g., PK=`USER#123`, SK=`ORDER#456`)
- **RCU/WCU**: 1 RCU = 1 strongly consistent read of ≤4KB; 1 WCU = 1 write of ≤1KB
- **Eventually consistent reads**: half the RCU cost; reads may lag behind writes
- **GSI**: project attributes + own throughput; eventually consistent with base table
- **DynamoDB Streams**: change data capture; records inserts/updates/deletes; triggers Lambda

---

## 🧪 Thought Experiment

E-commerce: User has Orders, Orders have Items. SQL: 3 tables with JOINs. DynamoDB single-table: `PK=USER#123, SK=METADATA` (user profile), `PK=USER#123, SK=ORDER#456` (order belonging to user), `PK=ORDER#456, SK=ITEM#789` (item in order). Query "all orders for user 123": `Query PK=USER#123, SK begins_with ORDER#`. Zero table scans, O(log n) regardless of database size.

---

## 🧠 Mental Model / Analogy

DynamoDB is a **giant hash map + sorted set**: PK is the hash map key (which drawer in the filing cabinet), SK is the position within that drawer (alphabetically sorted). Queries work when you know the drawer (PK); additional sorting/filtering within a drawer (SK) is fast. Looking for something across all drawers (scan) = slow and expensive. Design your drawers to match your access patterns.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create table with PK and SK. Put/Get/Delete items. Understand that you can only query by PK (and optionally SK). Don't use Scan in production.

**Level 2 - Practitioner**: GSI: create alternate access pattern (e.g., query orders by status). On-Demand for variable/spiky workloads; Provisioned + Auto Scaling for steady workloads. TTL: set expiration attribute on items (automatic cleanup). DynamoDB Streams + Lambda for event-driven processing.

**Level 3 - Advanced**: Single-table design patterns: adjacency list (entity relationships), GSI overloading (reuse GSI for multiple access patterns using prefixed keys), composite sort keys. Transactions: `TransactWriteItems` for multi-item ACID operations (up to 100 items). Conditional writes: `ConditionExpression` for optimistic locking.

**Level 4 - Expert**: DynamoDB Global Tables: active-active multi-region replication (last-writer-wins conflict resolution). Partition key design for uniform distribution: avoid hot partitions (user ID, timestamp as sole PK with high cardinality = good; static values = bad). Read/write amplification with GSIs: write to base table → DynamoDB replicates to all GSIs (total WCU = base write + GSI writes). DynamoDB Accelerator (DAX): in-memory caching layer; microsecond reads for eventually consistent use cases. Export to S3: point-in-time export of DynamoDB table to S3 (Parquet/JSON) for analytics without consuming table capacity.

---

## ⚙️ How It Works

### Table and GSI (Terraform)

```hcl
resource "aws_dynamodb_table" "orders" {
  name         = "Orders"
  billing_mode = "PAY_PER_REQUEST"  # On-Demand

  # Primary key
  hash_key  = "PK"   # partition key
  range_key = "SK"   # sort key

  attribute {
    name = "PK"
    type = "S"  # String
  }
  attribute {
    name = "SK"
    type = "S"
  }
  # Note: only index attributes declared here; other attributes are flexible
  attribute {
    name = "GSI1PK"
    type = "S"
  }
  attribute {
    name = "GSI1SK"
    type = "S"
  }

  # Global Secondary Index (alternate access pattern)
  global_secondary_index {
    name               = "GSI1"
    hash_key           = "GSI1PK"
    range_key          = "GSI1SK"
    projection_type    = "ALL"
  }

  # TTL (auto-expire items)
  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }

  # Streams (for Lambda triggers)
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }

  tags = {
    Environment = "prod"
  }
}
```

### DynamoDB Operations (Java SDK v2)

```java
@Service
public class OrderRepository {

    private final DynamoDbClient dynamoDB;
    private final String tableName = "Orders";

    // Single-table design: PK/SK patterns
    // User entity:   PK=USER#<id>, SK=METADATA
    // Order entity:  PK=USER#<userId>, SK=ORDER#<orderId>
    // GSI:           GSI1PK=ORDER#<orderId>, GSI1SK=STATUS#<status>

    // Create order
    public void createOrder(Order order) {
        Map<String, AttributeValue> item = Map.of(
            "PK",       AttributeValue.fromS("USER#" + order.getUserId()),
            "SK",       AttributeValue.fromS("ORDER#" + order.getOrderId()),
            "GSI1PK",   AttributeValue.fromS("ORDER#" + order.getOrderId()),
            "GSI1SK",   AttributeValue.fromS("STATUS#" + order.getStatus()),
            "orderId",  AttributeValue.fromS(order.getOrderId()),
            "userId",   AttributeValue.fromS(order.getUserId()),
            "status",   AttributeValue.fromS(order.getStatus()),
            "amount",   AttributeValue.fromN(order.getAmount().toString()),
            "createdAt", AttributeValue.fromS(Instant.now().toString()),
            "expiresAt", AttributeValue.fromN(  // TTL for 1 year
                String.valueOf(Instant.now().plus(365, ChronoUnit.DAYS).getEpochSecond()))
        );

        dynamoDB.putItem(PutItemRequest.builder()
            .tableName(tableName)
            .item(item)
            .conditionExpression("attribute_not_exists(PK)")  // prevent duplicate
            .build());
    }

    // Query orders for a user (efficient: uses PK)
    public List<Order> getOrdersForUser(String userId) {
        QueryResponse response = dynamoDB.query(QueryRequest.builder()
            .tableName(tableName)
            .keyConditionExpression("PK = :pk AND begins_with(SK, :skPrefix)")
            .expressionAttributeValues(Map.of(
                ":pk",       AttributeValue.fromS("USER#" + userId),
                ":skPrefix", AttributeValue.fromS("ORDER#")
            ))
            .scanIndexForward(false)  // newest first
            .limit(20)
            .build());

        return response.items().stream()
            .map(this::mapToOrder)
            .collect(Collectors.toList());
    }

    // Update order status (optimistic locking)
    public void updateOrderStatus(String userId, String orderId,
                                   String oldStatus, String newStatus) {
        dynamoDB.updateItem(UpdateItemRequest.builder()
            .tableName(tableName)
            .key(Map.of(
                "PK", AttributeValue.fromS("USER#" + userId),
                "SK", AttributeValue.fromS("ORDER#" + orderId)
            ))
            .updateExpression("SET #status = :newStatus, GSI1SK = :newGsi1sk")
            .conditionExpression("#status = :oldStatus")  // optimistic lock
            .expressionAttributeNames(Map.of("#status", "status"))
            .expressionAttributeValues(Map.of(
                ":newStatus", AttributeValue.fromS(newStatus),
                ":oldStatus", AttributeValue.fromS(oldStatus),
                ":newGsi1sk", AttributeValue.fromS("STATUS#" + newStatus)
            ))
            .build());
    }

    // Transactional write (multi-item ACID)
    public void createOrderWithInventoryDeduction(Order order, String productId) {
        dynamoDB.transactWriteItems(TransactWriteItemsRequest.builder()
            .transactItems(
                TransactWriteItem.builder().put(Put.builder()
                    .tableName(tableName)
                    .item(buildOrderItem(order))
                    .conditionExpression("attribute_not_exists(PK)")
                    .build()).build(),
                TransactWriteItem.builder().update(Update.builder()
                    .tableName(tableName)
                    .key(Map.of(
                        "PK", AttributeValue.fromS("PRODUCT#" + productId),
                        "SK", AttributeValue.fromS("INVENTORY")
                    ))
                    .updateExpression("SET quantity = quantity - :qty")
                    .conditionExpression("quantity >= :qty")
                    .expressionAttributeValues(Map.of(
                        ":qty", AttributeValue.fromN("1")
                    ))
                    .build()).build()
            ).build());
    }
}
```

---

## ⚖️ Comparison Table: DynamoDB vs RDS

|                       | DynamoDB                                 | RDS/Aurora                    |
| --------------------- | ---------------------------------------- | ----------------------------- |
| **Model**             | Key-value / Document                     | Relational (SQL)              |
| **Scale**             | Horizontal (auto)                        | Vertical + read replicas      |
| **Latency**           | Single-digit ms                          | ~1ms (local), varies          |
| **JOINs**             | ❌ (single-table design)                 | ✅                            |
| **Transactions**      | ✅ (limited, same region)                | ✅ (full ACID)                |
| **Schema**            | Flexible per item                        | Fixed schema                  |
| **Query flexibility** | Access patterns must be designed upfront | Ad-hoc SQL queries            |
| **Cost at scale**     | Competitive                              | Expensive at very large scale |
| **Use case**          | High-scale, known access patterns        | Complex queries, reporting    |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                             |
| ------------------------------------- | --------------------------------------------------------------------------------------------------- |
| "DynamoDB is just a key-value store"  | Supports complex queries via sort key (range queries, begins_with, between) and GSIs                |
| "I can add GSIs later easily"         | You can add GSIs later, but you need to design access patterns upfront; retrofitting is painful     |
| "On-Demand is always cheaper"         | Provisioned + Auto Scaling is 60-70% cheaper at steady high throughput; On-Demand for spiky/unknown |
| "Scan is acceptable for small tables" | Scan consumes full table RCUs; even small tables should use Query with indexes                      |

---

## 🔗 Related Keywords

- [RDS](/cloud-aws/rds/) - relational SQL alternative
- [ElastiCache](/cloud-aws/elasticache/) - caching in front of DynamoDB for hot reads
- [Kinesis](/cloud-aws/kinesis/) - DynamoDB Streams can feed Kinesis

---

## 📌 Quick Reference Card

```bash
# Create table
aws dynamodb create-table \
  --table-name Orders \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Put item
aws dynamodb put-item \
  --table-name Orders \
  --item '{"PK":{"S":"USER#123"},"SK":{"S":"ORDER#456"},"status":{"S":"PENDING"}}'

# Query by PK
aws dynamodb query \
  --table-name Orders \
  --key-condition-expression "PK = :pk AND begins_with(SK, :prefix)" \
  --expression-attribute-values '{":pk":{"S":"USER#123"},":prefix":{"S":"ORDER#"}}'

# Get table metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=Orders \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 300 --statistics Sum
```

---

## 🧠 Think About This

The most important DynamoDB lesson is that access patterns must be designed before schema. With SQL, you design normalized tables and write queries later. With DynamoDB, you invert this: list ALL the ways your application needs to access data, then design PK/SK/GSI patterns to support every access pattern with O(log n) queries. If you miss an access pattern, adding it later (new GSI) works but is painful and may require backfilling. NoSQL Workbench for DynamoDB (free AWS tool) visualizes single-table designs and simulates access patterns before you write any code - use it for every new DynamoDB table. The "Hot Partition" anti-pattern kills DynamoDB performance: if your PK has low cardinality (e.g., PK=status values like "PENDING/COMPLETE"), all writes go to 2 partitions. Distribute writes by using high-cardinality PKs (user IDs, UUIDs, timestamps with random suffix).
