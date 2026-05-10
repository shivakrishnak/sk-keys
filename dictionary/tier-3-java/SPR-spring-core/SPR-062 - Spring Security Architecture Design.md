---
id: SPR-062
title: Spring Security Architecture Design
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-050, SPR-055, SPR-061
used_by:
related: SPR-059, SPR-063, SPR-075
tags:
  - spring
  - java
  - advanced
  - security
  - architecture
  - bestpractice
status: complete
version: 2
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /spr/spring-security-architecture-design/
---

# SPR-062 - Spring Security Architecture Design

⚡ TL;DR - Spring Security's filter chain intercepts every request before it reaches a controller; designing it correctly means understanding the filter order, authentication vs authorisation separation, and the SecurityContext thread model.

| Field          | Value                                                                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Depends on** | [[SPR-050 - Spring Security]], [[SPR-055 - Spring Data JPA]], [[SPR-061 - Spring Boot Configuration Strategy]]                                               |
| **Used by**    | -                                                                                                                                                            |
| **Related**    | [[SPR-059 - Spring Architecture at Scale]], [[SPR-063 - Microservice Decomposition with Spring Cloud]], [[SPR-075 - Spring Security OAuth2 Resource Server]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Security logic lives inside controllers and services: `if (user.hasRole("ADMIN"))` scattered across 50 endpoints. Authentication checking in one place, CSRF protection somewhere else, CORS handling in yet another interceptor. A new endpoint is added and the developer forgets to add the security check. No centralised audit of what endpoints are protected and how. Cross-cutting security concerns tangled with business logic.

**THE BREAKING POINT:**

A security audit reveals three unauthenticated endpoints that were added "temporarily" and forgotten. The CSRF token is validated in some controllers but not others. Two different authentication mechanisms conflict because they were added without understanding the filter chain order.

**THE INVENTION MOMENT:**

Spring Security's `SecurityFilterChain` places security as a _pre-controller_ concern implemented in the servlet filter pipeline. Every request is intercepted, authenticated, and authorised before reaching any controller. The filter chain is declarative, testable, and auditable - a single `SecurityFilterChain` bean defines all security rules.

**EVOLUTION:**

- **2004:** Spring Security (Acegi Security) - the original, complex XML-based security
- **2013:** Spring Security 3.2 - Java configuration (`HttpSecurity`), CSRF enabled by default
- **2017:** Spring Security 5.0 - OAuth 2.0 / OIDC support, password encoding standardised
- **2022:** Spring Security 5.7 - `WebSecurityConfigurerAdapter` deprecated; `SecurityFilterChain` beans are the standard
- **2022:** Spring Security 6.0 - Jakarta EE 9; all HTTP methods secured by default; `HttpSecurity.authorizeHttpRequests()` replaces `authorizeRequests()`

---

### 📘 Textbook Definition

**Spring Security architecture** is the layered model of security enforcement in a Spring web application. At the outermost layer, the `DelegatingFilterProxy` bridges the Servlet container's filter pipeline to Spring's bean lifecycle. Inside Spring, `FilterChainProxy` delegates each request through the `SecurityFilterChain` - an ordered list of `Filter` instances that implement authentication (`UsernamePasswordAuthenticationFilter`, `BearerTokenAuthenticationFilter`), session management, CSRF protection, CORS handling, and access control (`AuthorizationFilter`). The resolved `Authentication` is stored in the `SecurityContextHolder` for the duration of the request.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Every HTTP request passes through an ordered filter chain before reaching your code; security is enforced at the chain, not in the code.

> Spring Security is a bouncer at the entrance to your application. It checks ID (authentication) and verifies the guest list (authorisation) before anyone gets through the door. Your controllers never see an unauthenticated or unauthorised visitor.

**One insight:** The `SecurityContextHolder` stores the authenticated principal using a `ThreadLocal`. In reactive (WebFlux) applications, this model breaks - you must use `ReactiveSecurityContextHolder` with Reactor context propagation instead.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Authentication (who are you?) must be resolved before authorisation (what can you do?)
2. Security filters run before controllers - they cannot be bypassed via application code
3. The `SecurityContext` is request-scoped and cleared after each request
4. `HttpSecurity` rules are evaluated in order; first matching rule wins
5. Deny by default - Spring Security 6+ requires explicit permit for all paths

**DERIVED DESIGN:**

From invariant 1 → `SecurityFilterChain` order: authentication filters before `AuthorizationFilter`.
From invariant 2 → security rules cannot be forgotten for new endpoints if `anyRequest().authenticated()` is the default.
From invariant 3 → `SecurityContextHolder` cleared in `SecurityContextPersistenceFilter` after response is committed.
From invariant 5 → `anyRequest().denyAll()` or `anyRequest().authenticated()` must be the final rule.

**THE TRADE-OFFS:**

**Gain:** Centralised, auditable security policy; business code free of security checks; declarative permit/deny rules; automatic CSRF and XSS protection.

**Cost:** Filter chain complexity; debugging requires understanding filter order; reactive apps require different context propagation; stateless JWT and stateful sessions need different configurations.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Distinguishing authentication from authorisation, managing security context lifecycle, and ordering security filters are genuinely complex requirements.

**Accidental:** The pre-5.7 `WebSecurityConfigurerAdapter` extension model was accidentally complex - it required extending a class with many override points, making it unclear which method to override. The new `@Bean`-based `SecurityFilterChain` is cleaner.

---

### 🧪 Thought Experiment

**SETUP:** Three engineers each add a security mechanism: one adds JWT authentication, one adds session-based login, one adds OAuth2 social login. No coordination.

**WHAT HAPPENS without architecture:**

All three authentication mechanisms conflict. JWT filter checks for `Bearer` header first; if missing, falls through to session filter; if no session, redirects to OAuth2 login. The JWT check raises an exception that corrupts the session state. APIs that should be stateless now set cookies. OAuth2 redirect loop occurs when JWT token is expired.

**WHAT HAPPENS with architecture:**

One `SecurityFilterChain` bean. JWT `BearerTokenAuthenticationFilter` configured for `/api/**`. Session-based `UsernamePasswordAuthenticationFilter` for `/web/**`. OAuth2 `OAuth2LoginAuthenticationFilter` for `/oauth/**`. Filter order defined explicitly. API paths are stateless (`sessionCreationPolicy = STATELESS`). Web paths use session. No conflicts.

**THE INSIGHT:**

Spring Security architecture is a coordination protocol for multiple authentication mechanisms. Without a single authoritative `SecurityFilterChain`, every added mechanism can break the others.

---

### 🧠 Mental Model / Analogy

> Spring Security is like an airport security checkpoint. The first station checks your boarding pass (authentication). The second station checks your gate assignment (authorisation). If either check fails, you never reach the plane (controller). The security staff (filters) operate independently of the flight crew (controllers) - the crew never checks credentials.

**Element mapping:**

- Boarding pass check → `UsernamePasswordAuthenticationFilter` / `BearerTokenAuthenticationFilter`
- Gate assignment check → `AuthorizationFilter` with `permitAll()` / `hasRole()` rules
- Security staff → `SecurityFilterChain` filter list
- Flight crew (controllers) → `@RestController` / `@Controller` beans
- Security theatre announcement → `SecurityContextHolder` storing the verified principal
- Boarding pass database → `UserDetailsService` / `JwtDecoder`

Where this analogy breaks down: unlike airport security, Spring Security's `SecurityFilterChain` is fully programmable and can short-circuit, pass through, or modify the request before it reaches the "plane."

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring Security is like a locked door in front of every endpoint in your app. Before any request gets to your code, Spring Security checks: is this person logged in? Do they have permission? If the answer to either is no, the request is rejected and your code never runs.

**Level 2 - How to use it (junior developer):**
Add `spring-boot-starter-security`. Define a `SecurityFilterChain` `@Bean`. Use `http.authorizeHttpRequests()` to specify which paths require which roles. Use `http.formLogin()` for session-based auth or `http.oauth2ResourceServer().jwt()` for JWT. Use `http.csrf().disable()` only for stateless APIs (never for browser-facing apps). Test with `@WithMockUser`.

**Level 3 - How it works (mid-level engineer):**
`DelegatingFilterProxy` (registered by Spring Boot auto-config) delegates to `FilterChainProxy`. `FilterChainProxy` matches the request URL to a `SecurityFilterChain`. The chain's filters run in a defined order: `CsrfFilter` → `CorsFilter` → authentication filters → `AuthorizationFilter`. Authentication filters call `AuthenticationManager`, which delegates to `AuthenticationProvider` implementations. On success, `SecurityContextHolder.getContext().setAuthentication(auth)` stores the result. `AuthorizationFilter` then checks the stored `Authentication` against the path's `AuthorizationManager`.

**Level 4 - Why it was designed this way (senior/staff):**
Spring Security uses the _Chain of Responsibility_ pattern for filters and _Strategy_ for authentication providers deliberately. The chain allows multiple authentication mechanisms to coexist without mutual knowledge - each filter either handles the request or passes it on. The strategy pattern for `AuthenticationProvider` allows `DaoAuthenticationProvider` (username/password), `JwtAuthenticationProvider` (tokens), and `RememberMeAuthenticationProvider` to plug in without modifying the core `AuthenticationManager`. This extensibility model is why Spring Security can be adapted to any authentication protocol.

**Expert Thinking Cues:**

- `SecurityFilterChain` beans can be ordered with `@Order` to handle different URL patterns differently
- `SecurityContextRepository` (default: `HttpSessionSecurityContextRepository`) controls where the `SecurityContext` is persisted between requests
- For WebFlux: `ReactiveSecurityContextHolder.getContext()` returns `Mono<SecurityContext>`; `ThreadLocal` does not work in reactive pipelines

---

### ⚙️ How It Works (Mechanism)

```
[HTTP Request]
     |
[DelegatingFilterProxy] (Servlet container → Spring)
     |
[FilterChainProxy]
     |
[SecurityFilterChain - ordered filter list]
     |
     ├─ DisableEncodeUrlFilter
     ├─ WebAsyncManagerIntegrationFilter
     ├─ SecurityContextHolderFilter
     ├─ HeaderWriterFilter (HSTS, X-Frame-Options)
     ├─ CorsFilter
     ├─ CsrfFilter
     ├─ LogoutFilter
     ├─ [Authentication Filters]
     │   ├─ UsernamePasswordAuthenticationFilter
     │   ├─ BearerTokenAuthenticationFilter (JWT)
     │   └─ OAuth2LoginAuthenticationFilter
     ├─ RequestCacheAwareFilter
     ├─ AnonymousAuthenticationFilter
     ├─ ExceptionTranslationFilter
     └─ AuthorizationFilter ← access decision here
          |
[DispatcherServlet → @RestController]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (JWT stateless API):**

```
[POST /api/orders with Authorization: Bearer <token>]
     |
     ├─ CsrfFilter: disabled for /api/** (stateless)
     |
     ├─ BearerTokenAuthenticationFilter
     |    ├─ Extracts JWT from Authorization header
     |    ├─ JwtDecoder validates signature + expiry
     |    └─ SecurityContextHolder.setAuthentication(jwt)
     |          ← YOU ARE HERE
     |
     ├─ AuthorizationFilter
     |    └─ Checks: hasRole("USER") on /api/orders
     |    └─ Authentication.getAuthorities() → ["ROLE_USER"]
     |    └─ Access GRANTED
     |
[DispatcherServlet → OrderController.createOrder()]
```

**FAILURE PATH:**

- Expired JWT → `JwtValidationException` → `ExceptionTranslationFilter` → HTTP 401
- Missing role → `AccessDeniedException` → `ExceptionTranslationFilter` → HTTP 403
- CSRF token missing on state-changing request → `InvalidCsrfTokenException` → HTTP 403

**WHAT CHANGES AT SCALE:**

At scale, authentication is extracted to a dedicated identity provider (OAuth2 / OIDC). Each microservice becomes a _resource server_ that validates JWT tokens without calling the identity provider. The token carries claims (roles, permissions) that the resource server reads locally. No inter-service authentication network calls on every request.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**

`SecurityContextHolder` uses `ThreadLocal` by default. In async controllers (`@Async`, `CompletableFuture`), the security context is not automatically propagated to child threads. Use `DelegatingSecurityContextExecutor` or `SecurityContextHolder.setStrategyName(MODE_INHERITABLETHREADLOCAL)` to propagate. In WebFlux, context propagation uses Reactor's `Context` - never `ThreadLocal`.

---

### 💻 Code Example

**BAD - security scattered in controllers:**

```java
// Security check in controller - wrong layer
@GetMapping("/admin/users")
public List<User> listUsers(
        Authentication auth) {
    // Manual check: can be forgotten, bypassed
    if (!auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority()
                .equals("ROLE_ADMIN"))) {
        throw new AccessDeniedException("Not admin");
    }
    return userService.findAll();
}
```

**GOOD - security in SecurityFilterChain:**

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain apiSecurity(
            HttpSecurity http,
            JwtDecoder jwtDecoder) throws Exception {
        http
            // Stateless JWT API
            .sessionManagement(s -> s
                .sessionCreationPolicy(STATELESS))
            .csrf(AbstractHttpConfigurer::disable)
            // CORS for API clients
            .cors(c -> c.configurationSource(
                corsConfig()))
            // JWT token authentication
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.decoder(jwtDecoder)))
            // Authorisation rules
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health")
                    .permitAll()
                .requestMatchers("/admin/**")
                    .hasRole("ADMIN")
                .anyRequest()
                    .authenticated());  // deny by default
        return http.build();
    }
}

// Controller is clean - no security logic
@GetMapping("/admin/users")
public List<User> listUsers() {
    return userService.findAll(); // security handled upstream
}
```

**How to test / verify correctness:**

```java
@WebMvcTest(UserController.class)
@Import(SecurityConfig.class)
class UserControllerSecurityTest {
    @Autowired MockMvc mockMvc;

    @Test
    void adminEndpoint_withoutAuth_returns401()
            throws Exception {
        mockMvc.perform(get("/admin/users"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void adminEndpoint_withAdminRole_returns200()
            throws Exception {
        mockMvc.perform(get("/admin/users"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void adminEndpoint_withUserRole_returns403()
            throws Exception {
        mockMvc.perform(get("/admin/users"))
            .andExpect(status().isForbidden());
    }
}
```

---

### ⚖️ Comparison Table

| Concern       | Session-based                   | JWT (stateless)                | OAuth2 OIDC           |
| ------------- | ------------------------------- | ------------------------------ | --------------------- |
| State storage | Server session                  | Client token                   | External IdP          |
| Revocation    | Immediate (delete session)      | Wait for expiry                | Token introspection   |
| Scalability   | Sticky sessions or shared cache | Horizontally scalable          | Horizontally scalable |
| CSRF risk     | Yes (requires CSRF token)       | No (no cookies)                | Depends on cookie use |
| Use case      | Browser web apps                | REST APIs, mobile              | Third-party auth      |
| Spring config | `formLogin()`                   | `oauth2ResourceServer().jwt()` | `oauth2Login()`       |

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                     |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`csrf().disable()` is fine for all APIs"                     | CSRF protection must be disabled only for truly stateless (cookie-free) APIs. Browser-facing apps using cookie sessions MUST enable CSRF.                                                                   |
| "HTTPS is handled by Spring Security"                         | Spring Security handles application-layer security. TLS/HTTPS is a server/load-balancer concern. Spring can enforce HTTPS via `requiresChannel().anyRequest().requiresSecure()` but does not terminate TLS. |
| "`@PreAuthorize` is the best way to secure endpoints"         | `@PreAuthorize` is excellent for method-level security, but URL-level rules in `SecurityFilterChain` provide defence-in-depth and are centrally auditable. Use both.                                        |
| "Spring Security blocks requests before they hit the servlet" | Spring Security runs as a servlet filter, inside the servlet container, after the container's own filters but before the `DispatcherServlet`. It does not intercept at the network level.                   |
| "A 403 means the user is not authenticated"                   | HTTP 403 means the user IS authenticated but lacks permission. HTTP 401 means not authenticated. Spring Security correctly returns 401 for missing authentication and 403 for insufficient permissions.     |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: New endpoint accidentally unprotected**

**Symptom:** Security audit reveals `/api/internal/admin` accessible without authentication.

**Root Cause:** `authorizeHttpRequests` rules use path matchers that don't cover the new path; `anyRequest()` rule is missing or uses `permitAll()`.

**Diagnostic:**

```bash
# Enable Spring Security debug logging
logging.level.org.springframework.security=DEBUG
# Look for: "Checking authorization on ... [PERMIT]"
# vs "Checking authorization on ... [DENY]"
```

**Fix:** Always end `authorizeHttpRequests` with `anyRequest().authenticated()` or `anyRequest().denyAll()`. Never end with `anyRequest().permitAll()`.

**Prevention:** Write a test that requests every known endpoint without authentication and asserts 401/403; this catches new endpoints that forget security rules.

---

**Mode 2: SecurityContext not propagated to async thread**

**Symptom:** `@Async` method returns `null` for `SecurityContextHolder.getContext().getAuthentication()`; permission check fails in async service.

**Root Cause:** `ThreadLocal` SecurityContext not inherited by `@Async` thread pool threads.

**Diagnostic:**

```java
@Async
public void asyncMethod() {
    // Returns null: context not propagated
    Authentication auth =
        SecurityContextHolder.getContext()
        .getAuthentication();
}
```

**Fix:**

```java
@Bean
public Executor asyncExecutor() {
    return new DelegatingSecurityContextExecutor(
        new ThreadPoolTaskExecutor()
    );
}
```

**Prevention:** Always use `DelegatingSecurityContextExecutor` for async task executors in security-sensitive applications.

---

**Mode 3: JWT accepted after user is disabled (Security failure mode)**

**Symptom:** Revoked/disabled user's JWT is still accepted after account deactivation; user can still make API calls.

**Root Cause:** JWT is stateless - the resource server only validates the signature and expiry, not the current user status.

**Diagnostic:**

```bash
# Decode the JWT payload (base64 middle section)
echo "<token>" | cut -d. -f2 | base64 -d
# Check: exp claim vs current time
# Spring Security does NOT call UserDetailsService for JWT by default
```

**Fix:** One of: (1) use short expiry tokens (5-15 minutes) + refresh tokens; (2) add a token revocation list (Redis); (3) use JWT with `jti` claim and maintain a revocation list; (4) add a `JwtAuthenticationConverter` that loads current user status.

**Prevention:** Design access tokens with short expiry. Use refresh tokens for long sessions. Document revocation latency in security runbooks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-050 - Spring Security]] - Spring Security fundamentals
- [[SPR-033 - JDK Dynamic Proxy]] - how Spring Security creates proxy-based AOP guards
- [[SPR-034 - AOP (Aspect-Oriented Programming)]] - the AOP mechanism behind `@PreAuthorize`

**Builds On This (learn these next):**

- [[SPR-075 - Spring Security OAuth2 Resource Server]] - JWT and OIDC configuration
- [[SPR-062 - Spring Security Architecture Design]] - this entry
- [[SPR-063 - Microservice Decomposition with Spring Cloud]] - security in distributed Spring systems

**Alternatives / Comparisons:**

- Keycloak - full Identity Provider with Spring Security adapter
- Auth0 / Okta - cloud-hosted IdP with Spring Security OIDC integration
- Apache Shiro - lightweight alternative security framework for Java

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Spring Security filter chain design       |
| PROBLEM       | Security scattered in code; unprotected   |
|               | endpoints; conflicting auth mechanisms    |
| KEY INSIGHT   | SecurityFilterChain is the single source   |
|               | of truth for all security rules           |
| USE WHEN      | Any Spring web application                |
| AVOID WHEN    | -                                         |
| TRADE-OFF     | Centralised control vs filter complexity  |
| ONE-LINER     | Filter chain = authentication first, then |
|               | authorisation, always before controllers  |
| NEXT EXPLORE  | SPR-075 (OAuth2), SPR-050 (Security)      |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. `SecurityFilterChain` runs before `DispatcherServlet` - security is infrastructure, not application code
2. Always end `authorizeHttpRequests` with `anyRequest().authenticated()` - deny by default
3. JWTs are stateless; revocation requires either short expiry or an out-of-band revocation list

**Interview one-liner:** "Spring Security intercepts every request through an ordered `SecurityFilterChain` before it reaches controllers; authentication filters set the `SecurityContext`, and `AuthorizationFilter` enforces path-level access rules declaratively."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Security is a cross-cutting concern; implement it at the infrastructure layer, not the application layer._ This is the same principle as network firewalls, API gateway auth, and service mesh mTLS - security enforcement at the boundary prevents it from leaking into business logic.

**Where else this pattern appears:**

- **AWS API Gateway** - request authentication and authorisation at the gateway before Lambda/ECS receives the request
- **Nginx/Traefik middleware** - authentication middleware runs before requests reach the application
- **Kubernetes admission controllers** - authorisation checked by the API server before any controller processes the request

---

### 💡 The Surprising Truth

Spring Security enables CSRF protection by default in every Spring Boot web application - but the default is _automatically disabled_ for REST APIs that use `spring-boot-starter-web` with stateless JWT configuration. The nuance that trips many teams: CSRF protection is based on whether the session creation policy is `STATELESS`. A common mistake is disabling CSRF globally with `csrf().disable()` on a `SecurityFilterChain` that also serves a browser-rendered admin UI with session cookies. The UI then becomes vulnerable to CSRF attacks. The correct design is separate `SecurityFilterChain` beans: one for the API (stateless, CSRF disabled) and one for the admin UI (session-based, CSRF enabled), ordered with `@Order`.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** Spring Security's `ExceptionTranslationFilter` catches `AuthenticationException` and `AccessDeniedException` and translates them to HTTP 401 and 403. What happens if a service bean (not a filter) throws `AccessDeniedException` inside a `@Transactional` method - does Spring Security still intercept it?

_Hint:_ Trace the call stack: `@Transactional` proxy → service method → `AccessDeniedException` → propagates up to `@PreAuthorize` AOP proxy → propagates to `DispatcherServlet` exception handler vs `ExceptionTranslationFilter` - which one catches it first?

**Question 2 (C - Design Trade-off):** You need to support both a browser-facing web application (session cookies, CSRF protection required) and a REST API (JWT tokens, stateless) in the same Spring Boot application. Should you use one `SecurityFilterChain` bean with complex rules or two separate beans with `@Order`? What are the trade-offs?

_Hint:_ Consider `requestMatchers` scoping, the interaction between session creation policies, and what happens when a `/api/**` endpoint is accidentally matched by the web filter chain.

**Question 3 (E - First Principles):** `SecurityContextHolder` uses `ThreadLocal` to store the current authentication. Why is this a problem for reactive (WebFlux) applications, and what is the fundamental difference in how Reactor context works compared to `ThreadLocal`?

_Hint:_ Think about how a single request in WebFlux may execute on multiple threads (event-loop thread for network I/O, `boundedElastic` thread for blocking calls, another event-loop thread on response) - who owns the `ThreadLocal` at each point?
