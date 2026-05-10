---
id: SYD-054
title: System Evolution Strategy
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-001, SYD-003, SYD-005
used_by: SYD-055, SYD-056
related: SYD-051, SYD-060, SYD-062
tags:
  - architecture
  - pattern
  - bestpractice
  - deep-dive
  - advanced
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /syd/system-evolution-strategy/
---

# SYD-054 - System Evolution Strategy

⚡ TL;DR - System evolution strategy is the deliberate approach to changing a production system incrementally while it is running, avoiding the big-bang rewrite that almost never succeeds.

| SYD-054         | Category: System Design          | Difficulty: ★★★ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | SYD-001, SYD-003, SYD-005        |                 |
| **Used by:**    | SYD-055, SYD-056                 |                 |
| **Related:**    | SYD-051, SYD-060, SYD-062        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A five-year-old monolith has 300k lines of code, no tests, and
a schema nobody fully understands. The team decides to rewrite
everything as microservices. They spend 18 months building "the
new system" while the old one keeps changing. Launch day: the
new system misses 40% of the features. The rewrite is abandoned.
$3M wasted. The old monolith is still in production, now even
more hated.

**THE BREAKING POINT:**
Joel Spolsky called this "the single worst strategic mistake
any software company can make." Big-bang rewrites fail because:
the value of the old system is in its business logic - all of
which must be re-implemented perfectly; while the rewrite is
underway, the old system keeps evolving; and the new system
has no operational history, so it breaks in production in ways
the old system stopped breaking years ago.

**THE INVENTION MOMENT:**
Evolve the existing system incrementally. Apply the Strangler
Fig pattern (Martin Fowler, 2004): wrap the old system, route
specific requests to new implementations, deprecate the old
piece by piece. The system is always running. Each change is
small and verifiable.

**EVOLUTION:**
The Strangler Fig pattern formalised incremental replacement.
Michael Feathers' "Working Effectively with Legacy Code" (2004)
provided techniques for testing and modifying untested systems.
Sam Newman's "Monolith to Microservices" (2019) gave a complete
playbook. Today, feature flags, blue-green deployments, and
canary releases are infrastructure that makes incremental
evolution safe at scale.

---

### 📘 Textbook Definition

**System evolution strategy** is the set of techniques and
principles for changing a production software system over time
- including adding features, replacing components, and changing
the architecture - using incremental, reversible, and continuously
deployed changes rather than wholesale replacement.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Replace the ship's planks one at a time while
it is sailing, not while it is in dry dock.

> The Ship of Theseus was repaired plank by plank while still
> in service. At no point was the ship out of commission. After
> all planks were replaced, the ship was modernised and still
> the same ship in service, carrying the same reputation.

**One insight:** A system's value is not in its code; it is in
its accumulated understanding of business rules, edge cases, and
operational behaviour. Evolution preserves that value; rewrite
discards it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A running production system is always more valuable than a
   planned replacement.
2. Every change to a production system must be reversible without
   data loss or downtime.
3. You cannot validate a new system design without real
   production traffic and data.
4. Legacy code embeds business rules; most of those rules are
   undocumented; a rewrite will miss them.
5. The rate of change in the old system during a rewrite makes
   feature parity a moving target that is impossible to hit.

**DERIVED DESIGN:**
From invariant 2: use feature flags, blue-green deployments,
and canary releases for all changes.
From invariant 3: shadow traffic (send production requests to
both old and new systems; compare responses) before cutover.
From invariant 4: write characterisation tests on the old
system before extracting any component.
From invariant 5: freeze features in the old system during
migration or accept that you must port each new feature twice.

**THE TRADE-OFFS:**
**Gain:** System never stops serving users; each change is
small and testable; early detection of design errors; business
continuity.
**Cost:** Evolution is slower than rewrite in theory (not in
practice); requires discipline to resist scope creep; technical
debt in the transition state must be managed explicitly.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Managing the transition state - where old and
new components coexist - is inherently complex.
**Accidental:** Poorly designed seams (no abstraction between
old and new), missing characterisation tests, and no feature
flag infrastructure all make evolution harder than it needs
to be.

