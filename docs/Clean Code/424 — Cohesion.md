---
layout: default
title: "Cohesion"
parent: "Clean Code"
nav_order: 424
permalink: /clean-code/cohesion/
---
# 424 — Cohesion

`#cleancode` `#architecture` `#foundational`

⚡ TL;DR — How focused and related the responsibilities inside a single module are.

| #424 | Category: Clean Code | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SRP, Module Design | |
| **Used by:** | Coupling, Refactoring | |

---

### 📘 Textbook Definition

Cohesion is the degree to which the elements of a module (class, method, package) belong together — how logically related and focused they are on a single purpose or concept. High cohesion means all parts contribute directly to the module's single responsibility.

---

### 🟢 Simple Definition (Easy)

Cohesion is about **how well a module sticks to one job**. High cohesion = everything inside the class belongs together. Low cohesion = class does many unrelated things.

---

### 🔵 Simple Definition (Elaborated)

High cohesion means a class has a clear, single purpose. Every method and field directly supports that purpose. Low cohesion means the class juggles unrelated responsibilities — it becomes hard to understand, test, and change. Cohesion and coupling are the two fundamental dimensions of module quality. They work together: higher cohesion naturally leads to lower coupling.

---

### 🔩 First Principles Explanation

**The core problem:**
Classes that grew over time by adding unrelated responsibilities become hard to understand and maintain.

**The insight:**
> "A module should have one reason to change" — if everything inside serves one purpose, changes stay local.

```
Low cohesion:
  UserService { login(), sendEmail(), generateReport(), resizeImage() }

High cohesion:
  UserService  { login(), logout(), changePassword() }
  EmailService { sendEmail(), sendBulkEmail() }
  ReportService { generateUserReport(), exportCSV() }
```

---

### ❓ Why Does This Exist (Why Before What)

Without cohesion, changes to one feature accidentally break unrelated features in the same class. Tests become enormous. Reuse becomes impossible — you cannot take just the email logic without pulling in the user logic.

---

### 🧠 Mental Model / Analogy

> Think of a Swiss Army knife vs a chef's knife. The chef's knife does one thing perfectly — that's high cohesion. The Swiss Army knife does many things adequately — that's low cohesion. In software, the chef's knife is easier to maintain, sharpen, and reason about.

---

### ⚙️ How It Works (Mechanism)

Types of cohesion (weakest → strongest):

```
Coincidental   — elements grouped randomly (worst)
Logical        — elements do similar things (e.g., all I/O operations)
Temporal       — elements run at the same time (e.g., startup initializers)
Procedural     — elements follow a sequence
Communicational— elements work on the same data
Sequential     — output of one feeds the next
Functional     — all elements contribute to a single task (IDEAL)
```

---

### 🔄 How It Connects (Mini-Map)

```
         [SRP]
            ↓
[Low Cohesion] --> [Refactor] --> [High Cohesion]
                                       ↑
                                  [Coupling ↓]
```

---

### 💻 Code Example

```java
// LOW cohesion — class does too many unrelated things
class UserManager {
    void createUser(String name) { /* ... */ }
    void sendWelcomeEmail(String email) { /* ... */ }   // email concern
    void generateUserReport() { /* ... */ }             // reporting concern
    byte[] resizeProfilePicture(byte[] img) { /* ... */ } // image concern
}

// HIGH cohesion — each class has one focused purpose
class UserService {
    void createUser(String name) { /* ... */ }
    void deactivateUser(long id) { /* ... */ }
    Optional<User> findById(long id) { /* ... */ }
}

class UserEmailService {
    void sendWelcomeEmail(String email) { /* ... */ }
    void sendPasswordReset(String email) { /* ... */ }
}
```

---

### 🔁 Flow / Lifecycle

```
1. Class starts with one responsibility
        ↓
2. Features get added to the same class (convenience)
        ↓
3. Class becomes a "god class" with low cohesion
        ↓
4. Refactor: extract responsibilities into focused classes
        ↓
5. High cohesion restored — each class has a clear purpose
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| More methods = better cohesion | Fewer, focused methods = higher cohesion |
| Cohesion is about class size | Cohesion is about relatedness of members, not size |
| High cohesion means small classes | A class can be large and still highly cohesive |
| It only applies to classes | Cohesion applies at method, class, and package level |

---

### 🔥 Pitfalls in Production

**Pitfall 1: God Classes**
Gradually adding methods to an existing class is the most common cause of low cohesion. A class that does "everything" is the hardest to test and change.
Fix: identify distinct responsibilities and extract them into separate, focused classes.

**Pitfall 2: Utility Classes**
A class named `Utils`, `Helper`, or `Manager` with no coherent theme is almost always low cohesion.
Fix: split into domain-specific helpers (e.g., `DateUtils`, `StringValidator`).

**Pitfall 3: Over-splitting**
Creating a new class for every single method overcorrects. A 1-method class has no cohesion to measure.
Fix: balance — group things that change together.

---

### 🔗 Related Keywords

- **SRP (Single Responsibility Principle)** — formal principle that enforces high cohesion
- **Coupling** — the opposite dimension; reduce both for clean modules
- **Refactoring** — the activity of improving cohesion without changing behavior
- **God Class** — anti-pattern resulting from low cohesion
- **Package Design** — cohesion applies at higher structural levels too

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Everything inside a module belongs together   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Designing or reviewing class responsibilities  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't over-split — tiny 1-liner classes hurt  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Cohesion = how much a module sticks to one   │
│              │  single, clear purpose"                        │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Coupling → SRP → Refactoring                  │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Can a class have high cohesion but also high coupling? What would that look like?  
**Q2.** What is the difference between functional cohesion and sequential cohesion?  
**Q3.** How does package-level cohesion differ from class-level cohesion?

