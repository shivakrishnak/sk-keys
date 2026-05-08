---
layout: default
title: "ElastiCache"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /cloud-aws/elasticache/
id: AWS-048
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on: ["VPC", "RDS", "DynamoDB"]
used_by: ["AWS Cost Optimization"]
related: ["RDS", "DynamoDB", "Aurora", "AWS Cost Optimization"]
tags: [aws, elasticache, redis, memcached, caching, database, cloud]
---

# ElastiCache

## ⚡ TL;DR

**ElastiCache** is managed **Redis** or **Memcached** in AWS. Redis: rich data structures, persistence, clustering, pub/sub, sorted sets - general purpose. Memcached: simple key-value, multi-threaded, no persistence - pure cache. Primary use cases: application caching, session storage, rate limiting, leaderboards, real-time analytics. Reduces database load by 80%+ for read-heavy workloads.

---

## 🔥 Problem This Solves

Database is the bottleneck: 10,000 requests/sec all hitting RDS for the same product catalog data. Solution: cache hot data in Redis (sub-millisecond reads, handles 1M+ requests/sec). DB goes from 10K queries/sec to a few hundred cache misses. Response time: 200ms → 5ms.

---

## 📘 Textbook Definition

Amazon ElastiCache is a managed in-memory caching service supporting Redis and Memcached engines. It provides sub-millisecond latency for read-heavy workloads and frees relational databases from repetitive queries. ElastiCache for Redis also supports data persistence, replication, cluster mode, and advanced data structures.

---

## ⏱️ 30 Seconds

```
Redis (ElastiCache for Redis / Valkey):
  Data types: String, Hash, List, Set, Sorted Set, Stream, Bitmap, HyperLogLog
  Persistence: RDB snapshots, AOF logs
  Replication: 1 primary + up to 5 replicas per shard
  Cluster mode: horizontally shard keys across 1-500 shards
  Use: caching, sessions, rate limiting, leaderboards, pub/sub

Memcached:
  Data types: String key-value only
  No persistence, no replication
  Multi-threaded; simple
  Use: simple caching where Redis features not needed

ElastiCache Serverless:
  Auto-scales cache capacity; no cluster sizing
  From KB to 100+ TB; pay per data stored + ECUs
```

---

## 🔩 First Principles

- **Cache-aside**: app checks cache first; on miss, fetch from DB, write to cache, return result
- **Write-through**: app writes to cache AND DB simultaneously (cache never stale, but doubles writes)
- **Cache invalidation**: hardest problem; stale reads vs cache miss tradeoff
- **TTL (Time To Live)**: automatic expiration of cache entries; prevents stale data accumulation
- **Redis replication**: async; primary handles writes; replicas serve reads; failover promotes replica
- **Eviction policies**: `allkeys-lru` (evict least recently used when memory full) is most common

---

## 🧪 Thought Experiment

Product catalog API: 100 products, each requested ~1000x/min. Without cache: 100,000 DB queries/min. With cache-aside (TTL=5min): first 100 requests miss (100 DB queries), then 99,900 requests hit cache. DB load: 100 queries/5min = 20/min (99.98% cache hit rate). DB cost: effectively zero for catalog reads.

---

## 🧠 Mental Model / Analogy

ElastiCache/Redis is a **waiter's notepad**: instead of walking to the kitchen (DB) for every order, the waiter writes down recent orders (cache). When the same order comes again, the waiter reads from the notepad (sub-ms). If the notepad doesn't have it (miss), walk to the kitchen (DB) and write it down. The notepad has limited space, so old entries get erased (eviction/TTL).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Add Redis layer in front of RDS. Cache-aside in application: check Redis first, on miss query DB, write to Redis with TTL. Use for session storage, API response caching.

**Level 2 - Practitioner**: Redis data structures: sorted sets for leaderboards (`ZADD`, `ZRANGE`), sets for unique counters, lists for queues. Rate limiting: `INCR`+`EXPIRE` for sliding window counters. Connection pooling: avoid creating connection per request; use Lettuce (Spring Boot default) with connection pool.

**Level 3 - Advanced**: Redis Cluster Mode: shard keys across multiple shards for throughput/memory beyond single node. Redis Streams: append-only log for event processing (DynamoDB Streams alternative). Pub/Sub: real-time event broadcasting to subscribers. Redis replication lag: monitor `ReplicationLag` metric; async replication means replica may be slightly behind.

**Level 4 - Expert**: Redis Lua scripting: atomic multi-command operations (avoid race conditions without transactions). Redis MULTI/EXEC transactions: optimistic transactions with WATCH for compare-and-set. Distributed locks with Redlock algorithm. Cache warming strategies: pre-populate cache on startup to prevent cold-start thundering herd. Data size tuning: Redis serialization overhead (use MessagePack instead of JSON; 30-50% smaller). Memory optimization: use Redis Hash for objects >5 fields (internal ziplist encoding saves memory). ElastiCache Global Datastore: cross-region replication for globally distributed apps.

---

## ⚙️ How It Works

### ElastiCache Redis (Terraform)

```hcl
# Redis replication group (1 primary + 2 replicas)
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "main-redis"
  description                = "Main application cache"

  # Engine
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = "cache.r7g.large"

  # Replication
  num_cache_clusters   = 3    # 1 primary + 2 replicas
  automatic_failover_enabled = true
  multi_az_enabled     = true

  # Network
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  # Encryption
  at_rest_encryption_enabled  = true
  transit_encryption_enabled  = true
  auth_token                  = var.redis_auth_token  # from Secrets Manager

  # Persistence (optional, for recovery)
  snapshot_retention_limit = 1
  snapshot_window          = "03:00-04:00"

  # Maintenance
  maintenance_window = "sun:05:00-sun:06:00"

  # Parameters
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  tags = {
    Environment = "prod"
  }
}

resource "aws_elasticache_parameter_group" "redis" {
  family = "redis7"
  name   = "custom-redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"  # evict LRU when memory full
  }
  parameter {
    name  = "activedefrag"
    value = "yes"          # defragment memory online
  }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "redis-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}
```

