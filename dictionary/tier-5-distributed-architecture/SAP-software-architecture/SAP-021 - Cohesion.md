---
id: SAP-040
layout: default
title: "Cohesion"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /software-architecture/cohesion/
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-044
used_by: 
related: SAP-048, SAP-010
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
---

# SAP-012 - Cohesion

⚡ TL;DR - Cohesion measures how strongly related and focused the elements within a module, class, or function are - high cohesion means everything inside belongs together and serves a unified purpose; low cohesion means the module is doing unrelated things.

---
id: SAP-012

### 🔥 The Problem This Solves

**THE GRAB-BAG MODULE PROBLEM:**
A `UtilityService` class with 47 methods: `formatDate()`, `validateEmail()`, `sendSlackAlert()`, `calculateTax()`, `resizeImage()`, `parseCSV()`, `generatePDF()`, `hashPassword()`. What does this class do? Everything and nothing. It has no unified purpose. Changes to date formatting and changes to PDF generation both modify this class - for completely unrelated reasons. Tests must mock every possible dependency. Every team adds methods here because there's no natural home for utility code.

**HIGH COHESION SOLUTION:**
`DateFormatter` with date formatting methods. `EmailValidator` with email validation. `AlertNotifier` with alerting. `TaxCalculator` with tax logic. Each class has a clear, single purpose. Each is small, understandable, and testable independently. The `UtilityService` is deleted - its functionality distributed to the classes it properly belongs in.

**EVOLUTION:** Cohesion was formalized by Larry Constantine and Edward Yourdon in "Structured Design" (1979) alongside coupling, establishing the cohesion-coupling dyad as the fundamental metrics of module quality. Constantine's original 7-level taxonomy (Coincidental → Functional) provided the vocabulary, but practitioners found the taxonomy hard to apply in practice. The rise of OOP (1990s) shifted focus from module-level to class-level cohesion, and Robert Martin's SRP (2000s) expressed functional cohesion as an OO design principle. The DDD movement (Evans, 2003) elevated cohesion to the strategic level: Bounded Contexts are cohesive at the domain knowledge level. Modern microservices practice treats service boundary cohesion as an architecture-level concern, where the question "should these two capabilities be in the same service?" is answered by cohesion analysis.

---
id: SAP-012

### 📘 Textbook Definition

Cohesion is a measure of how strongly related the responsibilities of a single module (class, function, package, or service) are. The concept was formalized by Larry Constantine and Edward Yourdon in "Structured Design" (1979). High cohesion means the module has a single, well-defined purpose and all its elements contribute to that purpose. Low cohesion means the module bundles unrelated responsibilities. Constantine and Yourdon defined a hierarchy of cohesion types from weakest to strongest: Coincidental → Logical → Temporal → Procedural → Communicational → Sequential → Functional (the ideal). High cohesion is a design goal: it correlates with understandability, reusability, testability, and maintainability.

---
id: SAP-012

### ⏱️ Understand It in 30 Seconds

**One line:**
High cohesion = "everything in this class belongs together." Low cohesion = "this class does unrelated things and has no clear purpose."

**One analogy:**

> A Swiss Army knife is low-cohesion: it combines a blade, corkscrew, scissors, screwdriver, and toothpick in one tool. Each tool works, but the combination has no unified purpose. A chef's knife is high-cohesion: it does one thing - cut food - and does it very well. The best tool for serious work is the specialized, high-cohesion one.

**One insight:**
The Single Responsibility Principle (SRP) is cohesion applied to classes. A class with high cohesion has one responsibility - one reason to change (SRP). Cohesion extends this thinking to all levels: functions, classes, modules, services. The principle is the same at every level: the more unified the purpose, the better.

---
id: SAP-012

### 🔩 First Principles Explanation

**COHESION LEVELS (weakest to strongest):**

