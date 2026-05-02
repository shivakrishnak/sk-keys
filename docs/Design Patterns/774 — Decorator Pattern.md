---
layout: default
title: "Decorator Pattern"
parent: "Design Patterns"
nav_order: 774
permalink: /design-patterns/decorator-pattern/
number: "774"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Composite Pattern, Composition over Inheritance"
used_by: "Java I/O streams, HTTP filters, Middleware chains, Logging wrappers"
tags: #intermediate, #design-patterns, #structural, #oop, #composition, #wrapping
---

# 774 — Decorator Pattern

`#intermediate` `#design-patterns` `#structural` `#oop` `#composition` `#wrapping`

⚡ TL;DR — **Decorator** dynamically adds behavior to an object by wrapping it — each decorator wraps the previous, forming a chain that adds functionality incrementally, while all layers implement the same interface so the client sees no difference.

| #774            | Category: Design Patterns                                                    | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Composite Pattern, Composition over Inheritance |                 |
| **Used by:**    | Java I/O streams, HTTP filters, Middleware chains, Logging wrappers          |                 |

---

### 📘 Textbook Definition

**Decorator** (GoF, 1994): a structural design pattern that attaches additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality. Structure: the decorator implements the same interface as the wrapped component, holds a reference to the component, and delegates to it while adding behavior before/after/around the delegation. Multiple decorators can be stacked; each layer adds behavior; the innermost layer is the concrete component. GoF intent: "Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality." Distinguished from: **Proxy** (controls access; same interface; typically single wrapper). **Composite** (tree of N children; treats group as single unit). **Adapter** (changes interface).

---

### 🟢 Simple Definition (Easy)

A coffee order at Starbucks. Start with plain coffee (base component). Add milk: wrap it in `MilkDecorator`. Add caramel: wrap in `CaramelDecorator`. Add vanilla: wrap in `VanillaDecorator`. Each topping adds cost to the coffee's price and adds its flavor description. The final object is `VanillaDecorator(CaramelDecorator(MilkDecorator(PlainCoffee)))`. Call `getCost()`: each layer adds its cost to the inner layer's cost. Stacking decorators = stacking toppings.

---

### 🔵 Simple Definition (Elaborated)

Java's `InputStream`: `new GZIPInputStream(new BufferedInputStream(new FileInputStream("data.gz")))`. Each wraps the previous: `FileInputStream` reads raw bytes from disk. `BufferedInputStream` wraps it — adds buffering (reads in 8KB chunks rather than byte by byte). `GZIPInputStream` wraps that — adds decompression. All implement `InputStream`. Code using the stream calls `read()` — it goes through the decompression layer → buffering layer → disk reads. Each decorator adds one responsibility without modifying the others.

---

### 🔩 First Principles Explanation

**How the wrapping chain works and why it's better than subclassing:**

