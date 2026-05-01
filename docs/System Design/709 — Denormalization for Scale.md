---
layout: default
title: "Denormalization for Scale"
parent: "System Design"
nav_order: 709
permalink: /system-design/denormalization-for-scale/
number: "709"
category: System Design
difficulty: ★★★
depends_on: "Read-Heavy vs Write-Heavy Design, Caching, Database Normalization"
used_by: "Fan-Out on Write vs Read, CQRS"
tags: #advanced, #database, #architecture, #performance, #scalability
---

# 709 — Denormalization for Scale

`#advanced` `#database` `#architecture` `#performance` `#scalability`

⚡ TL;DR — **Denormalization for Scale** is the deliberate introduction of redundant data into a database schema to eliminate expensive JOINs, reduce read latency, and increase read throughput — trading write complexity and storage for read performance.

| #709 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Read-Heavy vs Write-Heavy Design, Caching, Database Normalization | |
| **Used by:** | Fan-Out on Write vs Read, CQRS | |

---

### 📘 Textbook Definition

**Denormalization** is the process of restructuring a database schema to include redundant copies of data (or pre-computed derivations of data) in order to reduce the computational cost of read queries. While normalisation (1NF, 2NF, 3NF) eliminates redundancy to minimise storage and update anomalies, denormalisation deliberately introduces controlled redundancy to enable single-table or single-document reads instead of multi-table JOINs. In distributed systems and NoSQL databases, JOINs across shards are prohibitively expensive or impossible — denormalisation is therefore not optional but architecturally required. Techniques include: flattening related entity attributes into a single table row, embedding nested documents (MongoDB), materialised views (pre-computed aggregations), and duplicate columns across tables for query locality. The trade-off: writes become more complex (must update all copies of redundant data) and storage increases.

---

### 🟢 Simple Definition (Easy)

Denormalization: copy data that you need together into one place, so you don't need to look it up elsewhere. Instead of storing "user_id=5" and looking up the username separately, store "username=Alice" right next to the data. One trip to the database instead of three. Trade: if Alice changes her name, you need to update three places instead of one.

---

### 🔵 Simple Definition (Elaborated)

Normalised schema: `orders` table has `customer_id`, `product_id`. To display an order: JOIN to `customers` (get name, email), JOIN to `products` (get name, price, image), JOIN to `categories` (get category name) = 3 joins per order. At 100,000 orders/second: 300,000 join operations/second. Denormalised: `orders` table has all fields inline: `customer_name`, `customer_email`, `product_name`, `product_price`, `category_name`. 0 joins per order read. 100,000 reads/second = 100,000 simple index scans. Trade: when a product price changes, update it in both `products` AND in all historical `orders` rows. But for an order history (which is immutable), this is perfect — orders capture the price at time of purchase anyway.

---

### 🔩 First Principles Explanation

**Denormalization techniques and when to apply each:**

