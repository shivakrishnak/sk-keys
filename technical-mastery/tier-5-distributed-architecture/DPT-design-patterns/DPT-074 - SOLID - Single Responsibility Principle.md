---
id: DPT-074
title: "SOLID: Single Responsibility Principle"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-043
used_by: DPT-075, DPT-076, DPT-077, DPT-078
related: DPT-043, DPT-075, DPT-076, DPT-077, DPT-078
tags:
  - concept
  - solid
  - intermediate
  - single-responsibility
  - cohesion
  - separation-of-concerns
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 74
permalink: /technical-mastery/design-patterns/srp/
---

⚡ TL;DR - A class should have one reason to change.
"Reason to change" = one stakeholder or actor whose
requirements drive changes to that class. Not "does
one thing" - a class can do many things for the same
actor. The principle is about change OWNERSHIP, not
about the number of methods.

| #74 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-043 | |
| **Used by:** | DPT-075, DPT-076, DPT-077, DPT-078 | |
| **Related:** | DPT-043, DPT-075, DPT-076, DPT-077, DPT-078 | |

---

### 🔥 The Problem This Solves

**THE MULTI-REASON-TO-CHANGE CLASS:**
A `UserService` class handles:
- User authentication (Security team drives changes)
- User profile management (Product team drives changes)
- User activity logging (Compliance team drives changes)

Three actors, three reasons to change. When Security
needs to change the authentication logic: they must
modify `UserService`. They must not break the product
profile management code or the compliance logging code.
But these are all in the same file, subject to the same
test suite, deployed together.

**THE COST:**
Unrelated changes cause merge conflicts, accidental
breakage of adjacent functionality, inflated test suites,
and cross-team coordination overhead. The three teams
step on each other.

**THE SOLUTION:**
Split by actor. `AuthenticationService` (Security),
`UserProfileService` (Product), `UserActivityLogger`
(Compliance). Each has one actor. Each changes for one
reason.

---

### 📘 Textbook Definition

The **Single Responsibility Principle (SRP)** is the
first of the SOLID principles (Robert C. Martin):

> "A class should have only one reason to change."

Martin's clarification: a "reason to change" corresponds
to an ACTOR - a group of stakeholders whose requirements
drive changes to that class. A class has one responsibility
when only one actor's requirements affect it.

**Common misinterpretation:**
"A class should do only one thing."
This misinterpretation leads to tiny classes that do
one method each. The principle is not about method count.
A `UserProfile` class may have 10 methods (get, set,
validate fields) and still have ONE responsibility
(representing a user's profile data). One actor (product
team) drives all changes to it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One reason to change = one actor whose requirements
drive changes to this class.

**One analogy:**
> A contractor who answers to one client vs one who answers
> to three clients simultaneously. Three clients for
> the same project: conflicting instructions, triple
> the coordination, impossible to satisfy all three.
>
> A class with three actors: three masters. Conflicting
> changes, triple the coupling, impossible to change
> for one without risking the others.
>
> SRP: each class has one client (actor) whose instructions
> it follows. One master, one responsibility, one reason
> to change.

---

### 🔩 First Principles Explanation

**COHESION:**
SRP is the definition of high cohesion applied to classes.
Cohesion = how closely related the responsibilities of
a module are. High cohesion: all methods and data serve
the same actor's purpose. Low cohesion: methods serve
different actors' purposes.

**THE ACTOR-RESPONSIBILITY MAPPING:**
For each class in the codebase: identify who (which actor,
which team, which stakeholder) drives changes to it.
If the answer is one team: SRP is satisfied.
If the answer is multiple teams: SRP is violated. Split
the class by actor.

**COUPLING CONSEQUENCE:**
SRP violation creates COUPLING between unrelated actors.
When Security changes authentication: the compliance
logger must be retested and redeployed. Not because
the compliance logger changed, but because it shares
a file with the authentication code. SRP removes this
artificial coupling.

**MICROSERVICE PARALLEL:**
At the service level, SRP says: each microservice should
be owned by one team (Conway's Law / Inverse Conway
Maneuver). A service owned by two teams has two reasons
to change at the service level. The principle applies
at every granularity: method, class, module, service.

---

### 🧪 Thought Experiment

**FINDING THE ACTOR:**

A `ReportGenerator` class with methods:
- `generateHtmlReport()` - for the web team
- `generatePdfReport()` - for the legal team
- `sendReportByEmail()` - for the operations team

Three actors. Three reasons to change. If web team
changes HTML output format: you modify the class.
You risk breaking the legal team's PDF output and
the operations team's email logic. All three methods
are in the same file.

SRP split:
- `HtmlReportRenderer` (one actor: web team)
- `PdfReportRenderer` (one actor: legal team)
- `ReportEmailSender` (one actor: operations team)
- `ReportGeneratorFacade` (optional: if clients need one entry point)

Now each class has one actor. The web team changes HTML
output: they modify `HtmlReportRenderer` only. The legal
team's PDF and the operations team's email are unaffected.

---

### 🧠 Mental Model / Analogy

> SRP = the "one boss" model.
> An employee who reports to one manager: clear priorities,
> consistent direction, single performance review.
>
> An employee who reports to three managers simultaneously:
> conflicting priorities (whose task first?), inconsistent
> direction (each manager has different standards),
> impossible to satisfy all three simultaneously.
>
> A class reporting to three actors: conflicting change
> requirements, inconsistent evolution, impossible to
> optimize for all three. One actor = one boss = clarity.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Identifying actor violations:**
Look at a class and ask: "Which different stakeholder
groups care about changes to this class?" If more than
one group: potential SRP violation. The "groups" might
be teams, departments, or just conceptual domains.