```
┌──────────────────────────────────────────────────────────┐
│     COHESION HIERARCHY (Constantine & Yourdon)           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Coincidental (worst):                                │
│     Elements grouped arbitrarily (the "utils" class)    │
│     No relationship between elements                     │
│                                                          │
│  2. Logical:                                             │
│     Elements grouped because they do similar things     │
│     "All I/O operations in one class"                    │
│     Interface controlled by a type parameter            │
│                                                          │
│  3. Temporal:                                            │
│     Elements grouped because they run at same time      │
│     "Everything that runs at startup"                    │
│                                                          │
│  4. Procedural:                                          │
│     Elements follow a procedural sequence               │
│     "First validate, then save, then notify"             │
│                                                          │
│  5. Communicational:                                     │
│     Elements operate on the same data                   │
│     "All methods that use the Order object"              │
│                                                          │
│  6. Sequential:                                          │
│     Output of one element is input to next              │
│     Pipeline stages that process the same data          │
│                                                          │
│  7. Functional (best):                                   │
│     All elements contribute to a single, well-defined   │
│     task. One cohesive purpose.                          │
│     "Calculate the VAT for a UK B2C transaction"         │
└──────────────────────────────────────────────────────────┘
```

**COHESION METRICS:**

```
┌──────────────────────────────────────────────────────────┐
│         COHESION INDICATORS TO MEASURE                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Good (high cohesion):                                   │
│    - Class name clearly describes ONE concept            │
│    - All methods use most fields (LCOM low)              │
│    - Class has few dependencies (few imports)            │
│    - Class can be described in one sentence              │
│    - Methods share parameters and return values          │
│                                                          │
│  Bad (low cohesion):                                     │
│    - Class name contains "Manager", "Helper", "Utils"    │
│    - Methods use disjoint sets of fields                 │
│    - Class has many unrelated dependencies               │
│    - Class description needs "and" or "also"             │
│    - Methods don't call each other or share data         │
│                                                          │
│  LCOM (Lack of Cohesion in Methods):                     │
│    Metric measuring how many method pairs share fields   │
│    High LCOM = low cohesion = split the class           │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-012

### 🧪 Thought Experiment

**THE "AND" TEST FOR COHESION:**
Try to describe the purpose of a class in one sentence without using "and." If you can't, it likely has low cohesion.

- `UserService`: "Manages user registration, profile updates, password resets, email verification, session management, and audit logging." Six responsibilities. Low cohesion.
- `PasswordResetService`: "Handles the password reset flow for users." One responsibility. High cohesion.
- `EmailAddressValidator`: "Validates whether a string is a valid email address." One responsibility. High cohesion.

**THE SPLIT INDICATOR:**
When discussing a class, if you find yourself saying "the first half of the class does X and the second half does Y," that's a clear indication the class should be split into two high-cohesion classes.

---
id: SAP-012

### 🧠 Mental Model / Analogy

> Cohesion is the difference between a museum exhibition and a junk drawer. A museum exhibition on ancient Egypt has a unified theme: everything belongs together and tells a coherent story. A junk drawer has rubber bands, expired coupons, old batteries, and mystery keys - coincidentally grouped by location (the drawer) but not by meaning. High-cohesion code is the exhibition - every element contributes to the story. Low-cohesion code is the junk drawer - things ended up there for lack of a better place.

---
id: SAP-012

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Do the things in this class all belong together? High cohesion: yes, they all serve one purpose. Low cohesion: they're mixed together but don't really fit.

**Level 2 - How to improve it (junior):**
Signs of low cohesion: class has "Manager", "Handler", "Helper", "Processor", or "Utils" in its name; class has more than ~5-7 distinct fields; class has 20+ methods doing unrelated things; class tests require many unrelated mocks. Fix: identify sub-groups of methods that use the same fields or serve the same purpose. Extract each group into a separate class with a clear, domain-meaningful name. Rename the original class or delete it.

**Level 3 - Cohesion and coupling relationship (mid-level):**
High cohesion and low coupling are the two complementary design goals - and they reinforce each other. A highly cohesive class has a clear, focused interface: less for other classes to couple to. A class with low cohesion has a sprawling interface: more for callers to know about, more surface area for coupling. The design goal: high cohesion within modules, low coupling between modules. Constantine's law: a well-designed system maximizes cohesion within modules and minimizes coupling between modules. LCOM (Lack of Cohesion in Methods) is a code metric that detects cohesion violations: if a class's methods fall into two non-overlapping sets (set A uses fields 1-3, set B uses fields 4-6), the class should be split.

**Level 4 - Cohesion at service boundaries (senior/staff):**
In microservices, cohesion determines service boundaries. A highly cohesive service owns a single Bounded Context: all data and behavior related to "Orders" in one service, all data and behavior related to "Inventory" in another. Low cohesion in services appears as "orchestrator services" that span multiple domains, or as services that contain unrelated business rules because they were grouped by technical layer rather than business domain. The organizational manifestation: Conway's Law says services match team structures. Low-cohesion services often reflect low-cohesion team structures (platform teams owning cross-cutting concerns across multiple domains). High-cohesion services reflect stream-aligned teams (each team owns one business domain end-to-end).

---
id: SAP-012

### ⚙️ How It Works (Mechanism)

**Measuring cohesion with LCOM:**

```
┌──────────────────────────────────────────────────────────┐
│          LCOM - LACK OF COHESION IN METHODS              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  class UserService {                                     │
│    String username;  // field A                          │
│    String email;     // field B                          │
│    String address;   // field C                          │
│    String taxId;     // field D                          │
│                                                          │
│    updateUsername(username) { uses A }                   │
│    validateEmail(email) { uses B }                       │
│    formatAddress(addr) { uses C }                        │
│    calculateTax(income) { uses D }                       │
│  }                                                       │
│                                                          │
│  LCOM: 4 methods, 0 shared fields between any pair       │
│  = Maximum lack of cohesion                              │
│  Each method uses a disjoint field set                   │
│  Should be 4 separate classes                            │
│                                                          │
│  class OrderProcessor {                                  │
│    Order order;      // single field                     │
│                                                          │
│    validate() { uses order }                             │
│    calculateTotal() { uses order }                       │
│    applyDiscount() { uses order }                        │
│    submit() { uses order }                               │
│  }                                                       │
│                                                          │
│  LCOM: all methods share the same field                  │
│  = High cohesion                                         │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-012

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│      COHESION - BEFORE AND AFTER SPLIT                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  BEFORE: NotificationService (low cohesion)              │
│    sendEmail(to, subject, body)       uses: emailClient  │
│    sendSMS(to, message)               uses: smsClient    │
│    sendPushNotification(deviceId, msg) uses: fcmClient   │
│    logNotification(type, recipient)   uses: auditLog     │
│    getNotificationHistory(userId)     uses: db           │
│    formatEmailTemplate(template, vars) uses: (pure)      │
│                                                          │
│  AFTER: Six high-cohesion classes                        │
│    EmailSender: sendEmail + formatEmailTemplate          │
│    SmsSender: sendSMS                                    │
│    PushNotifier: sendPushNotification                    │
│    NotificationAuditLogger: logNotification              │
│    NotificationHistoryRepository: getNotificationHistory │
│    NotificationDispatcher: orchestrates the above        │
│                                                          │
│  Each class: single purpose, single reason to change     │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-012