```
TECHNIQUE 1: COLUMN DUPLICATION (flatten foreign key references)

  NORMALISED (3 JOINs, slow reads):
  
  orders: | order_id | customer_id | product_id | quantity |
  customers: | customer_id | name | email | tier |
  products: | product_id | name | price | category_id |
  categories: | category_id | name |
  
  Query: "Show order #123 with customer and product details"
  SELECT o.*, c.name, c.email, p.name, p.price, cat.name
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN products p ON o.product_id = p.product_id
  JOIN categories cat ON p.category_id = cat.category_id
  WHERE o.order_id = 123;
  
  DENORMALISED (0 JOINs, fast reads):
  
  orders: | order_id | customer_id | customer_name | customer_email | 
          | product_id | product_name | product_price | category_name |
          | quantity | created_at |
  
  Query:
  SELECT * FROM orders WHERE order_id = 123;
  
  WHEN TO USE:
    - Orders: immutable after creation (price at purchase time is historically correct)
    - Read:Write ratio > 100:1 (reading orders >> writing orders)
    - Distributed DB (shards: JOINs across shards are impossible)
  
  WHEN NOT TO USE:
    - Mutable data with frequent updates (customer name change → update all orders)
    - Write-heavy systems where read optimisation isn't the bottleneck

TECHNIQUE 2: EMBEDDED DOCUMENTS (NoSQL / MongoDB)

  NORMALISED (separate collections, aggregation pipeline required):
  
  users: { user_id: 1, name: "Alice", address_id: 5 }
  addresses: { address_id: 5, street: "123 Main St", city: "NYC" }
  
  DENORMALISED (embedded document — 1 document read):
  
  users: {
    user_id: 1,
    name: "Alice",
    address: {          ← embedded, no separate lookup
      street: "123 Main St",
      city: "NYC"
    }
  }
  
  RULES FOR EMBEDDING vs REFERENCING (MongoDB data modelling):
    EMBED when:
    - "Has one" or "owned by" relationship (user has one address)
    - Child data is always read with parent (never standalone)
    - Child data rarely changes
    - Small child document size
    
    REFERENCE when:
    - "Many-to-many" relationship (products ↔ categories)
    - Child data accessed standalone frequently
    - Child data changes often (would require updating all parent docs)
    - Child document is large (> 1/3 of parent document)

TECHNIQUE 3: MATERIALISED VIEWS (pre-computed aggregations)

  EXPENSIVE QUERY (calculated on every request):
  SELECT product_id, SUM(quantity) as total_sold, AVG(price) as avg_price
  FROM order_items
  GROUP BY product_id
  ORDER BY total_sold DESC
  LIMIT 10;
  -- Full table scan on 100M rows: 10,000ms
  
  MATERIALISED VIEW (pre-computed, refreshed periodically):
  
  CREATE MATERIALIZED VIEW product_sales_summary AS
  SELECT product_id, SUM(quantity) as total_sold, AVG(price) as avg_price
  FROM order_items
  GROUP BY product_id;
  
  -- Index the materialised view:
  CREATE INDEX ON product_sales_summary(total_sold DESC);
  
  -- Query materialised view: fast index scan
  SELECT * FROM product_sales_summary ORDER BY total_sold DESC LIMIT 10;
  -- < 10ms (index scan on pre-computed table of ~10K product rows)
  
  -- Refresh (PostgreSQL CONCURRENTLY: no lock on reads during refresh):
  REFRESH MATERIALIZED VIEW CONCURRENTLY product_sales_summary;
  -- Schedule: every 5 minutes via pg_cron or application scheduler
  
  TRADE-OFF:
    - Data is stale (up to 5 minutes behind)
    - Refresh adds write load to DB
    - Acceptable for: dashboards, leaderboards, reports
    - Not acceptable for: real-time financial balances, inventory

TECHNIQUE 4: COUNTER CACHING (pre-computed counts)

  NORMALISED (count query, slow at scale):
  SELECT COUNT(*) FROM followers WHERE followed_user_id = ?;
  -- 100K followers: full index scan, 500ms → not feasible at Twitter scale
  
  DENORMALISED (stored counter):
  users: | user_id | username | follower_count | following_count |
  
  -- When a new follow happens:
  UPDATE users SET follower_count = follower_count + 1 WHERE user_id = followed_id;
  INSERT INTO followers (follower_id, followed_id) VALUES (?, ?);
  
  -- Read follower count:
  SELECT follower_count FROM users WHERE user_id = ?;
  -- 1ms single index lookup — no COUNT(*) scan
  
  TRADE-OFF:
    - Counter can diverge from actual row count if write fails partially
    - Use transactions or eventual consistency sync to reconcile
    - Periodic reconciliation: run COUNT(*) nightly, fix discrepancies

DECIDING WHEN TO DENORMALISE:

  SIGNALS to denormalise:
  ✓ Query has 3+ JOINs on hot read path
  ✓ Read:Write ratio > 10:1 on denormalised data
  ✓ Sharded DB (cross-shard JOINs impossible)
  ✓ NoSQL database (no JOIN support)
  ✓ Read latency p99 > SLA despite indexes and caching
  
  SIGNALS to STAY normalised:
  ✗ Data changes frequently (UPDATE storms on denormalised columns)
  ✗ Complex many-to-many relationships (denormalised copies explode)
  ✗ ACID transactions required across denormalised copies
  ✗ Write throughput is the bottleneck (not read throughput)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Denormalization:
- 3+ JOINs per read: multiplicative latency, CPU overhead
- Sharded DB: JOINs across shards require scatter-gather (slow, complex)
- COUNT(*) on large tables: full scans on every read

WITH Denormalization:
→ Single-row reads: no JOINs, sub-millisecond response
→ Sharding enabled: all data needed for a query lives on the same shard
→ Pre-computed values: counter/aggregation reads are O(1) not O(N)

---

### 🧠 Mental Model / Analogy

> A reference book with an extensive index vs. a summarised cheat sheet. The reference book (normalised) is perfectly organised — no duplication, every fact in exactly one place. The cheat sheet (denormalised) duplicates key facts for quick access — "For X, use Y" without looking up chapter 3, section 4. The cheat sheet is faster to use but if a fact changes, you must update both the reference book AND the cheat sheet. Choose based on: how often you read vs. how often facts change.

"Reference book (normalised)" = normalised database (one source of truth, JOINs needed)
"Cheat sheet (denormalised)" = denormalised schema (redundant data, no JOINs)
"Duplicating key facts for quick access" = embedding foreign key attributes inline
"Update both book and cheat sheet when fact changes" = write complexity of denormalisation
"Choose by read vs. change frequency" = denormalise when reads >> updates to that data

---

### ⚙️ How It Works (Mechanism)

**Cassandra: denormalized table design for query-driven modelling:**

```sql
-- RELATIONAL NORMALISED (doesn't work well in Cassandra):
-- Cannot do: JOIN followers f ON u.user_id = f.followed_user_id
-- Cassandra has no JOINs across partitions

-- DENORMALISED: design tables around query patterns

-- Query 1: "Get all tweets by user X" → table optimised for this query:
CREATE TABLE tweets_by_user (
  user_id    UUID,
  tweet_id   TIMEUUID,          -- time-based UUID for natural time ordering
  content    TEXT,
  created_at TIMESTAMP,
  like_count INT,
  -- Denormalized user data (avoids cross-partition lookup):
  username   TEXT,
  user_avatar_url TEXT,
  PRIMARY KEY (user_id, tweet_id)  -- partition by user_id, cluster by tweet_id
) WITH CLUSTERING ORDER BY (tweet_id DESC);  -- newest first

-- Query 2: "Get all tweets liked by user X" → separate denormalized table:
CREATE TABLE liked_tweets_by_user (
  user_id    UUID,
  liked_at   TIMESTAMP,
  tweet_id   UUID,
  -- Denormalized tweet data (avoids separate partition lookup):
  tweet_content TEXT,
  tweet_author_id UUID,
  tweet_author_name TEXT,
  PRIMARY KEY (user_id, liked_at, tweet_id)
) WITH CLUSTERING ORDER BY (liked_at DESC);

-- RESULT:
-- Reads for "get user's timeline": single partition scan (fast)
-- Writes: must write to both tables when tweet created/liked
-- Trade-off: 2× write volume for 10× read speed
-- Correct for: Twitter-scale where reads >> writes
```

---

### 🔄 How It Connects (Mini-Map)

```
Database Normalization (starting point: no redundancy)
        │ (read latency grows with JOINs at scale)
        ▼
Denormalization for Scale ◄──── (you are here)
(controlled redundancy for read performance)
        │
        ├── Materialised Views (aggregation denormalization)
        ├── Fan-Out on Write vs Read (timeline/feed denormalization)
        └── CQRS (separate read model = aggressively denormalized)
```

---

### 💻 Code Example

**Spring Boot + JPA: writing denormalized data on parent create:**

```java
@Service
@Transactional
public class OrderService {
    
    @Autowired private OrderRepository orderRepository;
    @Autowired private CustomerRepository customerRepository;
    @Autowired private ProductRepository productRepository;
    
    public Order createOrder(Long customerId, Long productId, int quantity) {
        // Fetch normalised source data:
        Customer customer = customerRepository.findById(customerId).orElseThrow();
        Product product = productRepository.findById(productId).orElseThrow();
        
        // Denormalize at write time — embed needed data in order row:
        Order order = new Order();
        order.setCustomerId(customerId);
        order.setProductId(productId);
        order.setQuantity(quantity);
        
        // Denormalized fields — copied at order creation time:
        order.setCustomerName(customer.getName());          // denormalized
        order.setCustomerEmail(customer.getEmail());        // denormalized
        order.setProductName(product.getName());            // denormalized
        order.setProductPriceCents(product.getPriceCents());// denormalized (immutable: price at purchase)
        order.setCategoryName(product.getCategory().getName()); // denormalized
        
        return orderRepository.save(order);
        
        // Result: Order row is self-contained.
        // Reads: SELECT * FROM orders WHERE order_id = ? → 0 JOINs.
        // If product name changes: historical orders correctly show OLD name (desired for order history).
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Denormalization means abandoning data integrity | Denormalization introduces redundancy but integrity is maintained through application-layer writes (update all copies on change). The trade-off is that the database can no longer enforce single-source-of-truth integrity — the application must ensure consistency. This is acceptable when the denormalized data is write-rarely, read-often |
| Denormalization is only for NoSQL databases | Relational databases benefit equally from denormalization for read-heavy workloads. PostgreSQL materialised views, counter cache columns, and flattened read tables are all forms of relational denormalization. PostgreSQL, MySQL, and Oracle all support materialised views natively |
| More JOINs always means you need to denormalise | JOINs on small tables with good indexes are fast. A JOIN on a 1,000-row countries table is trivially fast even at high read rates (fits in buffer pool). Denormalise only JOINs to large tables or tables with frequently changing index patterns. Profile before denormalizing |
| Denormalization permanently locks the schema | Denormalization can be applied incrementally: start normalised, add denormalized columns when profiling shows JOINs are bottlenecks. Rolling schema changes with background backfills allow gradual denormalization without system rewrites |

---

### 🔥 Pitfalls in Production

**Counter cache out-of-sync with actual data:**

```
PROBLEM: Denormalized counter diverges from reality

  users table: follower_count column (denormalized counter)
  followers table: actual follow relationships
  
  Expected invariant: follower_count = COUNT(*) FROM followers WHERE followed_user_id = user_id
  
  BUG: Transaction fails after INSERT into followers but before UPDATE to follower_count:
  
  BEGIN;
    INSERT INTO followers (follower_id, followed_user_id) VALUES (100, 200);
    -- Application crashes here (network timeout, OOM, etc.)
    UPDATE users SET follower_count = follower_count + 1 WHERE user_id = 200;
    -- Never executed!
  COMMIT;
  
  Result: 
    followers table: shows user 100 follows user 200 ✓
    users.follower_count for user 200: N (not N+1) ✗
    Counter is now permanently off by 1.
    
FIX 1: ATOMIC TRANSACTION (ensure both updates succeed or both fail)

  @Transactional
  public void followUser(Long followerId, Long followedId) {
    followRepository.save(new Follow(followerId, followedId));
    userRepository.incrementFollowerCount(followedId);  // in same transaction
    // Both succeed or both rollback — no divergence
  }

FIX 2: PERIODIC RECONCILIATION (catch historical divergence)

  // Nightly job: reconcile counters
  @Scheduled(cron = "0 2 * * *")  // 2 AM daily
  public void reconcileFollowerCounts() {
    List<Long> divergedUsers = jdbcTemplate.queryForList(
      "SELECT u.user_id FROM users u " +
      "JOIN (SELECT followed_user_id, COUNT(*) as actual_count FROM followers GROUP BY 1) f " +
      "ON u.user_id = f.followed_user_id " +
      "WHERE u.follower_count != f.actual_count",
      Long.class
    );
    
    for (Long userId : divergedUsers) {
      jdbcTemplate.update(
        "UPDATE users SET follower_count = " +
        "(SELECT COUNT(*) FROM followers WHERE followed_user_id = ?) " +
        "WHERE user_id = ?",
        userId, userId
      );
    }
    log.info("Reconciled {} diverged follower counts", divergedUsers.size());
  }
```

---

### 🔗 Related Keywords

- `Read-Heavy vs Write-Heavy Design` — denormalization is the primary data model strategy for read-heavy systems
- `Fan-Out on Write vs Read` — social feed systems use denormalization to pre-compute timelines
- `CQRS` — read model in CQRS is always denormalized for query performance
- `Materialised Views` — database-native form of denormalization for aggregations
- `NoSQL` — document and wide-column databases (MongoDB, Cassandra) require denormalization by design

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Redundant data embedded at write time     │
│              │ eliminates JOINs on the read path         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 3+ JOINs on hot read path; sharded DB;    │
│              │ read:write ratio > 10:1                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Frequently updated denormalized fields;   │
│              │ write-heavy workloads; ACID required      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cheat sheet: duplicate facts for speed,  │
│              │  but update all copies when facts change."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fan-Out on Write vs Read → CQRS           │
│              │ → Materialised Views                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A social network stores user profiles (name, bio, avatar URL) normalised in a `users` table. Posts are in a `posts` table with `user_id` foreign key. The "post feed" query displays: post content + author name + author avatar. Feed is read 10M times/day; user profiles are updated by ~1% of users per day. Should the `posts` table denormalize `author_name` and `author_avatar_url`? What is the write overhead of denormalization? What happens when a user changes their avatar — how do you handle the 10M existing posts that have the old avatar URL denormalized?

**Q2.** You're designing a Cassandra data model for an e-commerce system. Customers query: (a) "all orders by customer X" and (b) "all orders for product Y". Cassandra requires denormalization for each query pattern. Design two separate tables to support these queries, showing all columns in each table. What is the storage overhead compared to a single normalised `orders` table? What must the write path do to ensure both tables are consistent? What happens if a partial write fails (INSERT to table 1 succeeds, INSERT to table 2 fails)?
