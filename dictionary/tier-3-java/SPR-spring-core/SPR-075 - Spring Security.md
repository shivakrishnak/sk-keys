---
version: 1
layout: default
title: "Spring Security"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /spring/spring-security/
id: SPR-035
category: Spring Core
difficulty: ★★★
depends_on: Filter Chain, OAuth2, JWT, Authentication
used_by: REST APIs, Web Applications, Microservices
related: OAuth2, JWT, CORS, CSRF
tags:
  - spring
  - security
  - api
  - deep-dive
---

# SPR-075 - Spring Security

⚡ TL;DR - Spring Security is a servlet filter chain that intercepts every HTTP request, performing authentication (who are you?) and authorization (are you allowed?) before your controller ever sees the request.

| #407            | Category: Spring Core                      | Difficulty: ★★★ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | Filter Chain, OAuth2, JWT, Authentication  |                 |
| **Used by:**    | REST APIs, Web Applications, Microservices |                 |
| **Related:**    | OAuth2, JWT, CORS, CSRF                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every HTTP endpoint in your application needs to verify the caller's identity. Naively, you add authentication checks inside each controller method: read the Authorization header, validate the JWT, check expiry, look up the user, verify the role. Duplicate this across 50 endpoints. Some endpoints check `ADMIN` role, some check `USER`, some are public. A new security requirement arrives: all endpoints must now log access attempts. You touch 50 files. One team member forgets to add the check on a new endpoint. That endpoint is now unauthenticated in production for 6 months before anyone notices.

**THE BREAKING POINT:**
Security logic dispersed across business code is neither auditable nor maintainable. One missed check is a vulnerability. The Principle of Secure by Default cannot be achieved when security is opt-in per endpoint.

**THE INVENTION MOMENT:**
"This is exactly why Spring Security was created."

---

### 📘 Textbook Definition

**Spring Security** is a framework that provides authentication, authorization, and protection against common web exploits for Spring applications. It operates as a chain of `javax.servlet.Filter` implementations that intercept HTTP requests before they reach the `DispatcherServlet`. The `FilterChainProxy` (exposed as a single `DelegatingFilterProxy` in the servlet container) delegates to a chain of `SecurityFilter`s for each request: extracting credentials, authenticating, loading authorities, and enforcing access rules. Authentication results are stored in `SecurityContextHolder` (backed by a `ThreadLocal`) for use throughout the request's processing. Spring Security auto-configures sensible defaults when its starter is added and is fully customizable via a `SecurityFilterChain` bean.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spring Security wraps every HTTP request in a security checkpoint before your code ever runs.

**One analogy:**

> Spring Security is like a hotel with a front desk and key card system. Every door in the hotel has a card reader (filter chain). The front desk issues key cards to authenticated guests (login). Each door checks the card - does this guest have access to this room? (authorization). Housekeeping rooms require a different card type (roles). The manager can re-key all locks from one place (security config) without touching each door individually.

**One insight:**
Security is a cross-cutting concern. Spring Security separates it from business logic by solving it in the filter layer - before the servlet/controller layer. Your controllers assume a security context is established and focus on business rules.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every request passes through the `SecurityFilterChain` - there is no way to receive a request without security filters running (unless explicitly bypassed via `permitAll()` or excluded paths).
2. Authentication populates `SecurityContextHolder.getContext().getAuthentication()` - once set, the authentication is available to any code running in that thread without passing it explicitly.
3. Authorization decisions are evaluated against the populated `Authentication` - roles/authorities are checked against the request URL, HTTP method, or method-level annotations.

**DERIVED DESIGN:**
The filter-based architecture solves the dispersal problem: instead of each controller checking authentication, one filter does it for all. The `SecurityContextHolder` ThreadLocal solves the "how does my service layer know who the user is" problem without passing `User` objects through every method call.

The separation of authentication (establishing who you are) from authorization (deciding what you can do) allows mixing strategies: JWT authentication + role-based authorization, OAuth2 authentication + attribute-based authorization, API key authentication + IP-based rules - all composable.

