---
layout: default
title: "Builder Pattern"
parent: "Design Patterns"
nav_order: 768
permalink: /design-patterns/builder-pattern/
number: "768"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Factory Method Pattern"
used_by: "Complex object construction, Fluent APIs, Test fixtures, Immutable objects"
tags: #intermediate, #design-patterns, #creational, #fluent-api, #oop
---

# 768 — Builder Pattern

`#intermediate` `#design-patterns` `#creational` `#fluent-api` `#oop`

⚡ TL;DR — **Builder** separates the construction of a complex object from its representation — using a step-by-step building process with a fluent API, avoiding the "telescoping constructor" anti-pattern where a class has constructors with every possible combination of optional parameters.

| #768 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Factory Method Pattern | |
| **Used by:** | Complex object construction, Fluent APIs, Test fixtures, Immutable objects | |

---

### 📘 Textbook Definition

**Builder** (GoF, 1994): a creational design pattern that separates the construction of a complex object from its representation so that the same construction process can create different representations. The Builder encapsulates the object's construction logic, providing a step-by-step interface; a Director (optional) controls the construction sequence; the final object is returned by `build()`. Modern Java usage (Effective Java, Bloch — Item 2): Builder is used primarily to address the "telescoping constructor" problem — a class with many optional parameters becomes unreadable and error-prone. The Builder provides named parameter semantics in Java (which lacks named parameters). Key benefit: optional parameters, immutable objects (build() creates the final immutable instance), readable construction.

---

### 🟢 Simple Definition (Easy)

Ordering a custom sandwich. You tell the counter: "Start with sourdough. Add turkey. Add swiss cheese. Add lettuce. No tomato. Add mustard. Done." Each step is explicit, named, and optional. Compare: a `Sandwich(String bread, String meat, String cheese, boolean lettuce, boolean tomato, String condiment)` constructor — 6-parameter call where position matters, and you have to remember which boolean is lettuce and which is tomato.

---

### 🔵 Simple Definition (Elaborated)

`Email.builder().to("user@example.com").subject("Hello").body("...").cc("mgr@example.com").build()` — each method names what it's setting. All optional except `to`. Without Builder: `new Email("user@example.com", "Hello", "...", null, "mgr@example.com", null, false, Priority.NORMAL)` — 8 parameters, all positional. Which null is bcc? What does `false` mean? Builder solves both the readability problem and the optional parameter explosion.

---

### 🔩 First Principles Explanation

**Telescoping constructor problem and how Builder solves it:**

