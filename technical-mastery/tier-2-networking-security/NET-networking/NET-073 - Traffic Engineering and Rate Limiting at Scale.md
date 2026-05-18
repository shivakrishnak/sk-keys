---
id: NET-073
title: "Traffic Engineering and Rate Limiting at Scale"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-034, NET-062
used_by: NET-075
related: NET-034, NET-062, NET-075
tags:
  - networking
  - traffic-engineering
  - rate-limiting
  - load-balancing
  - congestion
  - qos
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/net/traffic-engineering-and-rate-limiting-at-scale/
---

**⚡ TL;DR** - Traffic engineering controls HOW traffic flows
through a network. Rate limiting controls HOW MUCH traffic
a service accepts. Both are essential for availability at
scale: without traffic engineering, one bad actor or traffic
spike takes down the whole system. Core patterns:
token bucket and leaky bucket algorithms, distributed rate
limiting (Redis-based), global vs local rate limits, and
adaptive load shedding. The hard production problem:
rate limits that work in single-server mode silently fail
when distributed across 10 nodes.

| #073 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | Load Balancing Algorithms (NET-034), Service Mesh - Istio (NET-062) | |
| **Used by:** | Build a Secure Network Platform (NET-075) | |
| **Related:** | Load Balancing Algorithms, Service Mesh, Build a Secure Network Platform | |

---

### 🧠 Intuition: Token Bucket vs Leaky Bucket

```
Token bucket:
  Bucket holds N tokens
  Each token: allows one request
  New tokens: added at rate R tokens/second
  Request arrives: consume 1 token (allow) or reject (bucket empty)
  
  Example: N=100, R=100/sec
  Burst: up to 100 requests instantly (drains bucket)
  Sustained: exactly 100 req/sec
  
  Behavior: allows SHORT bursts above sustained rate
  Use: API rate limiting (allow brief bursts, limit sustained)

Leaky bucket:
  Requests enter queue, process at constant rate R
  Queue full: requests dropped
  
  Behavior: output is always constant rate R
  Use: network traffic shaping (smooth transmission rate)
  
  Difference:
  Token bucket: bursty input allowed, bursty output possible
  Leaky bucket: bursty input smoothed to constant output rate
```

---

### ⚙️ Single-Node Rate Limiting

```python
# Redis-based token bucket rate limiter (thread-safe)
import redis
import time

r = redis.Redis(host='redis', port=6379, decode_responses=True)

RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local fill_rate = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

-- Get current tokens and last refill time
local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

-- Calculate new tokens based on elapsed time
local elapsed = now - last_refill
local new_tokens = math.min(capacity, tokens + elapsed * fill_rate)

-- Can we serve this request?
if new_tokens >= requested then
    -- Update state
    redis.call('HMSET', key, 
        'tokens', new_tokens - requested,
        'last_refill', now)
    redis.call('EXPIRE', key, 60)
    return 1  -- allowed
else
    redis.call('HMSET', key,
        'tokens', new_tokens,
        'last_refill', now)
    redis.call('EXPIRE', key, 60)
    return 0  -- rate limited
end
"""

lua_script = r.register_script(RATE_LIMIT_SCRIPT)

def is_allowed(user_id: str, capacity: int = 100,
               fill_rate: float = 10.0) -> bool:
    """
    capacity: max tokens (burst limit)
    fill_rate: tokens per second (sustained rate)
    Returns: True if request allowed, False if rate limited
    """
    now = time.time()
    result = lua_script(
        keys=[f"ratelimit:{user_id}"],
        args=[now, capacity, fill_rate, 1]
    )
    return bool(result)

# Usage:
if not is_allowed("user:123"):
    return 429, {"error": "rate limit exceeded",
                 "retry_after": "1s"}
```

---

### ⚙️ Distributed Rate Limiting: The Hard Problem

```
Problem: single rate limit across N nodes
  10 instances each with local limit of 100 req/min
  User sees: 1,000 req/min effective limit
  (each instance allows 100, user round-robins across 10)
  
Naive fix: share state in Redis
  Works, but adds ~1ms RTT per request (Redis lookup)
  At 10,000 RPS: Redis becomes bottleneck
  
Better approach: approximate distributed rate limiting
  Each instance: local counter + periodic sync to Redis
  Local: allow up to limit/N requests per sync window
  Sync: every 100ms, push local count, pull global count
  
  Trade-off: can allow up to 2x the limit during sync window
  Acceptable for most use cases (burst allowance)
```