---

### 🧪 Thought Experiment

**SETUP:** You have a monolith handling 50k RPS. The team
wants to extract the checkout service into a microservice.
The checkout code is 20k lines with no unit tests.

**WHAT HAPPENS WITHOUT EVOLUTION STRATEGY:**
You extract the code into a new service. It works in staging.
You deploy to production. Three days later, an edge case in
the tax calculation logic causes incorrect charges for users
in Canada. The old monolith had a special-case workaround that
was never documented and was not copied. You roll back. Users
are refunded. Legal involvement. Two months of delay.

**WHAT HAPPENS WITH EVOLUTION STRATEGY:**
You first write characterisation tests: run the old checkout
service 1M times with production request replays; record every
output. These are your golden answers. You build the new service.
You run it in shadow mode - every checkout request goes to both
old and new; you diff the outputs. You find 12 discrepancies
including the Canada tax edge case. You fix them. After 2 weeks
of 0 discrepancies, you route 1% of real traffic to the new
service. You expand to 100% over 2 weeks. No incidents.

**THE INSIGHT:**
Evolution strategy is about managing risk incrementally. Each
step is small enough to roll back safely. The system teaches
you what it knows if you listen to it carefully.

---

### 🧠 Mental Model / Analogy

> Think of system evolution as renovating a house you are still
> living in. You do not demolish the whole house and rebuild it
> because you would have nowhere to live. Instead, you renovate
> room by room. You live in the kitchen while the bedroom is being
> renovated, then move back. The house is always habitable.

- **Rooms** = system components / services
- **Renovation** = refactoring or replacement
- **Living in** = serving production traffic
- **Demolish and rebuild** = big-bang rewrite
- **Move back in** = canary / cutover

Where this analogy breaks down: renovating a room does not
change the plumbing shared with other rooms; software components
often share databases, APIs, or events, making isolation harder
than physical renovation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of throwing away the old system and building a new one
from scratch (which almost always fails), you change the system
one piece at a time while it is still running.

**Level 2 - How to use it (junior developer):**
Apply feature flags to decouple deployment from release. Use
the Strangler Fig: create a facade that routes to the old
implementation, then replace internals piece by piece. Use
blue-green deployments so you can switch back instantly.
Characterisation-test the old code before touching it.

**Level 3 - How it works (mid-level engineer):**
Key patterns:
- **Strangler Fig:** Intercept calls at the boundary (API
  gateway, event bus). New implementation handles a growing
  percentage of calls. Old implementation is removed when
  traffic reaches 0%.
- **Branch by Abstraction:** Introduce an interface over the
  old code; write new implementation behind interface; switch
  implementations via config.
- **Shadow testing:** Run both implementations in parallel;
  compare outputs; alert on divergence.
- **Expand/contract (parallel change):** For DB schema changes,
  first expand (add new column, write to both), then migrate
  data, then contract (remove old column).

**Level 4 - Why it was designed this way (senior/staff):**
System evolution strategy is fundamentally about managing
accumulated institutional knowledge. Legacy code contains
years of bug fixes, edge cases, and regulatory adaptations
that are not written anywhere - they are encoded in the code
behaviour. Characterisation tests capture that behaviour. Shadow
testing validates that new code reproduces it. The alternative
(rewrite) discards that knowledge and learns it again the hard
way: in production incidents.

**Expert Thinking Cues:**
- "What is the seam where I can intercept calls without
  changing the caller?"
- "What characterisation tests do I need before this change?"
- "How do I make this change reversible?"
- "What is the minimum change that lets me learn what I need?"
- "What shared resources (DB, cache, event bus) need migration
  coordination?"

---

### ⚙️ How It Works (Mechanism)

**Strangler Fig pattern:**
```
Before:
  Client → Monolith (checkout, users, orders)

Step 1 - Facade:
  Client → Facade → Monolith (all traffic)

Step 2 - Route subset:
  Client → Facade → New Checkout Service (checkout)
                 → Monolith (users, orders)

Step 3 - Complete:
  Client → Facade → New Checkout Service
                  → New User Service
                  → New Order Service
  Monolith: retired
```