### 💻 Code Example

```java
// LOW COHESION: Methods use disjoint field sets
public class OrderUtils {
    private final EmailClient emailClient;
    private final SMSClient smsClient;
    private final OrderRepository orderRepo;
    private final TaxService taxService;
    private final InventoryClient inventoryClient;

    // Uses: orderRepo, taxService
    public BigDecimal calculateOrderTotal(Order order) { ... }

    // Uses: emailClient
    public void sendOrderConfirmation(Order order) { ... }

    // Uses: smsClient
    public void sendShippingAlert(Order order) { ... }

    // Uses: inventoryClient
    public boolean checkStock(ProductId productId) { ... }
}

// ─────────────────────────────────────────────────────────

// HIGH COHESION: Each class focused on one purpose
public class OrderTotalCalculator {
    private final TaxService taxService;
    // All methods use taxService + work with Order financials
    public BigDecimal calculateTotal(Order order) { ... }
    public BigDecimal calculateTax(Order order) { ... }
    public BigDecimal calculateDiscount(Order order) { ... }
}

public class OrderNotificationService {
    private final EmailClient emailClient;
    private final SMSClient smsClient;
    // All methods relate to notifying customers about orders
    public void sendConfirmation(Order order) { ... }
    public void sendShippingUpdate(Order order) { ... }
}
```