```python
# Approximate distributed rate limit (reduced Redis calls)
import threading
import time

class DistributedRateLimiter:
    def __init__(self, redis_client, limit: int,
                 window_sec: int, sync_interval_ms: int = 100):
        self.redis = redis_client
        self.limit = limit
        self.window = window_sec
        self.sync_interval = sync_interval_ms / 1000.0
        
        self.local_count = 0
        self.last_sync = time.time()
        self.global_count = 0
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        with self.lock:
            now = time.time()
            
            # Sync with Redis if interval elapsed
            if now - self.last_sync > self.sync_interval:
                pipeline = self.redis.pipeline()
                pipeline.incrby(f"global:{key}", self.local_count)
                pipeline.expire(f"global:{key}", self.window)
                pipeline.get(f"global:{key}")
                results = pipeline.execute()
                self.global_count = int(results[2] or 0)
                self.local_count = 0
                self.last_sync = now
            
            # Allow if within limit
            if self.global_count + self.local_count < self.limit:
                self.local_count += 1
                return True
            return False
```

---

### ⚙️ Envoy Rate Limiting (Service Mesh)

```yaml
# Global rate limit via Envoy + Ratelimit service
# Envoy calls gRPC ratelimit service before forwarding
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: filter-ratelimit
  namespace: payment
spec:
  workloadSelector:
    labels:
      app: payment-api
  configPatches:
    - applyTo: HTTP_FILTER
      match:
        context: SIDECAR_INBOUND
        listener:
          filterChain:
            filter:
              name: "envoy.filters.network.http_connection_manager"
      patch:
        operation: INSERT_BEFORE
        value:
          name: envoy.filters.http.ratelimit
          typed_config:
            "@type": type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
            domain: payment-api
            failure_mode_deny: false  # open on ratelimit service failure
            rate_limit_service:
              grpc_service:
                envoy_grpc:
                  cluster_name: outbound|8081||ratelimit.istio-system.svc.cluster.local
              transport_api_version: V3
```

```yaml
# Rate limit service configuration
# Defines the actual limits:
domain: payment-api
descriptors:
  - key: user_id
    rate_limit:
      unit: MINUTE
      requests_per_unit: 100
  - key: user_id
    value: premium
    rate_limit:
      unit: MINUTE
      requests_per_unit: 1000  # premium users: 10x limit
  - key: remote_address
    rate_limit:
      unit: SECOND
      requests_per_unit: 10   # per-IP limit
```

---

### ⚙️ Load Shedding vs Rate Limiting

```
Rate limiting: reject based on IDENTITY (user, IP, API key)
  "This user has exceeded their quota"
  Fairness: quota applies equally
  
Load shedding: reject based on SYSTEM HEALTH
  "The system is at capacity, drop low-priority work"
  Not about quotas - about keeping system alive
  
Adaptive load shedding (Google SRE pattern):
  When CPU > 80% or latency P99 > threshold:
    Start rejecting requests randomly
    Probability of rejection: proportional to overload
    
  Priority shedding:
    Assign priorities to request types
    Under load: reject low-priority first
    Critical: health checks, auth, payments - never drop
    Low priority: analytics, recommendations - drop first
```

```python
# Adaptive load shedding based on CPU utilization
import psutil
import random

class LoadShedder:
    THRESHOLDS = {
        "critical": 0.0,    # never drop critical
        "high":     0.7,    # start dropping at 70% CPU
        "medium":   0.5,    # start dropping at 50% CPU
        "low":      0.3,    # start dropping at 30% CPU
    }
    
    def should_shed(self, priority: str = "medium") -> bool:
        """Returns True if this request should be dropped."""
        cpu = psutil.cpu_percent(interval=0.01) / 100
        threshold = self.THRESHOLDS.get(priority, 0.5)
        
        if cpu < threshold:
            return False  # under threshold: allow everything
        
        # Probability increases as CPU exceeds threshold
        # At 100% CPU: drop rate = 100%
        overload_ratio = (cpu - threshold) / (1.0 - threshold)
        return random.random() < overload_ratio

shedder = LoadShedder()

def handle_request(priority: str = "medium"):
    if shedder.should_shed(priority):
        return 503, {
            "error": "service overloaded",
            "retry_after": "5"
        }
    # Process request
```