**Expand/contract (schema migration):**
```
Step 1 - Expand:
  ALTER TABLE orders ADD COLUMN customer_id_v2 BIGINT;
  App writes to BOTH order_id (old) and customer_id_v2

Step 2 - Migrate:
  Background job: back-fill customer_id_v2 from order_id

Step 3 - Contract:
  Verify all rows have customer_id_v2 populated.
  App reads from customer_id_v2 only.
  DROP COLUMN order_id (old column removed).
```

**Shadow testing:**
```
Request → Primary handler (old) → Response to user
       → Shadow handler (new)   → Response discarded
                                → Diff: old vs. new
                                → Alert on divergence
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
+--------------------------------------------------+
| Identify component to extract / replace          |
|   ↓                                              |
| Write characterisation tests on old code         |
|   ← YOU ARE HERE                                 |
| Create seam / abstraction layer                  |
|   ↓                                              |
| Build new implementation behind seam             |
|   ↓                                              |
| Shadow test: compare old vs new output           |
|   ↓                                              |
| Canary: 1% → 10% → 50% → 100% traffic           |
|   ↓                                              |
| Remove old code path                             |
+--------------------------------------------------+
```

**FAILURE PATH:**
- Characterisation tests miss an edge case → shadow test
  reveals divergence before users are affected; fix and repeat.
- Canary rollout reveals regression → roll back canary
  immediately; investigate before expanding.
- Shared DB migration fails → expand/contract keeps both
  columns valid; rollback is possible at any step.

**WHAT CHANGES AT SCALE:**
Small team: feature flags in code (if/else) is sufficient.
Mid-size: feature flag service (LaunchDarkly, Flipt) for
  independent control per user segment.
Large: traffic mirroring at service mesh level (Envoy); schema
  changes via migration scripts in CI; canary managed by
  progressive delivery tool (Argo Rollouts, Flagger).

---

### 💻 Code Example

**BAD - big-bang schema migration with downtime:**
```sql
-- BAD: locks table, requires downtime
ALTER TABLE users
  DROP COLUMN legacy_id,
  ADD COLUMN new_id UUID DEFAULT gen_random_uuid();
-- Blocks all reads/writes for minutes on large tables
```

**GOOD - expand/contract non-blocking migration:**
```sql
-- GOOD Step 1: Add new column (no lock on data)
ALTER TABLE users
  ADD COLUMN new_id UUID;

-- Step 2: Backfill in batches (no table lock)
UPDATE users SET new_id = gen_random_uuid()
  WHERE new_id IS NULL
  LIMIT 10000;
-- Repeat until all rows populated

-- Step 3: Add NOT NULL after all rows populated
ALTER TABLE users
  ALTER COLUMN new_id SET NOT NULL;

-- Step 4: Remove old column when safe
ALTER TABLE users DROP COLUMN legacy_id;
```

**BAD - binary feature switch with no gradual rollout:**
```java
// BAD: all or nothing
if (NEW_SERVICE_ENABLED) {
    return newCheckoutService.checkout(cart);
} else {
    return legacyCheckout.checkout(cart);
}
```

**GOOD - gradual canary with rollback capability:**
```java
// GOOD: gradual routing with per-user control
if (featureFlags.isEnabled("new-checkout", userId)) {
    try {
        return newCheckoutService.checkout(cart);
    } catch (Exception e) {
        // Automatic fallback on error
        metrics.increment("new_checkout.fallback");
        return legacyCheckout.checkout(cart);
    }
}
return legacyCheckout.checkout(cart);
```

**How to test / verify correctness:**
- Run characterisation tests before any change; they define
  expected behaviour.
- Run shadow test for at least 1 week with production traffic
  before any canary rollout.
- Verify rollback works: deploy canary, then rollback in < 2 min.

---

### ⚖️ Comparison Table