**THE TRADE-OFFS:**
**Gain:** Security by default (all requests intercepted); centralized security policy; auditable filter chain; rich authentication integrations (OAuth2, LDAP, SAML, JDBC).
**Cost:** Non-trivial to configure for complex scenarios; security misconfiguration is still possible (e.g., wrong `antMatchers` ordering); debugging requires understanding the filter chain order; CSRF protection must be disabled thoughtfully for stateless REST APIs.

---

### 🧪 Thought Experiment

**SETUP:**
A junior developer adds a new `@GetMapping("/admin/users")` endpoint but forgets to add a security annotation or update the security config. What happens in a properly configured Spring Security setup vs. a naively hand-rolled security setup?

**WITH SPRING SECURITY:**
Security config: `anyRequest().authenticated()` (the recommended default). The new endpoint requires authentication - any unauthenticated request gets 401. Even though the developer forgot, the default-secure policy protects the new endpoint automatically. If the endpoint needs to be public, the developer must explicitly add `.requestMatchers("/admin/users").permitAll()` - a conscious opt-out.

**WITHOUT SPRING SECURITY (hand-rolled checks):**
The developer forgot to add `if (!currentUser.hasRole("ADMIN")) throw new ForbiddenException()`. The endpoint is publicly accessible. Nobody notices for months. OWASP A01:2021 - Broken Access Control.

**THE INSIGHT:**
Default-deny (all requests require authentication unless explicitly permitted) is the only secure default. Spring Security's `anyRequest().authenticated()` implements this; hand-rolled security forces every developer to remember to opt-in to security on every endpoint.

---

### 🧠 Mental Model / Analogy

> Spring Security is like the bouncer + backstage pass system at a concert. The bouncer (filter chain) checks every single person entering (every HTTP request). The ticket stub (JWT/session) proves identity. The backstage pass (role/authority) grants access to restricted areas. The band (your controllers) never sees unchecked attendees - everyone who reaches them has been verified.

- "Bouncer at the door" → `SecurityFilter` processing every request
- "Ticket stub" → JWT token or session cookie
- "Checking the ticket" → `JwtAuthenticationFilter` or `UsernamePasswordAuthenticationFilter`
- "Backstage pass types" → `ROLE_ADMIN`, `ROLE_USER`, `SCOPE_read` authorities
- "Backstage area access rules" → `hasRole("ADMIN")` in security config
- "The band" → your `@RestController` methods

Where this analogy breaks down: unlike a physical bouncer who can only check one person at a time, Spring Security's filter chain handles each concurrent request independently (each request has its own `SecurityContext`).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring Security is the tool that makes sure only the right people can access the right parts of your application. It checks who you are (authentication) and what you're allowed to do (authorization) before your application code runs.

**Level 2 - How to use it (junior developer):**
Add `spring-boot-starter-security`. Define a `SecurityFilterChain` bean to configure rules. Use `.requestMatchers("/public/**").permitAll()` for public endpoints and `.anyRequest().authenticated()` as the catch-all. For JWT: configure a `JwtDecoder` and `JwtAuthenticationConverter`. Annotate controller methods with `@PreAuthorize("hasRole('ADMIN')")` for method-level security. Disable CSRF for stateless REST APIs: `http.csrf().disable()`.

**Level 3 - How it works (mid-level engineer):**
Spring Security's `FilterChainProxy` is registered as a servlet filter. For each request, it selects the matching `SecurityFilterChain` (by request matcher). The default filter order: `SecurityContextPersistenceFilter` → `UsernamePasswordAuthenticationFilter` or `BearerTokenAuthenticationFilter` → `ExceptionTranslationFilter` → `FilterSecurityInterceptor`. The `AuthenticationManager` delegates to `AuthenticationProvider`s (DaoAuthenticationProvider for username/password, JwtAuthenticationProvider for tokens). On success, an `Authentication` object is stored in `SecurityContextHolder`. `FilterSecurityInterceptor` then checks the `Authentication`'s authorities against the configured access rules using an `AccessDecisionManager`.