---

### ⚙️ Wrong vs Right: Local-Only Rate Limiting

```python
# BAD: in-memory rate limiting on a multi-instance service
from collections import defaultdict, deque
import time

# In-memory counter - only works on ONE instance
rate_limits = defaultdict(deque)

def is_allowed_bad(user_id: str, limit: int = 100,
                   window: int = 60) -> bool:
    now = time.time()
    requests = rate_limits[user_id]
    # Remove old requests
    while requests and requests[0] < now - window:
        requests.popleft()
    if len(requests) < limit:
        requests.append(now)
        return True
    return False

# Problem: 10 instances, each allows 100 req/min
# User: 1000 req/min (round-robin to all instances = bypass)
# Each instance: thinks user has only made 100 requests

# GOOD: use centralized Redis for distributed rate limiting
# (see the Redis-based implementation above)

# If Redis is unavailable: graceful degradation
import redis

def is_allowed_good(user_id: str) -> bool:
    try:
        return is_allowed_redis(user_id)
    except redis.exceptions.ConnectionError:
        # Redis down: fail open or use local limiter
        # Fail open: risky (no protection during Redis outage)
        # Local limiter: rough protection during outage
        return is_allowed_local_fallback(user_id)
    # Separate alert on Redis downtime
```

---

### 📐 Scale Considerations

```
At 100 RPS:
  Single Redis node: handles rate limiting
  Local token bucket: sufficient for single-instance
  
At 10,000 RPS:
  Redis rate limit adds ~1ms per request = 100ms at 100x
  Use: local cache + periodic Redis sync (see distributed example)
  Sync interval: 100ms (slight over-limit possible, acceptable)
  
At 1,000,000 RPS:
  Redis cannot handle 1M operations/second per rate check
  Solution: Rate limiting at CDN edge (Cloudflare rules)
  Cloudflare: rate limits at PoP (distributed, no central Redis)
  API Gateway: AWS API Gateway built-in rate limiting
               (no per-request Redis call)
  
  Layer the defenses:
  CDN edge: block obvious abuse (high volume per IP)
  API Gateway: per-API-key limits
  Service level: fine-grained per-user/feature limits
  
Traffic engineering at global scale:
  AWS Traffic Mirroring: copy traffic to analytics without affecting flow
  VPC Flow Logs: captures all IP traffic metadata
  Network ACLs (NACLs): stateless packet filtering (before security groups)
  Use NACLs for: blocking known-bad CIDR ranges at subnet level
                 (no per-connection overhead unlike SGs)
```

---

### 🧭 Decision Guide

```
Rate limiting algorithm selection:

Flexible burst allowed (APIs):
  Token bucket: allows bursts up to capacity
  Best for: public APIs, user-facing services
  
Constant rate enforcement (billing, analytics):
  Leaky bucket: strict constant rate output
  Best for: batch jobs, payment processing (no burst desired)

Distributed vs local:
  Single instance or test environment:
    Local in-memory rate limiter (no Redis needed)
  Multi-instance production:
    Redis-based with Lua scripts (atomic operations)
  Very high RPS (> 50,000/sec):
    Edge rate limiting (CDN/API Gateway layer)
    + coarse application-level limiting only

Rate limit response behavior:
  Accept: 429 with Retry-After header
  Use: HTTP 429 Too Many Requests
  Include: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
  
  return Response(
    status_code=429,
    headers={
      "Retry-After": "1",
      "X-RateLimit-Limit": "100",
      "X-RateLimit-Remaining": "0",
      "X-RateLimit-Reset": str(int(time.time()) + 60)
    }
  )

Load shedding vs rate limiting:
  Rate limiting: by customer/user identity
  Load shedding: by system health + request priority
  Both needed: complement each other
  Rate limiting without shedding: single user with slow queries
  can still exhaust the system
  Shedding without rate limiting: abusive users get same share as others
```
permalink: /technical-mastery/net/traffic-engineering-and-rate-limiting-at-scale/
---