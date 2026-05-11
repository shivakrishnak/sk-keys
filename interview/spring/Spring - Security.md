---
layout: default
title: "Spring - Security"
parent: "Spring"
grand_parent: "Interview Mastery"
nav_order: 6
permalink: /interview/spring/security/
topic: Spring
subtopic: Security
keywords:
  - Security Filter Chain
  - Authentication
  - Authorization
  - OAuth2 and JWT
  - CORS and CSRF
difficulty_range: medium to hard
status: in-progress
version: 2
---

# Security Filter Chain

**TL;DR** - Spring Security is a servlet filter chain that intercepts every HTTP request before it reaches DispatcherServlet, applying authentication, authorization, CSRF protection, and session management through a configurable pipeline of security filters.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Security logic scattered in every controller: check auth header, validate token, verify roles. Miss one endpoint and you have an unauthenticated API. No standardized way to handle login flows, session management, or security headers.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A security checkpoint that every request passes through. It checks: "Who are you?" (authentication) and "Are you allowed to do this?" (authorization).

**Level 2 - How to use it (junior developer):**

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**")
                    .permitAll()
                .requestMatchers("/api/admin/**")
                    .hasRole("ADMIN")
                .anyRequest().authenticated())
            .httpBasic(Customizer.withDefaults())
            .build();
    }
}
```

**Level 3 - How it works (mid-level engineer):**

**Filter chain order (simplified):**

```
Request ->
  SecurityContextPersistenceFilter
    (load SecurityContext from session)
  CorsFilter
  CsrfFilter
  LogoutFilter
  UsernamePasswordAuthenticationFilter
    (or OAuth2LoginAuthFilter, BearerTokenFilter)
  ExceptionTranslationFilter
  AuthorizationFilter
    (check access rules)
  -> DispatcherServlet -> Controller
```

**SecurityContext:**

```java
// After authentication, get current user:
SecurityContext ctx = SecurityContextHolder
    .getContext();
Authentication auth = ctx.getAuthentication();
String username = auth.getName();
Collection<? extends GrantedAuthority> roles =
    auth.getAuthorities();
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Multiple filter chains (API + Web):**

```java
@Bean
@Order(1)
public SecurityFilterChain apiChain(
        HttpSecurity http) throws Exception {
    return http
        .securityMatcher("/api/**")
        .authorizeHttpRequests(a ->
            a.anyRequest().authenticated())
        .oauth2ResourceServer(oauth2 ->
            oauth2.jwt(Customizer.withDefaults()))
        .sessionManagement(s ->
            s.sessionCreationPolicy(STATELESS))
        .csrf(c -> c.disable())
        .build();
}

@Bean
@Order(2)
public SecurityFilterChain webChain(
        HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(a ->
            a.anyRequest().authenticated())
        .formLogin(Customizer.withDefaults())
        .build();
}
```

**Custom filter insertion:**

```java
http.addFilterBefore(
    new TenantFilter(),
    AuthorizationFilter.class);
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Spring Security = chain of servlet filters before DispatcherServlet
2. `SecurityFilterChain` bean configures which endpoints need what auth
3. `SecurityContextHolder` stores the current user after authentication

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: How does Spring Security handle stateless REST APIs differently from web applications?**

_Why they ask:_ Tests architectural understanding.

_Strong answer:_

For stateless REST APIs:

```java
http
    .sessionManagement(s ->
        s.sessionCreationPolicy(STATELESS))
    // No session = no CSRF needed
    .csrf(c -> c.disable())
    // JWT bearer token authentication
    .oauth2ResourceServer(o -> o.jwt(j -> j
        .decoder(jwtDecoder())))
    // No login page
    .exceptionHandling(e -> e
        .authenticationEntryPoint(
            (req, res, ex) ->
                res.sendError(401)));
```

Key differences from web apps:

- No HTTP session (no `JSESSIONID` cookie)
- CSRF disabled (token-based auth is CSRF-immune)
- No form login (401 response instead of redirect)
- Token validated on every request (no server-side state)

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Security Filter Chain. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Authentication

**TL;DR** - Authentication verifies "who you are" by validating credentials (password, token, certificate) through an `AuthenticationManager` that delegates to `AuthenticationProvider` implementations, producing a verified `Authentication` object stored in `SecurityContext`.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every endpoint manually reads credentials, queries user database, checks passwords, manages sessions. No standard way to support multiple auth mechanisms (form login + OAuth + API keys) simultaneously.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The system verifies your identity: "You say you're Alice. Prove it." You provide credentials, the system checks them, and either lets you in or rejects you.

**Level 2 - How to use it (junior developer):**

```java
@Bean
public UserDetailsService userDetailsService() {
    return username -> userRepository
        .findByUsername(username)
        .map(user -> User.builder()
            .username(user.getUsername())
            .password(user.getPassword())
            .roles(user.getRoles()
                .toArray(String[]::new))
            .build())
        .orElseThrow(() ->
            new UsernameNotFoundException(
                "User not found: " + username));
}