**Level 2 - Applying SRP without fragmentation:**
SRP does not require one method per class. A `User` domain
object may have many methods (all related to representing
user data - one actor: the product team). A `PaymentProcessor`
may have many methods (all related to processing payments -
one actor: the payments team). SRP is satisfied in both.

**Level 3 - SRP at module and service level:**
SRP applies at every granularity. A module should be owned
by one team. A microservice should be owned by one team.
An API endpoint should serve one client type. When a
module serves multiple teams: Conway's Law creates the
same multi-actor coupling problem at scale. The Inverse
Conway Maneuver: design team boundaries to match the
desired architecture's actor boundaries.

---

### ⚙️ How It Works (Mechanism)

```
SRP Actor Analysis
┌─────────────────────────────────────────────────────────┐
│ STEP 1: List the class's responsibilities (methods/data)│
│                                                         │
│ STEP 2: For each responsibility: who drives changes?   │
│         (Which actor would ask for a change here?)     │
│                                                         │
│ STEP 3: Count distinct actors                          │
│         1 actor → SRP satisfied                        │
│         2+ actors → SRP violated: split by actor       │
│                                                         │
│ STEP 4: For each actor's set of responsibilities:      │
│         Create one class/module per actor              │
│                                                         │
│ STEP 5: If clients need one entry point: add Facade    │
│         (the Facade has one responsibility: delegation) │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - SRP violation and fix:**

```java
// BAD: UserService with 3 actors driving changes.
// Actor 1: Security team (authentication)
// Actor 2: Product team (profile management)
// Actor 3: Compliance team (activity logging)

class UserService {

    // ACTOR 1: Security team drives these
    User authenticate(String username, String password) {...}
    void logout(String sessionId) {...}
    boolean isSessionValid(String sessionId) {...}

    // ACTOR 2: Product team drives these
    UserProfile getProfile(Long userId) {...}
    void updateBio(Long userId, String bio) {...}
    void uploadAvatar(Long userId, byte[] image) {...}

    // ACTOR 3: Compliance team drives these
    void logActivity(Long userId, String action) {...}
    UserActivityReport getActivityReport(Long userId) {...}
    void retainLogs(int years) {...}
}
// Any of the 3 teams changes this class.
// Other 2 teams: affected, must retest, may have conflicts.
```

```java
// GOOD: Split by actor. One class per actor.

// Actor: Security team
class AuthenticationService {
    User authenticate(String username, String password) {...}
    void logout(String sessionId) {...}
    boolean isSessionValid(String sessionId) {...}
}

// Actor: Product team
class UserProfileService {
    UserProfile getProfile(Long userId) {...}
    void updateBio(Long userId, String bio) {...}
    void uploadAvatar(Long userId, byte[] image) {...}
}

// Actor: Compliance team
class UserActivityLogger {
    void logActivity(Long userId, String action) {...}
    UserActivityReport getActivityReport(Long userId) {...}
    void retainLogs(int years) {...}
}

// Optional: Facade for callers that need one entry point
class UserFacade {
    @Autowired AuthenticationService authService;
    @Autowired UserProfileService profileService;
    @Autowired UserActivityLogger activityLogger;
    // Delegates: each method delegates to the right service
}
```

---

### ⚖️ SRP Granularity Guide

| Level | One responsibility = | Actor example |
|---|---|---|
| Method | One operation | N/A (method is atomic) |
| Class | One actor's requirements | One team or stakeholder group |
| Module | One business capability | One product domain |
| Microservice | One team owns it | One delivery team |
| API | One client type | One consumer profile |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SRP = one method per class | SRP is about ONE ACTOR (one reason to change), not one method. A class with 20 cohesive methods serving one actor perfectly satisfies SRP. A class with 2 methods serving two different actors violates SRP |
| SRP requires splitting everything into tiny classes | Splitting by actor produces classes with the RIGHT size: as large as needed to serve one actor's requirements, no larger. Sometimes that is 2 methods; sometimes it is 20 |
| Every class should have exactly one public method | This misreading leads to "method objects" - a class wrapping a single function. This is over-engineering (DPT-072). SRP does not require this |
| SRP is only about classes | SRP applies at every level of granularity: method, class, module, microservice. A microservice owned by two teams has two reasons to change and violates SRP at the service level |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ "One reason to change" = one ACTOR       │
│              │ whose requirements drive changes         │
├──────────────┼──────────────────────────────────────────┤
│ NOT: one     │ "One thing" is too vague. Use: "one      │
│ thing        │ actor" to test correctly.               │
├──────────────┼──────────────────────────────────────────┤
│ TEST         │ List all teams/stakeholders who would    │
│              │ ask for changes to this class.          │
│              │ Count > 1 → SRP violation               │
├──────────────┼──────────────────────────────────────────┤
│ FIX          │ Split by actor. One class per actor.     │
│              │ Use Facade if single entry point needed. │
├──────────────┼──────────────────────────────────────────┤
│ COHESION     │ SRP = high cohesion. Methods/data all   │
│              │ serve the same actor's purpose.         │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-075: SOLID - Open/Closed Principle  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. "One reason to change" = one ACTOR (stakeholder, team,
   user role) whose requirements drive changes to this
   class. Not "one method" or "one thing." Count actors,
   not methods.
2. SRP violation symptom: merge conflicts between unrelated
   teams modifying the same class. Multi-actor class =
   multi-team coupling = coordination overhead + unrelated
   breakage.
3. Fix: split by actor. Each class per actor. Use a Facade
   if callers need a single entry point. The Facade itself
   has one responsibility: delegation.