---
id: SAP-012

### ⚖️ Comparison Table

| Cohesion level  | Description                            | Quality       |
| --------------- | -------------------------------------- | ------------- |
| Functional      | Single, well-defined task              | Best          |
| Sequential      | Elements pass data in sequence         | Good          |
| Communicational | Share the same data                    | Good          |
| Procedural      | Sequential steps, but not data-related | Average       |
| Temporal        | Execute at same time                   | Below average |
| Logical         | Similar things grouped by type         | Poor          |
| Coincidental    | No relationship                        | Worst         |

---
id: SAP-012

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                  |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Small class = high cohesion           | A tiny class can have low cohesion (two unrelated methods); a large class can have high cohesion (many methods, all serving one purpose) |
| High cohesion means one method        | Cohesion is about unity of purpose, not method count                                                                                     |
| Cohesion and coupling are independent | They are complementary - improving cohesion typically reduces coupling (focused classes have smaller interfaces)                         |
| "Utils" classes are acceptable        | They're a design smell - coincidental cohesion; the code belongs in focused domain classes                                               |

---
id: SAP-012

### 🚨 Failure Modes & Diagnosis

**God class - everything ends up in one place**

**Symptom:** One class (often named `*Service`, `*Manager`, `*Controller`) has hundreds of methods and grows continuously as every new feature adds to it.

**Root Cause:** Coincidental cohesion - the class became a catch-all.

**Fix:** Identify clusters of related methods using the field usage matrix. Each cluster is a candidate for a new class. Extract one at a time to avoid big-bang refactoring. Use the "and" test: if you can't describe the class without "and," split it.

---
id: SAP-012

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Things that change together should live together. The natural clustering of changes reveals the right boundaries. If two methods always change in the same commit, they belong in the same class. If they rarely change together, they may belong apart.

**Where else this pattern appears:**

- **Urban zoning:** A city district is cohesive when the buildings serve a unified purpose (residential, industrial, commercial). A mixed-use block where a chemical plant sits next to a kindergarten has low cohesion - changes to one (safety regulations for the plant) affect the other inappropriately.
- **Cookbooks:** A book about Italian cuisine is cohesive - all content relates to a single culinary tradition. An "Everything Food" book covering molecular gastronomy, Korean BBQ, French pastry, and vegan cooking has low cohesion - the knowledge doesn't integrate or reinforce.
- **Swiss Army Knife vs. specialist tools:** A surgeon's scalpel is highly cohesive - it does one thing perfectly. A Swiss Army Knife has low cohesion - many loosely related tools. Cohesion is not about how many things you include; it is about how well the included things form a unified whole.

---
id: SAP-012

### 💡 The Surprising Truth

The most powerful way to measure cohesion in practice is not to analyze the code - it is to analyze the git history. A module with high cohesion has commits that cluster: most commits change the same set of files together. A module with low cohesion shows scattered commits where changes to one method rarely require changes to other methods in the same class. This technique ("change coupling" or "logical coupling" analysis) was researched by Martin Fowler and Adam Tornhill ("Software Design X-Rays") and reveals real cohesion problems that static analysis misses. Tools like CodeScene analyze commit history to find classes where methods rarely change together - a reliable signal of low cohesion that should be refactored.

---
id: SAP-012

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-044 - SOLID Principles (SRP is the specific application of cohesion to class design; understanding SOLID gives the OO context in which cohesion is most commonly analyzed)