```
TELESCOPING CONSTRUCTOR PROBLEM:

  class Pizza {
      Pizza(Size size) { ... }
      Pizza(Size size, Crust crust) { ... }
      Pizza(Size size, Crust crust, boolean extraCheese) { ... }
      Pizza(Size size, Crust crust, boolean extraCheese, List<Topping> toppings) { ... }
      Pizza(Size size, Crust crust, boolean extraCheese, List<Topping> toppings, boolean extraSauce) { ... }
  }
  
  new Pizza(LARGE, THIN, true, List.of(PEPPERONI, MUSHROOM), false)
  //         ↑ size ↑ crust ↑ extra cheese ↑ toppings              ↑ extra sauce?
  // What does the last false mean? Hard to read. Easy to swap booleans.
  
JAVABEAN ALTERNATIVE (also bad — mutable, broken invariants):

  Pizza pizza = new Pizza();
  pizza.setSize(LARGE);
  pizza.setCrust(THIN);
  pizza.setExtraCheese(true);
  pizza.setToppings(List.of(PEPPERONI));
  pizza.bake();  // What if setSize was never called? Inconsistent object.
  // JavaBean: object can be in invalid state during construction.
  
BUILDER SOLUTION:

  // BUILD PROCESS:
  Pizza pizza = Pizza.builder()
      .size(LARGE)                          // required
      .crust(THIN)                          // optional, has default
      .extraCheese(true)                    // optional
      .toppings(PEPPERONI, MUSHROOM)        // optional, varargs
      .build();                             // creates final, IMMUTABLE pizza
      
  // BUILDER IMPLEMENTATION:
  public class Pizza {
      private final Size size;            // final — immutable after build
      private final Crust crust;
      private final boolean extraCheese;
      private final List<Topping> toppings;
      
      private Pizza(Builder b) {          // private constructor — only Builder can create
          this.size        = b.size;
          this.crust       = b.crust != null ? b.crust : Crust.REGULAR;
          this.extraCheese = b.extraCheese;
          this.toppings    = List.copyOf(b.toppings);  // defensive copy
      }
      
      public static Builder builder() { return new Builder(); }
      
      public static class Builder {
          private Size size;                            // required
          private Crust crust;                          // optional
          private boolean extraCheese = false;          // optional, default
          private List<Topping> toppings = new ArrayList<>();
          
          public Builder size(Size size) {
              this.size = Objects.requireNonNull(size);
              return this;  // fluent: returns this for chaining
          }
          
          public Builder crust(Crust crust) { this.crust = crust; return this; }
          public Builder extraCheese(boolean extra) { this.extraCheese = extra; return this; }
          public Builder toppings(Topping... t) { this.toppings.addAll(Arrays.asList(t)); return this; }
          
          public Pizza build() {
              if (size == null) throw new IllegalStateException("size is required");
              return new Pizza(this);
          }
      }
  }
  
LOMBOK @Builder (eliminates boilerplate):

  @Builder
  @Value  // @Value = @Getter + @FieldDefaults(final) + constructor + equals/hashCode
  public class Email {
      @NonNull String to;
      @NonNull String subject;
      @Builder.Default String from = "noreply@example.com";
      String body;
      String cc;
      String bcc;
  }
  
  // Usage:
  Email email = Email.builder()
      .to("user@example.com")
      .subject("Welcome")
      .body("Hello!")
      .build();
  
BUILDER IN TESTS (test data builder / object mother pattern):

  // Test data builders make tests readable:
  Order order = OrderBuilder.anOrder()
      .withCustomer(CustomerBuilder.aPremiumCustomer().build())
      .withItems(3)
      .withTotal(Money.of(200, USD))
      .withStatus(PENDING)
      .build();
      
  // Compare: new Order(new Customer("id1", "John", PREMIUM), items, Money.of(200, USD), PENDING)
  // Builder: reads like a specification, not a data dump.
  
DIRECTOR PATTERN (GoF original — less common in modern Java):

  // Director controls the sequence of builder calls:
  class PizzaDirector {
      Pizza buildMargarita(Pizza.Builder builder) {
          return builder.size(MEDIUM).crust(THIN).build();
      }
      Pizza buildPepperoniSpecial(Pizza.Builder builder) {
          return builder.size(LARGE).crust(THICK).extraCheese(true).toppings(PEPPERONI).build();
      }
  }
  // Director encapsulates "recipes" (common build sequences).
  // Less needed in Java because the builder API already reads like instructions.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Builder (telescoping constructors):
- `new Email("to@", "from@", "subject", "body", null, null, false, Priority.NORMAL)` — 8 positional params, unreadable, error-prone
- Objects with optional parameters require N! constructor combinations

WITH Builder:
→ `Email.builder().to("to@").subject("subject").build()` — readable, named, optional params handled
→ `build()` validates and creates an immutable object — no partially-constructed invalid state

---

### 🧠 Mental Model / Analogy

> A custom car order form. You fill in: model (required), color (optional, default: white), sunroof (optional), sport package (optional), interior (optional: leather/fabric). Each field is named — you can't accidentally put "sport package" in the "interior" field. The form validates: model must be filled. Then submits (build()). The car (immutable product) is created from the completed order form (builder state).

"Order form" = Builder (accumulates parameters step by step)
"Each named field" = named builder methods (no positional confusion)
"Model = required" = validation in build()
"Submit the form → car built" = build() creates the immutable product
"Can't change the car after delivery" = final fields in the built object

---

### ⚙️ How It Works (Mechanism)

```
BUILDER CHAIN:

  Builder.builder()      → returns new Builder()
         .field1(val1)   → sets field, returns this
         .field2(val2)   → sets field, returns this
         .build()        → validates + constructs immutable product
         
  INVARIANT CHECK IN build():
    if (required == null) throw IllegalStateException
    if (field1 > field2) throw IllegalArgumentException
    return new Product(this);  // private Product constructor takes Builder
```

---

### 🔄 How It Connects (Mini-Map)

```
Complex object with many optional parameters (telescoping constructors)
        │
        ▼ (step-by-step named construction)
Builder Pattern ◄──── (you are here)
(separate construction from representation; fluent, named, validated)
        │
        ├── Factory Method: Factory Method creates WHICH type; Builder creates HOW it's built
        ├── Immutable Objects: Builder enables constructing immutable objects step-by-step
        ├── Fluent API: Builder is the canonical fluent API use case
        └── Test Data Builder: Builder pattern in test code for readable test fixtures
```

---

### 💻 Code Example

```java
// Builder for an HTTP request (many optional parameters):
public class HttpRequest {
    private final String url;           // required
    private final HttpMethod method;    // required
    private final Map<String, String> headers;
    private final String body;
    private final Duration timeout;
    
    private HttpRequest(Builder b) {
        this.url     = b.url;
        this.method  = b.method;
        this.headers = Map.copyOf(b.headers);
        this.body    = b.body;
        this.timeout = b.timeout != null ? b.timeout : Duration.ofSeconds(30);
    }
    