**Level 4 - Why it was designed this way (senior/staff):**
Spring Security's filter chain architecture predates AOP in Spring; filters were the only cross-cutting mechanism available in the servlet model. The `SecurityContextHolder` ThreadLocal is a pragmatic compromise - it avoids passing `Principal` through every method signature, which would pollute APIs. This design breaks in async contexts (spawned threads don't inherit the parent's ThreadLocal), which is why `DelegatingSecurityContextExecutorService` exists. The transition to method-security (`@PreAuthorize`) using SpEL expressions moved authorization to code alongside the secured method - better for auditability. Spring Security 6 deprecated the `WebSecurityConfigurerAdapter` pattern in favor of `SecurityFilterChain` beans - a shift toward composition over inheritance that enables multiple filter chains with different rules for different URL patterns in the same application (e.g., one chain for API paths with JWT, another for admin paths with form login).

---

### ⚙️ How It Works (Mechanism)

```
HTTP REQUEST
    │
    ↓
DelegatingFilterProxy (servlet filter)
    │
    ↓
FilterChainProxy
    │ selects matching SecurityFilterChain
    │
    ↓
SecurityFilterChain (ordered filters):
    │
    ├─1. SecurityContextPersistenceFilter
    │     → restore SecurityContext from session (stateful)
    │       or create new (stateless/JWT)
    │
    ├─2. UsernamePasswordAuthenticationFilter (form login)
    │   OR BearerTokenAuthenticationFilter (JWT/OAuth2)
    │     → extract credentials from request
    │     → call AuthenticationManager.authenticate()
    │       → AuthenticationProvider validates credentials
    │       → returns Authentication with authorities
    │     → SecurityContextHolder.getContext()
    │         .setAuthentication(authentication)
    │
    ├─3. ExceptionTranslationFilter
    │     → catches AccessDeniedException → 403
    │     → catches AuthenticationException → 401
    │
    ├─4. FilterSecurityInterceptor
    │     → match request URL to security rules
    │     → call AccessDecisionManager
    │       → check Authentication.authorities vs. rules
    │       → ACCESS GRANTED or AccessDeniedException
    │
    ↓
DispatcherServlet → @Controller method
    (SecurityContext available via SecurityContextHolder)
```

---

### 💻 Code Example

**Example 1 - Modern SecurityFilterChain configuration:**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // enables @PreAuthorize
public class SecurityConfig {

    @Bean
    public SecurityFilterChain apiSecurity(
            HttpSecurity http) throws Exception {
        return http
            // Stateless REST API - no sessions, no CSRF
            .sessionManagement(s -> s
                .sessionCreationPolicy(STATELESS))
            .csrf(csrf -> csrf.disable())

            // Authorization rules
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**")
                    .hasRole("ADMIN")
                .anyRequest().authenticated())

            // JWT bearer token authentication
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .decoder(jwtDecoder())
                    .jwtAuthenticationConverter(
                        jwtAuthConverter())))

            // Return 401 (not 302 redirect) for unauthorized
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(
                    new HttpStatusEntryPoint(UNAUTHORIZED)))

            .build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        // Validate against JWKS endpoint (OAuth2 server)
        return JwtDecoders.fromIssuerLocation(
            "https://auth.mycompany.com");
    }
}
```

**Example 2 - Method-level security:**

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // Only ADMIN can delete orders
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deleteOrder(
            @PathVariable String id) {
        orderService.delete(id);
        return ResponseEntity.noContent().build();
    }

    // Users can only see their own orders
    // #userId refers to the @PathVariable
    // principal.name is the authenticated user's ID
    @GetMapping("/user/{userId}")
    @PreAuthorize("#userId == authentication.name" +
        " or hasRole('ADMIN')")
    public List<Order> getOrdersForUser(
            @PathVariable String userId) {
        return orderService.findByUser(userId);
    }

    // Access SecurityContext in service layer
    @GetMapping("/my")
    public List<Order> getMyOrders() {
        // SecurityContextHolder available in same thread
        String userId = SecurityContextHolder.getContext()
            .getAuthentication().getName();
        return orderService.findByUser(userId);
    }
}
```

**Example 3 - Testing with Spring Security:**