```
WITHOUT DECORATOR — SUBCLASS EXPLOSION:

  Coffee: base
  MilkCoffee extends Coffee
  CaramelCoffee extends Coffee
  VanillaCoffee extends Coffee
  MilkCaramelCoffee extends Coffee
  MilkVanillaCoffee extends Coffee
  CaramelVanillaCoffee extends Coffee
  MilkCaramelVanillaCoffee extends Coffee

  3 toppings = 8 subclasses.
  10 toppings = 1024 subclasses (2^10). UNWORKABLE.

WITH DECORATOR — STACKABLE:

  // COMPONENT INTERFACE:
  interface Coffee {
      double getCost();
      String getDescription();
  }

  // CONCRETE COMPONENT (base):
  class PlainCoffee implements Coffee {
      public double getCost()          { return 1.00; }
      public String getDescription()   { return "Plain coffee"; }
  }

  // ABSTRACT DECORATOR (wraps a Coffee):
  abstract class CoffeeDecorator implements Coffee {
      protected final Coffee coffee;  // wraps any Coffee (including other decorators!)

      CoffeeDecorator(Coffee coffee) { this.coffee = coffee; }

      // Default: delegate to inner coffee:
      public double getCost()        { return coffee.getCost(); }
      public String getDescription() { return coffee.getDescription(); }
  }

  // CONCRETE DECORATORS:
  class MilkDecorator extends CoffeeDecorator {
      MilkDecorator(Coffee coffee) { super(coffee); }

      public double getCost()        { return super.getCost() + 0.30; }
      public String getDescription() { return super.getDescription() + ", milk"; }
  }

  class CaramelDecorator extends CoffeeDecorator {
      CaramelDecorator(Coffee coffee) { super(coffee); }

      public double getCost()        { return super.getCost() + 0.50; }
      public String getDescription() { return super.getDescription() + ", caramel"; }
  }

  // STACKING DECORATORS:
  Coffee order = new CaramelDecorator(
                   new MilkDecorator(
                     new PlainCoffee()   // inner: $1.00
                   )                     // +milk: $0.30
                 );                      // +caramel: $0.50

  order.getCost();           // 1.80
  order.getDescription();   // "Plain coffee, milk, caramel"

  // Can add same decorator multiple times:
  Coffee extraShots = new ShotDecorator(new ShotDecorator(new PlainCoffee()));

  // Can combine any combination:
  Coffee fancy = new VanillaDecorator(new CaramelDecorator(new MilkDecorator(new PlainCoffee())));

JAVA I/O — THE CANONICAL DECORATOR EXAMPLE:

  // FileInputStream: leaf — reads bytes from file
  // BufferedInputStream: decorator — adds buffering
  // DataInputStream: decorator — adds typed reads (readInt, readUTF)
  // GZIPInputStream: decorator — adds decompression
  // CipherInputStream: decorator — adds decryption

  // Stack however needed:
  InputStream in = new CipherInputStream(
                     new GZIPInputStream(
                       new BufferedInputStream(
                         new FileInputStream("data.encrypted.gz")
                       )
                     ),
                     cipher
                   );

  // All are InputStream. read() call flows through:
  // CipherInputStream.read() → decrypts → GZIPInputStream.read() → decompresses →
  // BufferedInputStream.read() → uses buffer / reads FileInputStream.read() → disk

SERVLET FILTER CHAIN — DECORATOR IN HTTP:

  // Each Filter wraps the next:
  // LoggingFilter → AuthFilter → RateLimitFilter → CompressionFilter → Servlet

  // Spring's OncePerRequestFilter is a Decorator:
  // Each filter: do before → chain.doFilter() (delegates to next) → do after

  class LoggingFilter extends OncePerRequestFilter {
      protected void doFilterInternal(request, response, FilterChain chain) {
          log.info("Request: {} {}", request.getMethod(), request.getUri());
          long start = System.currentTimeMillis();

          chain.doFilter(request, response);  // ← delegate to next in chain (inner)

          log.info("Response: {} in {}ms", response.getStatus(),
                   System.currentTimeMillis() - start);
      }
  }

DECORATOR ORDERING MATTERS:

  // Encryption THEN compression vs. compression THEN encryption:
  // Order 1: CipherOutputStream(GZIPOutputStream(FileOutputStream))
  //   → compress first, then encrypt compressed data (better compression)
  // Order 2: GZIPOutputStream(CipherOutputStream(FileOutputStream))
  //   → encrypt first, then try to compress encrypted data (encrypted data is random → poor compression)

  // Order of HTTP filters matters: auth before business logic, logging around everything.
  // Decorator order = pipeline order.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Decorator (subclassing for each combination):

- 10 optional features × combinations = hundreds/thousands of subclasses
- Adding a feature: add N subclasses (one per existing combination)

WITH Decorator:
→ Each feature = one decorator class. Combine any way at runtime: N + M classes, not N × M
→ Add a feature: one new decorator class. All existing combinations still work.

---

### 🧠 Mental Model / Analogy

> Russian nesting dolls (Matryoshka). The innermost doll is the real component. Each outer doll adds an "outer layer" — a new coat of paint, a new costume. When someone asks "what does this doll look like?" — the outermost doll answers, then passes the question inward. The response adds all layers. You can nest any number of dolls; each adds its visual contribution; all look like a Russian doll from the outside.

"Innermost doll" = concrete component (PlainCoffee, FileInputStream)
"Each outer doll" = one decorator (MilkDecorator, BufferedInputStream)
"All look like a doll" = all implement the same interface (Coffee, InputStream)
"Answer passes inward" = decorator calls super/inner.method()
"Nest any number of dolls" = stack any number of decorators

---

### ⚙️ How It Works (Mechanism)

```
DECORATOR CHAIN:

  Client → OuterDecorator.op()
               → calls inner.op() (before/after logic)
           MiddleDecorator.op()
               → calls inner.op() (before/after logic)
           ConcreteComponent.op()
               → actual work

  Result flows back up through each decorator layer.
  Each layer can transform result or add side effects.
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to add behavior to objects dynamically without subclassing for every combination
        │
        ▼