    public static Builder builder(String url, HttpMethod method) {
        return new Builder(url, method);  // required params in factory method
    }
    
    public static class Builder {
        private final String url;
        private final HttpMethod method;
        private final Map<String, String> headers = new LinkedHashMap<>();
        private String body;
        private Duration timeout;
        
        private Builder(String url, HttpMethod method) {
            this.url = Objects.requireNonNull(url, "url required");
            this.method = Objects.requireNonNull(method, "method required");
        }
        
        public Builder header(String key, String value) {
            this.headers.put(key, value); return this;
        }
        public Builder body(String body) { this.body = body; return this; }
        public Builder timeout(Duration t) { this.timeout = t; return this; }
        
        public HttpRequest build() { return new HttpRequest(this); }
    }
}

// Usage — readable, named, self-documenting:
HttpRequest req = HttpRequest.builder("https://api.example.com/orders", POST)
    .header("Authorization", "Bearer " + token)
    .header("Content-Type", "application/json")
    .body(orderJson)
    .timeout(Duration.ofSeconds(5))
    .build();
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Builder Pattern is always needed for complex objects | Builder is best when: (1) many optional parameters, (2) immutability desired, (3) readability matters. For objects with 2-3 required parameters: a simple constructor is cleaner. YAGNI: don't add a Builder until the telescoping constructor problem actually appears |
| Builder and Factory Method are the same | Different problems: Factory Method decides WHICH type to create (what class). Builder decides HOW to create it (what parameters, what configuration). They can be combined: Factory Method returns a Builder, and Builder constructs the product |
| Builder breaks immutability because builder is mutable | The BUILDER is mutable during construction — that's the point. The PRODUCT (what build() returns) is immutable. The mutable builder is a temporary construction helper. The final product should have final fields and no setters |

---

### 🔥 Pitfalls in Production

**Required parameter validation deferred too late:**

```java
// ANTI-PATTERN: No validation in build() — invalid object created silently:
HttpRequest req = HttpRequest.builder()
    .body(json)
    .build();
// Forgot to set url! build() creates object with null url.
// Fails with NullPointerException when the request is actually sent.

// FIX: Validate required fields in build():
public HttpRequest build() {
    if (url == null)    throw new IllegalStateException("url is required");
    if (method == null) throw new IllegalStateException("method is required");
    if (method.requiresBody() && body == null)
        throw new IllegalStateException(method + " requires a body");
    return new HttpRequest(this);
}

// EVEN BETTER: Require mandatory params in builder constructor (compile-time enforcement):
public static Builder builder(String url, HttpMethod method) {
    // null check here — constructor fails fast:
    return new Builder(
        Objects.requireNonNull(url, "url required"),
        Objects.requireNonNull(method, "method required")
    );
}
// Can't forget url or method — won't compile without them in the factory call.
```

---

### 🔗 Related Keywords

- `Factory Method` — decides WHICH type to create; Builder decides HOW to build it
- `Immutable Objects` — Builder is the idiomatic way to construct immutable objects with optional fields
- `Lombok @Builder` — annotation that generates Builder boilerplate automatically
- `Fluent API` — Builder is the canonical fluent API design pattern
- `Test Data Builder` — Builder pattern applied to test fixtures for readable tests

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Step-by-step named construction of complex│
│              │ objects. Solves telescoping constructors. │
│              │ build() validates + returns immutable obj. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 4+ optional parameters; need immutability;│
│              │ readability matters; test fixtures        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple objects with 1-3 required params;  │
│              │ mutable objects where setters are fine;  │
│              │ YAGNI until telescoping constructor occurs│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Custom sandwich order form: each topping │
│              │  named, all optional except bread,       │
│              │  submitted to build the sandwich."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Factory Method → Immutable Objects →      │
│              │ Lombok @Builder → Test Data Builder       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `Query` object needs to be built from many optional parts: table, selected columns, WHERE clauses, ORDER BY, LIMIT, OFFSET, JOIN clauses. Using Builder: `Query.builder().from("orders").select("id", "total").where("status = 'PENDING'").orderBy("created_at DESC").limit(10).build()`. How does the Builder validate that the resulting SQL query is valid (e.g., can't have OFFSET without LIMIT)? Where does this validation live — in the builder methods, or in `build()`?

**Q2.** Lombok's `@Builder` generates the Builder automatically. But it also generates `@Builder.toBuilder()` — a method that creates a Builder pre-populated from an existing object's values, allowing you to create a modified copy: `existingEmail.toBuilder().body("new body").build()`. This is useful for immutable objects. How does this compare to using `withXxx()` methods (records/wither pattern) for creating modified copies? When would you prefer `toBuilder()` over `withXxx()` methods?