| Strategy            | Risk      | Speed    | Downtime | Success Rate |
|---------------------|-----------|----------|----------|--------------|
| Big-bang rewrite    | Very high | Slow     | High     | < 20%        |
| Strangler Fig       | Low       | Medium   | Zero     | High         |
| Branch by abstract  | Low       | Medium   | Zero     | High         |
| Feature flags only  | Medium    | Fast     | Zero     | High         |
| In-place refactor   | Medium    | Fastest  | Zero     | Medium       |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The rewrite will be faster than incremental evolution" | Rewrites consistently take 2-5x longer than estimated and rarely achieve feature parity. Incremental evolution is slower per day but reaches the goal sooner. |
| "Legacy code has no value" | Legacy code's value is the accumulated understanding of business rules, edge cases, and operational knowledge. A rewrite loses all of that. |
| "Strangler Fig only works for microservices" | The Strangler Fig pattern applies to any abstraction boundary - classes, modules, database tables, API endpoints. |
| "Feature flags are just for A/B testing" | Feature flags are the primary mechanism for safe system evolution - decoupling deployment from release and enabling instant rollback. |
| "Once the new service is built, migration is fast" | Data migration is almost always the long tail. Schema migrations for multi-TB databases can take weeks or months to complete safely. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Characterisation test gap**

**Symptom:** New service passes all tests in staging but
produces different outputs than old service for 0.1% of
production requests.

**Root Cause:** Characterisation tests were written against
synthetic data that did not include edge cases present in
production data.

**Diagnostic:**
```sql
-- Compare outputs of old vs. new for divergent cases
SELECT old_output, new_output, input_hash
FROM shadow_comparison
WHERE old_output != new_output
ORDER BY created_at DESC LIMIT 100;
```

**Fix:** Expand characterisation tests to cover divergent
production cases found in shadow testing.

**Prevention:** Run shadow testing open-ended with production
traffic replay before any real canary. Never cut over until
divergence rate is 0.

---

**Failure Mode 2: Shared database coupling blocks extraction**

**Symptom:** New service cannot be deployed independently
because it shares the same database schema as the old monolith.
Schema changes require coordinated deployments.

**Root Cause:** Service extraction was not paired with database
decomposition; the new service is a "distributed monolith" by
shared schema.

**Diagnostic:**
```sql
-- Find tables accessed by both old and new service
SELECT table_name, application
FROM db_access_log
GROUP BY table_name
HAVING COUNT(DISTINCT application) > 1;
```

**Fix:** Apply expand/contract to duplicate the shared data
into the new service's schema; sync via event bus during
transition; cut over reads; remove old schema dependency.

**Prevention:** Design service boundaries around data ownership
from the start. Each service must own its own data.

---

**Failure Mode 3: Feature flag debt accumulates**

**Symptom:** Codebase has 200 feature flags, 150 of which
are always-on and dead code. Engineers fear removing them.
Build times increase; code is unreadable.

**Root Cause:** New flags are added for every change but old
flags are never retired after full rollout.

**Diagnostic:**
```bash
# Find feature flags that have been 100% enabled > 90 days
# Using LaunchDarkly API:
curl -H "Authorization: $LD_API_KEY" \
  "https://app.launchdarkly.com/api/v2/flags/<proj>" \
  | jq '.items[] | select(.variations[0].rollout == 100)'
```

**Fix:** Treat feature flag cleanup as technical debt.
For every flag added, assign a removal date (typically
30-90 days post full rollout).

**Prevention:** Add flag expiry dates in code comments.
Sprint-level hygiene: remove flags that have been 100%
rolled out for > 60 days.

---

**Failure Mode 4 (Security): Seam exposes admin endpoints**

**Symptom:** The Strangler Fig facade that routes between
old and new services exposes internal admin endpoints that
were never meant to be accessible from outside the monolith.

**Root Cause:** The routing facade was built to pass all
paths through to the underlying service; internal admin paths
were included accidentally.

**Diagnostic:**
```bash
# Test if internal admin paths are reachable via facade
curl -I https://api.example.com/internal/admin/users
# Expect 404 or 403 - if 200, facade is misconfigured
```

**Fix:** Explicitly whitelist permitted paths in the facade;
block all `/internal/*` paths by default.