Decorator Pattern ◄──── (you are here)
(wraps component, same interface, adds behavior before/after delegation)
        │
        ├── Proxy: similar wrapping; different intent (access control, caching, lazy init)
        ├── Composite: tree of N children (vs Decorator: chain of 1 per layer)
        ├── Chain of Responsibility: chain handles requests; Decorator processes all
        └── Adapter: changes interface (vs Decorator: preserves and enhances interface)
```

---

### 💻 Code Example

```java
// HTTP response decorator — adding CORS + compression headers:

interface HttpResponse {
    int getStatus();
    String getBody();
    Map<String, String> getHeaders();
}

class SimpleHttpResponse implements HttpResponse {
    private final int status;
    private final String body;

    SimpleHttpResponse(int status, String body) {
        this.status = status;
        this.body = body;
    }
    public int getStatus()                  { return status; }
    public String getBody()                 { return body; }
    public Map<String, String> getHeaders() { return new HashMap<>(); }
}

// Abstract decorator:
abstract class ResponseDecorator implements HttpResponse {
    protected final HttpResponse inner;
    ResponseDecorator(HttpResponse inner) { this.inner = inner; }

    public int getStatus()    { return inner.getStatus(); }
    public String getBody()   { return inner.getBody(); }
    public Map<String, String> getHeaders() { return new HashMap<>(inner.getHeaders()); }
}

// Concrete decorators:
class CorsDecorator extends ResponseDecorator {
    CorsDecorator(HttpResponse inner) { super(inner); }

    public Map<String, String> getHeaders() {
        Map<String, String> headers = super.getHeaders();
        headers.put("Access-Control-Allow-Origin", "*");
        headers.put("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
        return headers;
    }
}

class CacheControlDecorator extends ResponseDecorator {
    private final int maxAgeSeconds;
    CacheControlDecorator(HttpResponse inner, int maxAgeSeconds) {
        super(inner);
        this.maxAgeSeconds = maxAgeSeconds;
    }