```java
@WebMvcTest(OrderController.class)
@Import(SecurityConfig.class)
class OrderControllerTest {

    @Autowired MockMvc mockMvc;

    @Test
    @WithMockUser(roles = "USER")
    void userCanGetOwnOrders() throws Exception {
        mockMvc.perform(get("/api/orders/my"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void userCannotDeleteOrders() throws Exception {
        mockMvc.perform(delete("/api/orders/123"))
            .andExpect(status().isForbidden()); // 403
    }

    @Test
    void unauthenticatedUserGets401() throws Exception {
        mockMvc.perform(get("/api/orders/my"))
            .andExpect(status().isUnauthorized()); // 401
    }
}
```

---

### ⚖️ Comparison Table

| Feature           | Session-Based                        | JWT-Based                        | OAuth2/OIDC                      |
| ----------------- | ------------------------------------ | -------------------------------- | -------------------------------- |
| **State**         | Server-side session                  | Stateless                        | Stateless (at resource server)   |
| **Logout**        | Server invalidates session           | Token expiry only (or blacklist) | Token revocation at auth server  |
| **Scalability**   | Session sticky / shared store needed | Any pod validates independently  | Any pod validates via JWKS       |
| **Best For**      | Traditional web apps                 | REST APIs, microservices         | Third-party auth, SSO            |
| **Spring Config** | formLogin() + session                | oauth2ResourceServer().jwt()     | oauth2Login() or resource server |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                            |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@PreAuthorize` works without `@EnableMethodSecurity` | It silently has no effect without the annotation - a critical security gap                                                                         |
| Disabling CSRF is safe for REST APIs                  | Safe ONLY for stateless APIs using JWT/API keys where cookies are not used for authentication; unsafe if cookies carry session tokens              |
| `.antMatchers()` ordering doesn't matter              | First matching rule wins - `.antMatchers("/**").permitAll()` before `.antMatchers("/admin/**").hasRole("ADMIN")` opens all paths                   |
| Spring Security handles XSS automatically             | Spring Security adds security headers (`X-XSS-Protection`, `Content-Security-Policy`); actual XSS prevention requires output encoding in templates |
| `permitAll()` skips Spring Security filters           | `permitAll()` allows the request through the authorization check but ALL filters still run; credentials are still processed                        |

---

### 🚨 Failure Modes & Diagnosis

**1. 403 Forbidden on Valid Admin Request**

**Symptom:** An authenticated user with `ROLE_ADMIN` gets 403 when accessing an admin endpoint despite having the correct role.

**Root Cause:** Role prefix mismatch. Spring Security's `hasRole("ADMIN")` automatically prepends `ROLE_` - it checks for `ROLE_ADMIN`. If the JWT claim contains `"admin"` (lowercase) or `"ADMIN"` (without prefix), the check fails.

**Diagnostic:**

```java
// Add debug logging for security decisions
logging.level.org.springframework.security=DEBUG

// Check granted authorities in a filter or controller
Authentication auth = SecurityContextHolder
    .getContext().getAuthentication();
log.debug("Authorities: {}", auth.getAuthorities());
// Should show: [ROLE_ADMIN] - not [admin] or [ADMIN]
```

**Fix:**

```java
// Option 1: map JWT claim to ROLE_ prefixed authority
public JwtAuthenticationConverter jwtAuthConverter() {
    JwtGrantedAuthoritiesConverter conv =
        new JwtGrantedAuthoritiesConverter();
    conv.setAuthorityPrefix("ROLE_");
    conv.setAuthoritiesClaimName("roles"); // your JWT claim
    JwtAuthenticationConverter authConv =
        new JwtAuthenticationConverter();
    authConv.setJwtGrantedAuthoritiesConverter(conv);
    return authConv;
}

// Option 2: use hasAuthority instead of hasRole
.requestMatchers("/admin/**").hasAuthority("ADMIN")
// hasAuthority checks exact match, no ROLE_ prefix
```

---

**2. 403 on `@PreAuthorize` Despite Correct Role**

**Symptom:** A method annotated with `@PreAuthorize("hasRole('ADMIN')")` returns 403 even though the user has `ROLE_ADMIN`.

**Root Cause:** `@EnableMethodSecurity` (or legacy `@EnableGlobalMethodSecurity`) is missing from the configuration class. Without it, `@PreAuthorize` annotations are parsed but never enforced.

**Diagnostic:**

```bash
# Check if method security is enabled
grep -r "@EnableMethodSecurity\|@EnableGlobalMethodSecurity" src/
# If not found → add to @Configuration class
```

**Fix:**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // MUST be present for @PreAuthorize to work
public class SecurityConfig { ... }
```

