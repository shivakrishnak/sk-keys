---
layout: default
title: "Boat Anchor Anti-Pattern"
parent: "Design Patterns"
nav_order: 806
permalink: /design-patterns/boat-anchor-anti-pattern/
number: "806"
category: Design Patterns
difficulty: ★★☆
depends_on: "Anti-Patterns Overview, Lava Flow Anti-Pattern, Technical Debt"
used_by: "Code review, legacy system analysis, refactoring planning"
tags: #intermediate, #anti-patterns, #design-patterns, #dead-code, #over-engineering, #technical-debt
---

# 806 — Boat Anchor Anti-Pattern

`#intermediate` `#anti-patterns` `#design-patterns` `#dead-code` `#over-engineering` `#technical-debt`

⚡ TL;DR — **Boat Anchor** is keeping a component, module, or subsystem in the codebase that was built for a planned feature that never launched — dead weight that slows the system without providing value, like an anchor dragging behind a boat.

| #806            | Category: Design Patterns                                      | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Anti-Patterns Overview, Lava Flow Anti-Pattern, Technical Debt |                 |
| **Used by:**    | Code review, legacy system analysis, refactoring planning      |                 |

---

### 📘 Textbook Definition

**Boat Anchor Anti-Pattern** (Brown et al., "AntiPatterns", 1998): a software component, subsystem, or dependency retained in a system after it has ceased to serve a useful purpose — built in anticipation of a requirement that was cancelled, postponed indefinitely, or never materialized. Unlike Lava Flow (which was once active and hardened), Boat Anchor code was often never used at all in production: it was built speculatively. The name comes from the metaphor of a boat dragging an anchor — the anchor serves no purpose (the boat isn't anchored) but creates drag, increases weight, and consumes resources. Manifestations: a full authentication plugin built for an enterprise customer that pulled out; a batch processing engine built for an analytics feature that was deprioritized; an entire microservice scaffolded but never connected to any traffic.

---

### 🟢 Simple Definition (Easy)

Team builds a full multi-currency support module in anticipation of an international expansion. The expansion was cancelled. The module: 3,000 lines of code, 120 tests, 2 new database tables — all maintained, updated whenever currency data changes, occasionally causing merge conflicts. Nobody uses it. Nothing calls it. It's just there, costing maintenance time. Boat Anchor: built for a future that didn't arrive.

---

### 🔵 Simple Definition (Elaborated)

A startup pivoted from B2C to B2B 18 months ago. Still in the codebase: the social sharing module (share to Twitter/Instagram/Facebook), the referral system, the social profile pages, and the gamification/badges system. All built for B2C, none applicable to B2B. None removed. Each module: has dependencies, schema migrations, configuration, tests, and occasional breaking changes when libraries are upgraded. 8 developers spend roughly 2 hours per month maintaining code nobody uses. Boat Anchor: dead weight from a strategic direction the company abandoned.

---

### 🔩 First Principles Explanation

**How Boat Anchors form and how to systematically remove them:**

```
BOAT ANCHOR ACCUMULATION PATTERNS:

  1. SPECULATIVE FEATURE BUILDING (YAGNI violation):

  // "We'll need multi-tenancy eventually — let's build it now."
  // 3 months of work: tenant isolation, tenant-scoped queries, tenant config
  // Product decision: single-tenant SaaS only for the foreseeable future

  // Result:
  // - Every query: WHERE tenant_id = ? (performance overhead)
  // - Every domain object: has tenantId field (cognitive overhead)
  // - Every test: sets up tenant context (test setup overhead)
  // - No multi-tenant customers: benefit = 0

  YAGNI: "You Ain't Gonna Need It" (XP principle, Ron Jeffries)
  Build what is needed NOW. Don't build for hypothetical future requirements.

  2. CANCELLED INTEGRATION SCAFFOLDING:

  // Engineering built full Salesforce CRM integration:
  // - SalesforceAuthService, SalesforceContactService, SalesforceOpportunityService
  // - 4 database tables for CRM sync state
  // - OAuth flow for Salesforce connection
  // - 15 Salesforce-specific DTOs

  // Sales deal with Salesforce integration requirement: fell through.
  // Code: stays in the repo. Never activated. Regularly updated when
  // Salesforce SDK version changes break compilation.

  3. ABANDONED MIGRATION ARTIFACTS:

  // Team started migrating from Hibernate to JOOQ.
  // Got 30% through. Product priorities changed. Migration stalled.
  // Result: both Hibernate AND JOOQ in the codebase simultaneously.
  // Some entities: @Entity (Hibernate)
  // Some queries: JOOQ DSL
  // Team: unclear which to use for new code
  // Both: maintained, both: tested, both: updated when DB schema changes

  4. DEPRECATED PLUGIN/SDK RETENTION:

  // Application used AWS SDK v1 → migrated to v2 → v1 still in pom.xml
  // Both: on the classpath. Classpath conflicts. Confusing to new developers.
  // "We kept v1 in case something doesn't work in v2"
  // It's been 2 years. Everything works with v2. AWS SDK v1 is EOL.

BOAT ANCHOR vs. LAVA FLOW:

  Lava Flow: was once ACTIVE in production, hardened, now feared
  Boat Anchor: was built speculatively, NEVER fully active, now inert

  Similarity: both are dead weight, both feared, both should be removed
  Difference: Boat Anchor typically has clearer removal path (was never active)

BOAT ANCHOR REMOVAL PROCESS:

  Step 1: Identify (static analysis + architectural review)
  - Find all entry points to the module
  - Confirm: none are reachable from active code paths
  - Check feature flags: is it behind a disabled flag?

  Step 2: Notify (short review)
  - Confirm with product owner: "Multi-currency feature — still planned?"
  - "No" → schedule removal sprint

  Step 3: Remove (one commit per module)
  - Remove source code
  - Remove database migrations (or add a drop migration)
  - Remove pom.xml/build.gradle dependencies
  - Remove configuration entries

  Step 4: Document (in commit message)
  // "Remove multi-currency module — feature cancelled Q3 2023 per product decision.
  //  Code archived in git history. DB tables dropped in migration V42."
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Boat Anchor awareness:

- Speculative features feel like "good engineering" — anticipating future needs
- Removing code feels risky and unproductive

WITH Boat Anchor removal:
→ Codebase represents current system state. Onboarding is faster. Build and test times drop. No cognitive overhead from unused abstractions.

---

### 🧠 Mental Model / Analogy

> A fishing boat with its anchor dragging along the seabed — not deployed for anchoring, just forgotten and dragging. The anchor adds weight, creates drag, reduces speed, consumes fuel — all without anchoring the boat (which is actively moving). Removing the anchor: boat becomes lighter, faster, more fuel-efficient. The captain's fear: "What if we need to anchor in an emergency?" Reality: the anchor line hasn't been secured to the cleat for 2 years. It's dragging, not anchoring.

"Anchor dragging along the seabed" = speculative code that was never activated
"Adds weight, creates drag, reduces speed" = build time overhead, test suite complexity, cognitive load
"Captain's fear: emergency anchoring" = "we might need this feature eventually"
"Anchor line not secured to the cleat" = no active code path calls into the module
"Remove anchor: lighter, faster" = remove boat anchor code: faster build, cleaner codebase

---

### ⚙️ How It Works (Mechanism)

```
YAGNI PRINCIPLE (prevention of Boat Anchor):

  YAGNI: You Ain't Gonna Need It
  Source: Ron Jeffries, Kent Beck — Extreme Programming (XP), 1999

  Rule: implement a feature when it is ACTUALLY needed, not when you
        ANTICIPATE it will be needed.

  Why YAGNI works:
  - Requirements change: what you build today for "future needs" is often wrong
  - Cost of building now: developer time + maintenance forever
  - Cost of building when needed: developer time (no maintenance until needed)
  - Future requirements, when real, are better understood than speculative ones

  FEATURE FLAGS as alternative to Boat Anchor:
  // Instead of leaving dead code, use feature flags:
  @Service
  class MultiCurrencyService {
      @Value("${feature.multi-currency.enabled:false}")
      private boolean enabled;

      public Money convert(Money amount, Currency target) {
          if (!enabled) {
              throw new FeatureNotEnabledException("Multi-currency not enabled");
          }
          return conversionService.convert(amount, target);
      }
  }
  // Feature flag: disable in all environments
  // Clear: code exists but is explicitly disabled
  // Easier removal: delete code, delete flag config
  // Avoids confusion: not silently dead — explicitly disabled

  DETECTION TOOLS:
  - IntelliJ IDEA: "Unused declaration" inspection → unused at module entry points
  - Maven: dependency:analyze → declared but unused dependencies
  - Feature flag audit: flags disabled for 6+ months = Boat Anchor candidate
  - Architecture review: modules with no inbound dependencies
```

---

### 🔄 How It Connects (Mini-Map)

```
Speculative code built for unneeded features → unused → dead weight maintenance burden
        │
        ▼
Boat Anchor Anti-Pattern ◄──── (you are here)
(speculative, never-activated code; built but never useful; dead weight)
        │
        ├── Lava Flow: similar — both are dead weight; Lava Flow was once active
        ├── YAGNI Principle: the preventive principle (don't build until needed)
        ├── Technical Debt: Boat Anchor is "speculative debt" — built in advance at cost
        └── Feature Flags: an alternative to Boat Anchor code (explicit enable/disable)
```

---

### 💻 Code Example

```java
// Identifying and removing a Boat Anchor: cancelled enterprise feature

// BOAT ANCHOR — full SAML SSO integration built for a deal that fell through:
// Files: SamlConfigurer.java, SamlUserDetailsService.java, SamlAuthResponse.java,
//        SamlMetadataController.java, saml-keystore.jks
// Database table: saml_service_providers (never populated)
// Dependencies in pom.xml:
//   <dependency>
//       <groupId>org.springframework.security.extensions</groupId>
//       <artifactId>spring-security-saml2-core</artifactId>
//       <version>1.0.10.RELEASE</version>
//   </dependency>
// Status: No customers configured. No entry point active. 2 years in codebase.

// DETECTION:
// 1. Find Usages on SamlConfigurer: 0 references from active code
// 2. Search for @Bean references: samlAuthenticationProvider not wired in active security config
// 3. Check DB: SELECT COUNT(*) FROM saml_service_providers → returns 0 (never used)
// 4. Check feature flag: saml.enabled=false in ALL environments

// REMOVAL COMMIT (proper documentation):
// git commit -m "Remove SAML SSO Boat Anchor
//
// Feature was built for Acme Corp enterprise deal (Q2 2022).
// Deal closed without SAML requirement. Feature never activated.
// saml_service_providers table had 0 rows in all environments.
// All code, dependencies, and DB table dropped.
// DB: migration V58_drop_saml_service_providers.sql
// If SAML needed in future: git log --all can recover the implementation."

// VERIFICATION (run in CI before merging removal PR):
class SamlRemovalVerificationTest {
    @Test
    void noSamlClassesRemainInClasspath() {
        assertThatThrownBy(() -> Class.forName("org.springframework.security.saml.SAMLEntryPoint"))
            .isInstanceOf(ClassNotFoundException.class);
    }

    @Test
    void samlTableDoesNotExist() {
        // Run against test DB — Flyway migration should have dropped the table
        assertThatThrownBy(() -> jdbcTemplate.queryForList("SELECT * FROM saml_service_providers"))
            .isInstanceOf(BadSqlGrammarException.class);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Keeping code is always "safer" than removing it | This reverses the risk: keeping unused code adds a maintenance surface (must update when dependencies change, confuses new developers, increases build time) with zero benefit. Version control makes removal safe — every deleted line can be recovered with `git show <hash>`. The risk of keeping Boat Anchor code is cumulative and compounding; the risk of removing it (with version control) is near-zero. |
| Boat Anchor and Lava Flow are the same thing    | Boat Anchor: built speculatively for a feature that never activated; often relatively clean code that was never integrated. Lava Flow: was once active in production; hardened and feared; tangled with active code. Boat Anchor is typically easier to remove (clear boundaries, never integrated). Lava Flow is harder (interwoven with live code paths). Both are dead weight; removal strategies differ.      |
| YAGNI means never designing for extensibility   | YAGNI applies to features and requirements, not to code quality. Writing clean, well-structured, testable code with clear interfaces is NOT YAGNI violation — it's the foundation for future features. YAGNI violation: implementing multi-currency support before any customer has requested it. Not YAGNI: designing the Money value object cleanly so that currency can be added when needed.                  |

---

### 🔥 Pitfalls in Production

**Boat Anchor dependency causing security vulnerability through old transitive dependency:**

```xml
<!-- ANTI-PATTERN — Boat Anchor dependency keeping vulnerable library on classpath: -->

<!-- pom.xml — feature from cancelled project (2021): -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>legacy-analytics-connector</artifactId>
    <version>2.1.0</version>
    <!-- Boat Anchor: analytics feature cancelled. But dependency remains. -->
</dependency>

<!-- legacy-analytics-connector:2.1.0 transitively depends on: -->
<!--   log4j:log4j:1.2.17 (EOL, multiple CVEs) -->
<!--   commons-collections:3.2.1 (CVE-2015-7501, deserialization RCE) -->

<!-- Result: Boat Anchor dependency introduces 2 known CVEs into production. -->
<!-- OWASP Dependency Check / Snyk will flag these. -->
<!-- Developer response: "We need that dependency for the analytics feature." -->
<!-- Reality: analytics feature was cancelled 2 years ago. -->

<!-- FIX: remove the Boat Anchor dependency. -->
<!-- After removal: transitive CVEs gone. Classpath cleaner. Build faster. -->

<!-- PREVENTION: quarterly dependency audit: -->
<!--   mvn dependency:analyze → "declared but unused" = Boat Anchor candidate -->
<!--   mvn versions:display-dependency-updates → outdated dependencies -->
<!--   Snyk/OWASP Dependency Check → CVE scan on all dependencies -->
```

---

### 🔗 Related Keywords

- `Lava Flow Anti-Pattern` — related: Lava Flow was once active; Boat Anchor was never activated
- `YAGNI Principle` — the preventive principle: don't build until actually needed
- `Technical Debt` — Boat Anchor is speculative debt with ongoing maintenance cost and zero benefit
- `Feature Flags` — an alternative: make unactivated features explicitly disabled rather than dead code
- `Dependency Management` — Boat Anchor dependencies carry transitive CVE risk

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Code built for a feature that never       │
│              │ launched. Dead weight. Drags the system  │
│              │ without providing value.                  │
├──────────────┼───────────────────────────────────────────┤
│ DETECT WHEN  │ "Find Usages" → 0; feature flag disabled  │
│              │ for 6+ months; product says feature       │
│              │ cancelled; dependency "declared but unused"│
├──────────────┼───────────────────────────────────────────┤
│ FIX WITH     │ Confirm cancellation with product; remove │
│              │ code + deps + schema; document in commit; │
│              │ git history is the recovery mechanism     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Anchor dragging along the seabed: boat   │
│              │  is moving, anchor isn't anchoring —     │
│              │  just adding drag and burning fuel."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ YAGNI → Feature Flags → Technical Debt →  │
│              │ Lava Flow → Dependency Management          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The YAGNI principle (You Ain't Gonna Need It) is often in tension with "good architecture" — designing for extensibility. The debate: should you design your payment service to support multiple payment gateways from day one (anticipating future Stripe + PayPal + Apple Pay needs) or only implement Stripe and refactor when the second gateway is needed? Martin Fowler calls this the "Yagni Cost-Benefit" tradeoff. What factors tip the decision toward designing for extensibility NOW vs. waiting (YAGNI)?

**Q2.** Feature flags (LaunchDarkly, Unleash, Spring Cloud Config flags) are often proposed as an alternative to removing Boat Anchor code: "disable the feature flag, and the code is effectively inactive." But feature flags have a lifecycle problem: flags accumulate, old flags are never cleaned up, the codebase fills with `if (featureFlags.isEnabled("old-feature-2021"))` branches — creating a "Flag Debt" anti-pattern. How should a team manage feature flag lifecycle to prevent Flag Debt? What criteria should trigger feature flag removal, and what tooling (e.g., flag expiration metadata) helps enforce cleanup?