    public Map<String, String> getHeaders() {
        Map<String, String> headers = super.getHeaders();
        headers.put("Cache-Control", "max-age=" + maxAgeSeconds);
        return headers;
    }
}

// Stack decorators for the response:
HttpResponse response = new CacheControlDecorator(
    new CorsDecorator(
        new SimpleHttpResponse(200, "{\"users\": []}")
    ),
    3600  // 1 hour cache
);

// Client sees one HttpResponse:
response.getHeaders();  // → {Access-Control-Allow-Origin: *, Cache-Control: max-age=3600}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Decorator and Proxy are interchangeable                             | Both wrap a component implementing the same interface. Intent differs: Decorator adds behavior (enriches). Proxy controls access (lazy init, caching, security, remote). In practice: Spring AOP `@Transactional`, `@Cacheable` use Proxy (control access behavior). Java I/O streams use Decorator (add features). |
| Decorator must always delegate to inner — can't override completely | Decorator CAN override completely without delegation (though this defeats the purpose in most cases). What makes a Decorator is: same interface + holds inner component + TYPICALLY delegates with added behavior.                                                                                                  |
| Java annotations like @Transactional are Decorators                 | `@Transactional` is implemented via AOP proxy (Proxy pattern), not the Decorator pattern. AOP generates a proxy class that wraps the bean. Though structurally similar to Decorator, intent is access control / cross-cutting concern management — not feature addition.                                            |

---

### 🔥 Pitfalls in Production

**Identity problems: decorated object is not `==` to original:**

```java
// ANTI-PATTERN: Assuming decorated object is the same object:
Coffee plain = new PlainCoffee();
Coffee withMilk = new MilkDecorator(plain);

// withMilk is NOT plain — it's a wrapper around plain:
withMilk == plain;                        // false
withMilk instanceof PlainCoffee;          // false (it's a MilkDecorator)
withMilk.equals(plain);                   // depends on equals() implementation

// PROBLEM: code that stores reference and later does identity check:
Set<Coffee> knownOrders = new HashSet<>();
knownOrders.add(plain);
knownOrders.contains(withMilk);  // false — different object! Order "lost."

// FIX: either don't use identity for decorated objects,
// or implement equals()/hashCode() to unwrap inner for comparison,
// or store the final decorated reference from the start.

// ANOTHER PITFALL: too many decorator layers make debugging hard:
// withMilk.toString() might show:
// VanillaDecorator(CaramelDecorator(MilkDecorator(PlainCoffee(...))))
// Stack traces show decoration chain — can confuse novices.
// FIX: implement toString() in decorator to show meaningful description.
```

---

### 🔗 Related Keywords

- `Proxy Pattern` — same structure; different intent: access control vs behavior addition
- `Composite Pattern` — tree of N components; Decorator is a chain of 1 wrapping the next
- `Chain of Responsibility` — chain passes request; some may not handle; Decorator always processes
- `Java I/O` — canonical Decorator: InputStream, OutputStream wrapped layer by layer
- `Servlet Filter Chain` — HTTP-level Decorator: each filter wraps the next in the chain

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Wrap component in decorator layers.       │
│              │ Each layer: same interface + delegates    │
│              │ + adds behavior. Stack any combination.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Add responsibilities to objects at        │
│              │ runtime; many optional feature combos;   │
│              │ subclassing would cause class explosion   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ When order of decorators is hard to       │
│              │ reason about; when decorator identity    │
│              │ (==) causes subtle bugs; when simple     │
│              │ subclass is clearer                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Coffee toppings: stack milk, caramel,    │
│              │  vanilla — each adds cost and flavor;    │
│              │  any combination, any order."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Proxy Pattern → Composite Pattern →       │
│              │ Chain of Responsibility → Java I/O Streams│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP uses JDK dynamic proxies or CGLIB-based proxies for `@Transactional`, `@Cacheable`, `@Async`, etc. This creates a "proxy chain" around beans. Structurally, this looks like Decorator pattern. But Spring calls it "Proxy." What is the fundamental distinction that makes Spring AOP a proxy rather than a decorator? Consider: the purpose of `@Transactional` (manages resource access) vs. `BufferedInputStream` (adds feature to stream). When does the line blur between Decorator and Proxy?

**Q2.** Java `OutputStream` has a problem: `new GZIPOutputStream(new BufferedOutputStream(new FileOutputStream("out.gz")))`. If you forget to call `close()`, the GZIP footer might not be written, and `BufferedOutputStream` might not flush. In Java 7+, try-with-resources solves this. How do try-with-resources interact with Decorator chains? When you call `close()` on the outermost decorator, does it automatically close the inner ones? What is the contract that makes this work?