### Spring Boot Redis Integration

```yaml
# application.yml
spring:
  data:
    redis:
      host: ${REDIS_PRIMARY_ENDPOINT}
      port: 6379
      password: ${REDIS_AUTH_TOKEN}
      ssl:
        enabled: true
      lettuce:
        pool:
          max-active: 20
          max-idle: 10
          min-idle: 5

  cache:
    type: redis
    redis:
      time-to-live: 300000 # 5 minutes default TTL
      use-key-prefix: true
```

```java
// Cache-aside with Spring Cache abstraction
@Service
public class ProductService {

    private final ProductRepository productRepository;
    private final RedisTemplate<String, Object> redisTemplate;

    // Automatic cache-aside with @Cacheable
    @Cacheable(value = "products", key = "#productId", unless = "#result == null")
    public Product getProduct(String productId) {
        // Only called on cache miss
        return productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));
    }

    // Evict on update
    @CacheEvict(value = "products", key = "#product.productId")
    @Transactional
    public Product updateProduct(Product product) {
        return productRepository.save(product);
    }

    // Manual cache operations for complex patterns
    public void cacheRateLimitCounter(String userId, String action) {
        String key = "rate:" + userId + ":" + action;
        ValueOperations<String, Object> ops = redisTemplate.opsForValue();

        Long count = ops.increment(key);
        if (count == 1) {
            // First increment: set expiry (sliding window: 1 minute)
            redisTemplate.expire(key, Duration.ofMinutes(1));
        }

        if (count > 100) {  // 100 actions per minute
            throw new RateLimitExceededException("Rate limit exceeded for " + userId);
        }
    }

    // Sorted set for leaderboard
    public void recordScore(String gameId, String userId, double score) {
        redisTemplate.opsForZSet().add("leaderboard:" + gameId, userId, score);
    }

    public List<String> getTopPlayers(String gameId, int count) {
        return redisTemplate.opsForZSet()
            .reverseRange("leaderboard:" + gameId, 0, count - 1)
            .stream()
            .map(Object::toString)
            .collect(Collectors.toList());
    }
}
```

---

## ⚖️ Comparison Table: Redis vs Memcached

|                    | Redis                                        | Memcached                     |
| ------------------ | -------------------------------------------- | ----------------------------- |
| **Data types**     | Rich (String, Hash, List, Set, ZSet, Stream) | String only                   |
| **Persistence**    | ✅ (RDB + AOF)                               | ❌                            |
| **Replication**    | ✅                                           | ❌                            |
| **Cluster**        | ✅ (sharding)                                | ✅ (client-side)              |
| **Pub/Sub**        | ✅                                           | ❌                            |
| **Transactions**   | ✅ (MULTI/EXEC)                              | ❌                            |
| **Multi-threaded** | Single-threaded (Redis 7: partially multi)   | Multi-threaded                |
| **Use case**       | Most use cases                               | Simple caching, extreme scale |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| "Cache removes consistency concerns"    | Stale reads are real; design cache invalidation explicitly, not as afterthought                          |
| "More cache = always faster"            | Cache misses are expensive (DB query + cache write); too-low TTL increases misses                        |
| "Redis is single-threaded = slow"       | Redis single-threaded model handles 1M+ ops/sec; single-threaded avoids locking overhead                 |
| "ElastiCache Multi-AZ = zero data loss" | Async replication; failover may lose latest writes (seconds of data); for critical data, use persistence |

---

## 🔗 Related Keywords

- [RDS](/cloud-aws/rds/) - database layer behind ElastiCache
- [DynamoDB](/cloud-aws/dynamodb/) - NoSQL DB with built-in DAX caching option

---

## 📌 Quick Reference Card

```bash
# List ElastiCache clusters
aws elasticache describe-replication-groups \
  --query 'ReplicationGroups[].{Id:ReplicationGroupId,Status:Status,Nodes:NodeGroups[0].NodeGroupMembers[*].ReadEndpoint.Address}'

# Get primary endpoint
aws elasticache describe-replication-groups \
  --replication-group-id my-redis \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint'

# Check cache hit metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CacheHits \
  --dimensions Name=CacheClusterId,Value=my-redis-0001-001 \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 300 --statistics Sum

# Connect to Redis (via SSH tunnel or within VPC)
redis-cli -h <primary-endpoint> -p 6379 -a <auth-token> --tls

# Basic Redis commands
redis-cli> PING
redis-cli> SET key value EX 300  # set with 5min TTL
redis-cli> GET key
redis-cli> INFO memory           # memory usage stats
redis-cli> INFO stats            # hit/miss stats
```

---

## 🧠 Think About This

The thundering herd problem is the most dangerous ElastiCache failure mode. When a Redis node fails (or you clear the cache), all application instances simultaneously try to fetch the same hot data from the DB. At peak traffic: 1000 concurrent requests all miss the cache, all fire DB queries simultaneously, DB gets overwhelmed, entire system slows down. Mitigations: (1) **Cache warming**: pre-populate the cache before routing traffic to a new node. (2) **Mutex/lock on cache miss**: only one thread queries the DB for a given key; others wait. (3) **Stale-while-revalidate**: serve stale data and refresh asynchronously - never serve a miss. (4) **Jitter in TTLs**: instead of all keys expiring at the same time (cache stampede), add random jitter: `TTL = baseTTL + Random(0, baseTTL * 0.1)`. These patterns protect your database from the cascade failure that follows a cache outage.