**Builds On This (learn these next):**

- SAP-048 - Coupling (the complementary metric; always optimize cohesion and coupling together - high cohesion within units, low coupling between units)
- SAP-010 - Connascence (formal framework that provides more precise vocabulary for cohesion/coupling analysis at the code level)

**Alternatives / Comparisons:**

- SAP-048 - Coupling (not an alternative but a complement; they are two sides of the same module quality coin: maximize cohesion, minimize coupling)
- SAP-010 - Connascence (subsumes cohesion; connascence types that appear within a single class are cohesion concerns; connascence types that span classes are coupling concerns)

---
id: SAP-012

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Degree to which elements within a module │
│              │ belong together and serve one purpose    │
├──────────────┼───────────────────────────────────────────┤
│ GOAL         │ HIGH cohesion within modules             │
│              │ LOW coupling between modules             │
├──────────────┼───────────────────────────────────────────┤
│ SMELL        │ "Utils", "Manager", "Helper" class names  │
│              │ "and" in the class description           │
├──────────────┼───────────────────────────────────────────┤
│ METRIC       │ LCOM - if methods use disjoint fields:   │
│              │ split the class                          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Museum exhibition vs junk drawer:        │
│              │  everything belongs together or it's junk"│
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-012

### 🧠 Think About This Before We Continue

**Q1.** You have a `CustomerService` with these methods: `registerCustomer()`, `updateCustomerAddress()`, `getCustomerOrders()`, `calculateCustomerLifetimeValue()`, `sendCustomerBirthdayEmail()`, `blockCustomerAccount()`. Using cohesion principles, identify which methods belong together, what the natural class splits are, and what you would name the resulting classes.

*Hint:* Research Constantine's cohesion types and specifically "Communicational cohesion" (methods that operate on the same data) vs "Sequential cohesion" (output of one is input to another) vs "Functional cohesion" (methods that together complete a single well-defined function). Natural splits: `CustomerRegistrationService` (registerCustomer, updateCustomerAddress); `CustomerAnalyticsService` (getCustomerOrders, calculateCustomerLifetimeValue); `CustomerNotificationService` (sendCustomerBirthdayEmail); `CustomerAccountService` (blockCustomerAccount). Alternatively: split by bounded context: identity management vs order history vs communications.

**Q2.** In microservices, how does cohesion guide service boundary decisions? Give an example where a low-cohesion service (spanning multiple business domains) causes operational pain, and describe how splitting it into high-cohesion services would solve that pain. What's the risk of splitting too aggressively (too-small, over-split services)?

*Hint:* Research the "chatty microservices" anti-pattern and specifically how it arises from over-splitting: if `OrderService` makes 10 synchronous calls to `ProductService`, `PricingService`, `TaxService`, `DiscountService`, `ShippingService` etc., all of which serve only `OrderService`, those services have low cohesion with each other but high coupling with `OrderService`. The fix: aggregate related operations that always change together into the same service boundary. Too small: nanoservices where each service has one endpoint; high operational overhead with no independence benefit. The heuristic: a cohesive service should be ownable by a single team with a single deployment cadence.

**Q3.** A developer uses the git history to find that `CustomerRepository.findById()` and `EmailTemplateService.renderWelcomeEmail()` are frequently modified in the same commits. According to cohesion theory, what does this suggest, and should these methods be in the same class? What other evidence would you gather before making a structural change?

*Hint:* Research the "change coupling" analysis technique from Adam Tornhill's "Software Design X-Rays" - specifically that logical coupling (files changed together frequently) is a signal of functional dependency, not necessarily of cohesion violation. Two methods that are frequently changed together in the same commit are "logically coupled" - they represent a hidden dependency. This COULD mean: (1) they should be in the same class (if they represent the same concept); OR (2) they should be decoupled with an event/interface (if they're in different bounded contexts but share a change driver). Gather evidence: WHY are they changed together? Is it a business rule that spans both? Is it a shared data structure? The fix depends on the cause.