---

**3. SecurityContext Lost in Async Code**

**Symptom:** `SecurityContextHolder.getContext().getAuthentication()` returns null in a `@Async` method or inside a `CompletableFuture.supplyAsync()` call.

**Root Cause:** `SecurityContextHolder` is backed by a `ThreadLocal`. Async executors spawn new threads that do not inherit the parent thread's `SecurityContext`.

**Diagnostic:**

```java
@Async
public void asyncOperation() {
    // Returns null! ThreadLocal not propagated to async thread
    Authentication auth = SecurityContextHolder
        .getContext().getAuthentication();
}
```

**Fix:**

```java
// Option 1: configure async executor to propagate SecurityContext
@Configuration
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public Executor getAsyncExecutor() {
        return new DelegatingSecurityContextExecutorService(
            Executors.newFixedThreadPool(10));
    }
}

// Option 2: explicitly pass authentication to async code
Authentication auth = SecurityContextHolder
    .getContext().getAuthentication();
CompletableFuture.supplyAsync(() -> {
    SecurityContextHolder.getContext()
        .setAuthentication(auth); // manually propagate
    return processData();
});
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Filter Chain` - Spring Security is a servlet filter chain; understand how filters intercept requests
- `Authentication` - understand authentication concepts (credentials, tokens, identity) before the Spring implementation
- `JWT` - the most common token format used with Spring Security for stateless REST APIs

**Builds On This (learn these next):**

- `OAuth2` - Spring Security's OAuth2 resource server support; understand the token issuance and validation model
- `CORS` - Spring Security manages CORS headers; misconfigured CORS is a common security vulnerability
- `Spring Boot Testing` - `@WithMockUser`, `MockMvc` security integration - essential for testing secured endpoints

**Alternatives / Comparisons:**

- `Apache Shiro` - alternative Java security framework; simpler API but less Spring integration
- `Quarkus OIDC` - Quarkus's equivalent for OpenID Connect/JWT; similar concepts, different API
- `Manual JWT validation` - validating JWTs directly in a servlet filter; Spring Security does this more robustly with JWKS rotation support

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Servlet filter chain providing            │
│              │ authentication and authorization          │
├──────────────┼───────────────────────────────────────────┤
│ FLOW         │ Request → FilterChainProxy →              │
│              │ Authenticate → Authorize → Controller     │
├──────────────┼───────────────────────────────────────────┤
│ KEY CONFIG   │ SecurityFilterChain bean with             │
│              │ authorizeHttpRequests + jwt/oauth2        │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT SAFE │ anyRequest().authenticated() - all        │
│              │ endpoints require auth unless permitted   │
├──────────────┼───────────────────────────────────────────┤
│ METHOD SEC   │ @EnableMethodSecurity +                   │
│              │ @PreAuthorize("hasRole('ADMIN')")         │
├──────────────┼───────────────────────────────────────────┤
│ REST APIs    │ Disable CSRF, stateless sessions,         │
│              │ JWT via oauth2ResourceServer()            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security by default vs. non-trivial       │
│              │ configuration for complex scenarios       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bouncer before your controller - all     │
│              │  requests checked, none slip through"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OAuth2 → JWT deep-dive → CORS/CSRF        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) A microservice uses Spring Security with JWT authentication. The JWT issuer (OAuth2 server) rotates its signing keys every 24 hours and publishes the new keys at a JWKS endpoint. Your service caches the JWKS at startup. What happens to requests with tokens signed by the new key before the service reloads its key cache? How does Spring Security's default `NimbusJwtDecoder` handle JWKS rotation - and what configuration ensures seamless key rotation without any service restarts?

**Q2.** (TYPE D - Debugging) A security audit reveals that `GET /api/admin/report` returns 200 for unauthenticated requests in production, despite the security config having `anyRequest().authenticated()`. The code review shows no obvious gap. What four distinct Spring Security configuration mistakes could cause this specific bypass - ranked from most to least likely - and what log or metric would definitively identify which one is active?