@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

**Level 3 - How it works (mid-level engineer):**

**Authentication flow:**

```
Credentials (username + password)
     |
     v
AuthenticationManager
     |  (delegates to providers)
     v
AuthenticationProvider
     |  (e.g., DaoAuthenticationProvider)
     v
UserDetailsService.loadUserByUsername()
     |
     v
PasswordEncoder.matches(raw, encoded)
     |
     v
Success: Authentication object
  (principal + credentials + authorities)
     |
     v
SecurityContextHolder.setAuthentication(auth)
```

**Multiple auth providers:**

```java
@Bean
public AuthenticationManager authManager(
        HttpSecurity http) throws Exception {
    AuthenticationManagerBuilder builder =
        http.getSharedObject(
            AuthenticationManagerBuilder.class);
    // Try LDAP first, fall back to database
    builder
        .ldapAuthentication()
            .userDnPatterns("uid={0},ou=people")
            .contextSource()
            .url("ldap://ldap.company.com/dc=com")
        .and().and()
        .userDetailsService(dbUserService)
            .passwordEncoder(passwordEncoder());
    return builder.build();
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Custom AuthenticationProvider (API key):**

```java
@Component
public class ApiKeyAuthProvider
        implements AuthenticationProvider {

    public Authentication authenticate(
            Authentication auth) {
        String apiKey = (String)
            auth.getCredentials();

        ApiClient client = clientRepo
            .findByApiKey(apiKey)
            .orElseThrow(() ->
                new BadCredentialsException(
                    "Invalid API key"));

        return new UsernamePasswordAuthToken(
            client.getName(),
            null,
            client.getAuthorities());
    }

    public boolean supports(Class<?> authType) {
        return ApiKeyAuthToken.class
            .isAssignableFrom(authType);
    }
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `UserDetailsService` + `PasswordEncoder` = basic auth setup
2. `AuthenticationManager` delegates to `AuthenticationProvider` chain
3. Always use BCrypt (or Argon2) - never store plaintext or MD5/SHA

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: How do you implement multi-tenant authentication where each tenant has its own user store?**

_Why they ask:_ Tests advanced architecture skills.

_Strong answer:_

```java
@Component
public class TenantAwareAuthProvider
        implements AuthenticationProvider {

    private final Map<String, UserDetailsService>
        tenantServices;

    public Authentication authenticate(
            Authentication auth) {
        String tenant = TenantContext.getCurrent();
        UserDetailsService svc =
            tenantServices.get(tenant);

        UserDetails user = svc.loadUserByUsername(
            auth.getName());

        if (!encoder.matches(
                (String) auth.getCredentials(),
                user.getPassword())) {
            throw new BadCredentialsException(
                "Bad credentials");
        }

        return new UsernamePasswordAuthToken(
            user, null, user.getAuthorities());
    }
}
```

Steps: Extract tenant from request (header, subdomain, or path) -> resolve tenant-specific UserDetailsService -> authenticate against tenant's user store -> store tenant in SecurityContext for downstream use.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Authentication. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Authorization

**TL;DR** - Authorization determines "what you're allowed to do" after authentication, enforced at URL level (`authorizeHttpRequests`), method level (`@PreAuthorize`, `@Secured`), or domain object level (ACLs).

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Manually checking `if (user.hasRole("ADMIN"))` in every service method. Miss one check and an unprivileged user can access admin data. No audit trail of authorization decisions.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
After verifying who you are, the system checks what you're allowed to do. "You're Alice, but Alice can't delete other users - that requires admin access."

**Level 2 - How to use it (junior developer):**

```java
// URL-level authorization:
http.authorizeHttpRequests(auth -> auth
    .requestMatchers(GET, "/api/products/**")
        .permitAll()
    .requestMatchers("/api/admin/**")
        .hasRole("ADMIN")
    .requestMatchers("/api/orders/**")
        .hasAnyRole("USER", "ADMIN")
    .anyRequest().authenticated());

// Method-level authorization:
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long id) { }

@PreAuthorize("#userId == authentication.name")
public UserProfile getProfile(String userId) { }
```

**Level 3 - How it works (mid-level engineer):**

**Three levels of authorization:**

1. **URL-level** (SecurityFilterChain):
   - Coarse-grained (paths and HTTP methods)
   - Fast (filter level, before controller)

2. **Method-level** (`@PreAuthorize`, `@PostAuthorize`):
   - Fine-grained (SpEL expressions)
   - Can access method parameters
   - Requires `@EnableMethodSecurity`

3. **Domain-object level** (ACLs):
   - Per-entity permissions
   - "User X can edit Document Y"
   - Complex but powerful

```java
@EnableMethodSecurity
@Configuration
public class MethodSecurityConfig {}

@Service
public class DocumentService {

    @PreAuthorize(
        "hasRole('ADMIN') or " +
        "#doc.owner == authentication.name")
    public void update(Document doc) { }

    @PostAuthorize(
        "returnObject.owner == " +
        "authentication.name")
    public Document findById(Long id) {
        return repo.findById(id).orElseThrow();
    }

    @PostFilter(
        "filterObject.visible == true or " +
        "hasRole('ADMIN')")
    public List<Document> findAll() {
        return repo.findAll();
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Custom permission evaluator:**

```java
@Component
public class DocPermissionEvaluator
        implements PermissionEvaluator {

    public boolean hasPermission(
            Authentication auth,
            Object target,
            Object permission) {
        Document doc = (Document) target;
        String perm = (String) permission;

        return switch (perm) {
            case "read" -> doc.isPublic() ||
                isOwner(auth, doc) ||
                isSharedWith(auth, doc);
            case "write" -> isOwner(auth, doc);
            case "delete" -> isOwner(auth, doc) &&
                hasRole(auth, "ADMIN");
            default -> false;
        };
    }
}

// Usage:
@PreAuthorize(
    "hasPermission(#doc, 'write')")
public void update(Document doc) { }
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. URL-level for coarse access control, `@PreAuthorize` for fine-grained
2. SpEL in `@PreAuthorize` can access method params (`#paramName`) and authentication
3. `@PostFilter` filters collection results by permission

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: How do you implement row-level security (user can only see their own data)?**

_Why they ask:_ Tests practical multi-tenant/authorization design.

_Strong answer:_

Multiple approaches:

1. **Service-layer enforcement:**

```java
@PreAuthorize(
    "#userId == authentication.name")
public List<Order> getOrders(String userId) {}
```

2. **JPA Specification + SecurityContext:**

```java
public class OwnedByCurrentUser {
    public static <T> Specification<T> spec() {
        String user = SecurityContextHolder
            .getContext().getAuthentication()
            .getName();
        return (root, q, cb) ->
            cb.equal(root.get("ownerId"), user);
    }
}
// All queries automatically filtered
```

3. **Hibernate filters (database level):**

```java
@FilterDef(name = "tenantFilter",
    parameters = @ParamDef(
        name = "tenantId", type = String.class))
@Filter(name = "tenantFilter",
    condition = "tenant_id = :tenantId")
```

Best practice: Enforce at the lowest possible layer (database/repository) so no code path can bypass it.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Authorization. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# OAuth2 and JWT

**TL;DR** - OAuth2 is the authorization framework (delegated access via tokens), JWT is the token format (self-contained, signed claims). Spring Security supports both OAuth2 client (login with Google) and resource server (validate JWT on API calls).

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every service validates credentials against a user database. Users must share passwords with third-party apps. No single sign-on. Token validation requires a database lookup on every request.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OAuth2: "Let me log in with Google/Okta instead of creating another password." JWT: The proof-of-identity token that APIs validate without calling a central server.

**Level 2 - How to use it (junior developer):**

**Resource Server (validate JWT on API):**

```java
@Bean
public SecurityFilterChain api(
        HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(a ->
            a.anyRequest().authenticated())
        .oauth2ResourceServer(oauth2 ->
            oauth2.jwt(Customizer.withDefaults()))
        .build();
}
```

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com/
          # Auto-fetches JWK set for validation
```

**Level 3 - How it works (mid-level engineer):**

**JWT structure:**

```
Header.Payload.Signature
eyJhbGci... . eyJzdWIi... . SflKxwRJ...
```

```json
// Payload (claims):
{
  "sub": "user123",
  "iss": "https://auth.example.com",
  "exp": 1700000000,
  "roles": ["USER", "ADMIN"],
  "tenant_id": "acme"
}
```

**Mapping JWT claims to Spring authorities:**

```java
@Bean
public JwtAuthenticationConverter
        jwtAuthConverter() {
    JwtGrantedAuthoritiesConverter conv =
        new JwtGrantedAuthoritiesConverter();
    conv.setAuthoritiesClaimName("roles");
    conv.setAuthorityPrefix("ROLE_");

    JwtAuthenticationConverter jac =
        new JwtAuthenticationConverter();
    jac.setJwtGrantedAuthoritiesConverter(conv);
    return jac;
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Token validation strategy:**

- **Signature validation:** Verify JWT signature using issuer's public key (JWKS endpoint). No network call per request after key caching.
- **Expiry check:** Reject expired tokens.
- **Issuer/Audience validation:** Ensure token was issued for this service.

**Refresh token rotation:**

```
Client -> Auth Server: grant_type=refresh_token
Auth Server -> Client: new access_token +
                       new refresh_token
                       (old refresh_token revoked)
```

**Opaque vs JWT tokens:**

| Aspect      | JWT                         | Opaque                          |
| ----------- | --------------------------- | ------------------------------- |
| Validation  | Local (signature)           | Remote (introspection endpoint) |
| Revocation  | Difficult (wait for expiry) | Immediate (delete from store)   |
| Size        | Large (claims inside)       | Small (random string)           |
| Performance | Fast (no network)           | Slower (network per request)    |


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. JWT validated locally via signature (no DB/network call per request)
2. JWTs can't be revoked instantly - use short expiry + refresh tokens
3. `spring.security.oauth2.resourceserver.jwt.issuer-uri` auto-configures validation

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: How do you handle JWT revocation for a "logout all devices" feature?**

_Why they ask:_ Tests understanding of JWT limitations.

_Strong answer:_

JWTs are stateless - you can't revoke them. Strategies:

1. **Short-lived access tokens (5-15 min):** User effectively logged out when token expires. Combine with refresh token revocation in auth server.

2. **Token blacklist (Redis):** Store revoked JWT IDs (`jti` claim) in Redis with TTL matching token expiry. Check on each request. Trade-off: adds a network call per request.

3. **Token version in user record:** Increment user's `tokenVersion` on logout. JWT includes version. Resource server checks version matches (requires DB call or cache).

4. **Refresh token rotation:** On "logout all", revoke all refresh tokens in auth server. Existing access tokens expire within minutes.

Best practice: Short-lived access tokens (5 min) + refresh tokens + immediate refresh token revocation. Acceptable trade-off between security and performance.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for OAuth2 and JWT. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# CORS and CSRF

**TL;DR** - CORS (Cross-Origin Resource Sharing) controls which origins can call your API from browsers. CSRF (Cross-Site Request Forgery) prevents attackers from making authenticated requests on behalf of users. APIs with token auth disable CSRF; web apps with cookies need it.

---

### The Problem This Solves

**CORS without configuration:** Browser blocks `fetch('https://api.example.com')` from `https://frontend.example.com` - same-origin policy.

**CSRF without protection:** Malicious site submits a form to your bank while you're logged in, and your session cookie is sent automatically.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CORS: "Which websites are allowed to call my API?" CSRF: "Is this request really from my user, or from a malicious site?"

**Level 2 - How to use it (junior developer):**

```java
@Bean
public SecurityFilterChain security(
        HttpSecurity http) throws Exception {
    return http
        // CORS configuration
        .cors(cors -> cors
            .configurationSource(corsConfig()))
        // CSRF: disable for stateless API
        .csrf(csrf -> csrf.disable())
        .build();
}

CorsConfigurationSource corsConfig() {
    CorsConfiguration config =
        new CorsConfiguration();
    config.setAllowedOrigins(List.of(
        "https://frontend.example.com"));
    config.setAllowedMethods(List.of(
        "GET", "POST", "PUT", "DELETE"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source =
        new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration(
        "/api/**", config);
    return source;
}
```

**Level 3 - How it works (mid-level engineer):**

**CORS flow:**

```
Browser: OPTIONS /api/orders (preflight)
  Origin: https://frontend.example.com
  Access-Control-Request-Method: POST

Server response:
  Access-Control-Allow-Origin:
    https://frontend.example.com
  Access-Control-Allow-Methods: POST
  Access-Control-Max-Age: 3600

Browser: POST /api/orders (actual request)
  Origin: https://frontend.example.com
```

**When to disable CSRF:**

- Token-based auth (JWT in Authorization header): CSRF immune (browser doesn't auto-send headers)
- Cookie-based auth (JSESSIONID): CSRF protection needed!

**Level 4 - Mastery (senior/staff+ engineer):**

**CSRF with SPA + Cookie auth:**

```java
http.csrf(csrf -> csrf
    .csrfTokenRepository(
        CookieCsrfTokenRepository
            .withHttpOnlyFalse())
    .csrfTokenRequestHandler(
        new SpaCsrfTokenRequestHandler()));
// SPA reads XSRF-TOKEN cookie
// Sends X-XSRF-TOKEN header on mutations
```

**CORS security mistakes:**

```java
// DANGEROUS: allows any origin
config.setAllowedOrigins(List.of("*"));
config.setAllowCredentials(true);
// Browser rejects: can't use * with credentials

// DANGEROUS: reflecting Origin header
config.setAllowedOriginPatterns(List.of("*"));
// Allows any site to make authenticated requests!
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Stateless API (JWT in header): disable CSRF, configure CORS for frontend origin
2. Cookie-based auth: keep CSRF enabled, use `CookieCsrfTokenRepository` for SPAs
3. Never use `allowedOrigins("*")` with `allowCredentials(true)` - it's a security hole

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for CORS and CSRF. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