**Prevention:** Apply an allowlist approach to routing rules,
not a passthrough with exclusions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-001 - What Is System Design]] - foundational context
- [[SYD-003 - How to Approach Any System Design Problem]] -
  structured thinking
- [[SYD-005 - The System Design Ecosystem Map]] - understanding
  the full landscape

**Builds On This (learn these next):**
- [[SYD-055 - Platform Architecture Design]] - large-scale
  system evolution at platform level
- [[SYD-056 - Emergent Architecture Patterns]] - patterns that
  emerge from evolutionary design

**Alternatives / Comparisons:**
- [[SYD-060 - Constraint-First System Design Thinking]] -
  constraints determine the correct evolution path
- [[SYD-062 - Trade-off Navigation Framework]] - evaluating
  evolution decisions systematically

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS    | Incremental, safe production system change|
| PROBLEM       | Big-bang rewrites almost always fail      |
| KEY INSIGHT   | Legacy code embeds irreplaceable business  |
|               | rules - preserve via characterisation tests|
| USE WHEN      | Modernising any production system          |
| AVOID WHEN    | Greenfield - no legacy to constrain you   |
| TRADE-OFF     | Speed of change vs. safety of continuity  |
| ONE-LINER     | Replace planks one at a time, ship sails  |
| NEXT EXPLORE  | SYD-056 Emergent Architecture Patterns     |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Write characterisation tests before touching any legacy code -
   they capture behaviour that is not written anywhere else.
2. Shadow test new implementations against real production
   traffic before any real user sees them.
3. Feature flags are not optional; they are the rollback
   mechanism for system evolution.

**Interview one-liner:** "System evolution strategy uses
techniques like the Strangler Fig, branch by abstraction,
and expand/contract to change a production system incrementally,
preserving accumulated business logic while modernising
architecture without ever stopping the running system."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Any complex, valuable system
can be changed safely only by preserving its existing behaviour
as invariants while modifying its implementation - test first,
change second, validate continuously.

**Where else this pattern appears:**
- **Database schema migrations:** You never drop a column in the
  same deployment that you stop writing to it; expand/contract
  keeps both valid during the transition window.
- **API versioning:** `/v1` and `/v2` coexist; consumers migrate
  at their own pace; `/v1` is deprecated and sunset only after
  adoption drops to near zero.
- **Human organisations:** Restructuring a company team by team
  (splitting one division into two) is safer than reorganising
  everyone at once; each team adapts incrementally.

---

### 💡 The Surprising Truth

The Strangler Fig pattern is named after the Strangler Fig tree,
which germinates in the upper branches of a host tree, grows
roots down to the ground, and eventually completely envelops
the host - which dies and rots away, leaving the strangler
standing alone. Martin Fowler chose this name deliberately:
the new system grows around the old one, feeds off its
structure, and eventually the old system is gone - but at every
stage during the transition, a fully functional system is
serving users. The name is macabre; the technique is safe.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** A team spent 6 months on the "new
system" using the Strangler Fig pattern but traffic never
actually migrated from the old code path because the product
team kept adding features to the monolith instead of the new
service. What organisational and technical structural changes
would prevent this from happening on the next attempt?
*Hint: Look at how feature freeze agreements, API contracts,
and dedicated migration teams change the incentive structure.*

**Q2 (C - Design Trade-off):** You have a monolith with a 5TB
PostgreSQL database. The checkout component you want to extract
reads from 12 different tables, 6 of which are also written
to by 5 other components. What is your database decomposition
strategy, and how long do you expect the data migration phase
to take with zero downtime?
*Hint: Research the Database-per-Service pattern, the dual-write
with event sourcing approach, and how Shopify decomposed their
monolith database over 3 years.*

**Q3 (A - System Interaction):** During a Strangler Fig
migration, both the old and new checkout service are running
simultaneously. An order is created in the new service but the
inventory deduction still happens in the monolith. How do you
ensure consistency between the two, and what happens if the
network call between them fails mid-transaction?
*Hint: Look at the Saga pattern, the outbox pattern, and how
two-phase commit can be avoided while preserving consistency.*
