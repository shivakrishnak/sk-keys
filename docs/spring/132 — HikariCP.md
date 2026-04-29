---
layout: default
title: "HikariCP"
parent: "Spring Framework"
nav_order: 132
permalink: /spring/hikaricp/
---
⚡ TL;DR — HikariCP is the ultra-fast connection pool Spring Boot uses by default — it maintains a pre-warmed pool of JDBC connections for instant database access without per-request connection overhead.
## 📘 Textbook Definition
HikariCP is a high-performance JDBC connection pooling library. Instead of creating a new TCP connection to the database for each request (expensive: 10-200ms), HikariCP maintains a pool of pre-created, ready-to-use connections. Spring Boot auto-configures HikariCP as the default connection pool since Spring Boot 2.
## 🟢 Simple Definition (Easy)
Creating a database connection is slow (like starting a phone call from scratch). HikariCP maintains a pool of "always-connected" connections. When you need one, HikariCP hands you an existing one from its pool. When done, you return it — not disconnect.
## 🔩 First Principles Explanation
**Without connection pool:**
```
Request → new TCP connection to DB (10-200ms) → query → close connection
Request → new TCP connection to DB (10-200ms) → query → close connection
... repeated for every query! Huge latency.
```
**With HikariCP:**
```
App startup → HikariCP creates 10 connections (warm pool)
Request 1 → borrow connection instantly (microseconds) → query → return connection
Request 2 → borrow connection instantly → query → return connection
...never pays TCP connection cost again!
```
**HikariCP key config:**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10      # max connections (default: 10)
      minimum-idle: 5            # idle connections kept ready
      connection-timeout: 30000  # ms to wait for connection from pool
      idle-timeout: 600000       # ms until idle connection closed
      max-lifetime: 1800000      # ms max connection lifetime (< DB timeout)
      pool-name: HikariPool-Orders
```
## 💻 Code Example
```java
// HikariCP is the DEFAULT in Spring Boot — no config needed for basic usage
// Just add spring-boot-starter-data-jpa or spring-jdbc dependency
// Inspect pool at runtime
@Autowired DataSource dataSource;
void checkPool() {
    HikariDataSource hikari = (HikariDataSource) dataSource;
    HikariPoolMXBean pool = hikari.getHikariPoolMXBean();
    System.out.println("Active:  " + pool.getActiveConnections());
    System.out.println("Idle:    " + pool.getIdleConnections());
    System.out.println("Pending: " + pool.getThreadsAwaitingConnection());
    System.out.println("Total:   " + pool.getTotalConnections());
}
// Expose via Actuator for monitoring
// management.endpoints.web.exposure.include=metrics
// Metric: hikaricp.connections.active, hikaricp.connections.idle, etc.
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| More pool size = better | Too many connections overwhelm the DB — tune based on DB thread count |
| Connection pool is application-specific | Each app instance has its own pool; database sees total = instances × pool-size |
| HikariCP needs explicit config | Spring Boot autoconfigures it; you only tune when needed |
## 🔥 Pitfalls in Production
**Pitfall: Connection timeout under load**
```yaml
# If all 10 connections are in use and a new request waits > 30s:
# SQLTimeoutException: Connection is not available, request timed out after 30000ms
# Fix: increase pool size or identify long-running queries
maximum-pool-size: 20  # but verify DB can handle it
```
**Pitfall: max-lifetime > DB wait_timeout**
> If `max-lifetime` > MySQL `wait_timeout`, Hikari may hand out a stale closed connection.
> Always set `max-lifetime` to slightly less than the DB connection timeout.
## 🔗 Related Keywords
- **[N+1 Problem](./130 — N+1 Problem.md)** — N+1 exhausts the connection pool
- **[@Transactional](./127 — @Transactional.md)** — holds a connection for the duration of the transaction
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Pre-warmed pool of JDBC connections                  |
+------------------------------------------------------------------+
| DEFAULT     | Spring Boot 2+ uses HikariCP automatically           |
+------------------------------------------------------------------+
| POOL SIZE   | 10 connections default — tune by load testing        |
+------------------------------------------------------------------+
| MONITOR     | hikaricp.connections.* metrics via Actuator           |
+------------------------------------------------------------------+
```
