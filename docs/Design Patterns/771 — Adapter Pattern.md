---
layout: default
title: "Adapter Pattern"
parent: "Design Patterns"
nav_order: 771
permalink: /design-patterns/adapter-pattern/
number: "771"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, SOLID Principles, Interface Segregation"
used_by: "Legacy integration, Third-party libraries, API compatibility, Wrapping"
tags: #intermediate, #design-patterns, #structural, #oop, #integration
---

# 771 — Adapter Pattern

`#intermediate` `#design-patterns` `#structural` `#oop` `#integration`

⚡ TL;DR — **Adapter** converts the interface of a class into another interface that clients expect — like a travel plug adapter that lets a US plug work in a European socket, bridging incompatible interfaces without modifying either the client or the adaptee.

| #771 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, SOLID Principles, Interface Segregation | |
| **Used by:** | Legacy integration, Third-party libraries, API compatibility, Wrapping | |

---

### 📘 Textbook Definition

**Adapter** (GoF, 1994): a structural design pattern that converts the interface of a class into another interface that clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces. Also known as "Wrapper." Two variants: (1) **Object Adapter** — uses composition (holds a reference to the adaptee); (2) **Class Adapter** — uses multiple inheritance (not common in Java, which doesn't support it for classes; possible with interfaces). GoF intent: "Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces." Distinguished from: **Facade** (simplifies a complex subsystem's interface — doesn't adapt an existing one); **Decorator** (adds behavior, same interface); **Bridge** (separates abstraction/implementation by design, not for compatibility).

---

### 🟢 Simple Definition (Easy)

A UK-to-EU plug adapter. Your UK laptop charger has a UK plug. European sockets accept EU plugs. The adapter sits between them — UK plug goes in one side, EU socket connection on the other. You don't modify your charger (the client). You don't modify the European socket (the target). The adapter translates between them. In code: you don't modify the legacy class or the new interface your code expects. The adapter wraps the legacy class and presents the expected interface.

---

### 🔵 Simple Definition (Elaborated)

You have a new `Shape` interface with `draw(int x1, int y1, int x2, int y2)`. You have a legacy `LegacyRectangle` class with `display(int x, int y, int w, int h)`. You can't change `LegacyRectangle` (third-party library). You can't change your new code that uses `Shape`. Solution: `LegacyRectangleAdapter implements Shape` — wraps `LegacyRectangle` and translates `draw(x1, y1, x2, y2)` into `legacyRect.display(x1, y1, x2-x1, y2-y1)`. Adapter translates coordinate semantics between the two interfaces.

---

### 🔩 First Principles Explanation

**Object Adapter vs Class Adapter and how translation works:**

```
THE PROBLEM:

  // TARGET interface — what client expects:
  interface MediaPlayer {
      void play(String audioType, String fileName);
  }
  
  // CLIENT code uses MediaPlayer:
  class AudioPlayer {
      void playMusic(MediaPlayer player, String file) {
          player.play("mp3", file);
      }
  }
  
  // ADAPTEE — third-party library with incompatible interface:
  class AdvancedMediaPlayer {
      void playVlc(String fileName) { ... }   // VLC files only
      void playMp4(String fileName) { ... }   // MP4 files only
  }
  
  // Can't use AdvancedMediaPlayer as MediaPlayer — different interface!
  // Can't modify AdvancedMediaPlayer (third-party library).
  
OBJECT ADAPTER SOLUTION (composition):

  class MediaAdapter implements MediaPlayer {
      private final AdvancedMediaPlayer advanced;  // wraps the adaptee
      
      MediaAdapter(String audioType) {
          // Select which adaptee implementation to wrap:
          this.advanced = new AdvancedMediaPlayer();
      }
      
      @Override
      public void play(String audioType, String fileName) {
          // TRANSLATE: MediaPlayer.play() → AdvancedMediaPlayer.playVlc/playMp4()
          if ("vlc".equalsIgnoreCase(audioType)) {
              advanced.playVlc(fileName);     // translate call
          } else if ("mp4".equalsIgnoreCase(audioType)) {
              advanced.playMp4(fileName);     // translate call
          }
      }
  }
  
  // Usage:
  MediaPlayer player = new MediaAdapter("vlc");
  player.play("vlc", "movie.vlc");  // works! adapter translates.
  
COORDINATE TRANSLATION ADAPTER:

  // Target interface — new system uses two-corner coordinates:
  interface Shape {
      void draw(int x1, int y1, int x2, int y2);  // (top-left, bottom-right)
  }
  
  // Adaptee — legacy system uses origin + dimensions:
  class LegacyRectangle {
      void display(int x, int y, int width, int height) { ... }
  }
  
  // Adapter — translates coordinate systems:
  class LegacyRectangleAdapter implements Shape {
      private final LegacyRectangle legacy;
      
      LegacyRectangleAdapter(LegacyRectangle legacy) {
          this.legacy = legacy;
      }
      
      @Override
      public void draw(int x1, int y1, int x2, int y2) {
          // Translate: (x1,y1,x2,y2) → (x, y, width, height)
          int x      = x1;
          int y      = y1;
          int width  = x2 - x1;    // translation logic
          int height = y2 - y1;
          legacy.display(x, y, width, height);
      }
  }
  
JAVA CLASS ADAPTER (interface-only — since Java has no multi-class inheritance):

  // Instead of holding a reference to adaptee, IMPLEMENT the adaptee's interface:
  // Useful when adaptee is an interface (e.g., java.util.Iterator vs legacy Enumeration)
  
  class IteratorToEnumerationAdapter<T> implements Enumeration<T> {
      private final Iterator<T> iterator;
      
      IteratorToEnumerationAdapter(Iterator<T> iterator) { this.iterator = iterator; }
      
      @Override public boolean hasMoreElements() { return iterator.hasNext(); }
      @Override public T nextElement()           { return iterator.next(); }
  }
  
SPRING ADAPTER EXAMPLES:

  // Spring's HandlerAdapter — adapts different controller types to the same handler invocation:
  // Controller implements interface → HandlerAdapter bridges DispatcherServlet and the controller.
  
  // Spring's HttpMessageConverter — adapts Java objects to/from HTTP request/response bodies:
  // Converts Object → JSON (Jackson), Object → XML, etc.
  // All implement HttpMessageConverter<T> — same interface — different serialization logic.
  
ADAPTER vs FACADE vs DECORATOR:

  Adapter:    "I have this interface, I need that interface." Translates incompatible interfaces.
              Wraps ONE class. Interface CHANGES.
              
  Facade:     "This subsystem is complex. I want a simpler interface to it."
              Wraps MULTIPLE classes. Simplifies (not translates).
              
  Decorator:  "I want to add behavior to this object."
              Same interface as wrapped object. ENHANCES without changing interface.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Adapter:
- Can't use third-party / legacy class — incompatible interface
- Must modify legacy code (risky) or duplicate it (violates DRY)

WITH Adapter:
→ Wrap legacy/third-party class in adapter; client uses target interface — no modification to either
→ Open for new adapters (support new adaptees); closed to modification (client code unchanged)

---

### 🧠 Mental Model / Analogy

> A foreign language interpreter. You speak English. The expert witness speaks French only. The interpreter (adapter) sits between you and the witness. When you ask "What did you see?" (English), the interpreter translates to French for the witness, gets the French answer, translates back to English for you. Neither you nor the witness changes — the interpreter bridges the incompatible communication interfaces.

"You (English)" = client code using target interface
"Expert witness (French only)" = adaptee (third-party/legacy class)
"Interpreter" = adapter
"Translates English → French → English" = adapter's translation logic
"Neither you nor witness changes" = neither client nor adaptee is modified

---

### ⚙️ How It Works (Mechanism)

```
ADAPTER STRUCTURE (Object Adapter):

  «interface»            «concrete class»
  Target                 Adaptee
  ────────               ────────
  +request()             +specificRequest()
      ▲                       ▲
      │                       │ (holds reference)
  Adapter ──────────────────── 
  +request()
      → adaptee.specificRequest()  (translation)
      
  Client → Target interface → Adapter → Adaptee
```

---

### 🔄 How It Connects (Mini-Map)

```
Incompatible interface between client code and existing class
        │
        ▼
Adapter Pattern ◄──── (you are here)
(wraps adaptee; presents target interface; translates calls)
        │
        ├── Facade: simplifies complex subsystem (doesn't adapt one interface to another)
        ├── Decorator: adds behavior with same interface (doesn't translate interface)
        ├── Bridge: structural separation by design (not for post-hoc compatibility)
        └── Proxy: same interface, controls access (not interface translation)
```

---

### 💻 Code Example

```java
// Adapting a legacy payment processor to a modern payment interface:

// TARGET interface (what our system expects):
interface PaymentGateway {
    PaymentResult charge(String customerId, BigDecimal amount, Currency currency);
}

// ADAPTEE — legacy payment system with completely different interface:
class LegacyPaymentSystem {
    String processPayment(int merchantId, double amountInCents, String currencyCode, String customer) { ... }
    // Returns: "SUCCESS:txn123" or "FAIL:INSUFFICIENT_FUNDS"
}

// ADAPTER:
class LegacyPaymentAdapter implements PaymentGateway {
    private final LegacyPaymentSystem legacy;
    private final int merchantId;
    
    LegacyPaymentAdapter(LegacyPaymentSystem legacy, int merchantId) {
        this.legacy = legacy;
        this.merchantId = merchantId;
    }
    
    @Override
    public PaymentResult charge(String customerId, BigDecimal amount, Currency currency) {
        // TRANSLATE 1: BigDecimal → double in cents
        double cents = amount.multiply(BigDecimal.valueOf(100)).doubleValue();
        
        // TRANSLATE 2: Currency → String code
        String currencyCode = currency.getCurrencyCode();
        
        // DELEGATE to adaptee:
        String response = legacy.processPayment(merchantId, cents, currencyCode, customerId);
        
        // TRANSLATE 3: legacy "SUCCESS:txn123" → PaymentResult object
        if (response.startsWith("SUCCESS:")) {
            return PaymentResult.success(response.substring(8));  // extract txnId
        } else {
            String error = response.substring(5);  // strip "FAIL:"
            return PaymentResult.failed(error);
        }
    }
}

// Client code uses PaymentGateway — never knows about LegacyPaymentSystem:
PaymentGateway gateway = new LegacyPaymentAdapter(legacySystem, MERCHANT_ID);
PaymentResult result = gateway.charge("cust-123", new BigDecimal("49.99"), USD);
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Adapter and Facade are the same thing | Key difference — intent and scope: Adapter makes an INCOMPATIBLE interface match an EXPECTED interface (translation). Facade SIMPLIFIES a complex subsystem with a new, simpler interface (abstraction). Adapter doesn't simplify — it translates. Facade doesn't translate — it simplifies. |
| You can only adapt one class at a time | An adapter can wrap multiple adaptee classes internally if needed. However, typically an adapter targets one specific incompatible class or interface. If you're wrapping multiple subsystem classes into one interface, that's leaning toward a Facade. |
| Adapter always requires creating a new class | In languages with first-class functions (or Java lambdas), adapter can be achieved with a lambda if the target interface is functional: `Shape shape = (x1, y1, x2, y2) -> legacyRect.display(x1, y1, x2-x1, y2-y1);` — no new class needed. |

---

### 🔥 Pitfalls in Production

**Adapter hiding semantic mismatch (translating call but losing meaning):**

```java
// ANTI-PATTERN: Adapter glosses over a semantic difference:
// TemperatureLogger wants Celsius; LegacyThermometer returns Fahrenheit:
class ThermometerAdapter implements TemperatureLogger {
    private final LegacyThermometer thermometer;
    
    // BAD: "adapts" by just calling legacy — no unit conversion:
    public double getTemperature() {
        return thermometer.readFahrenheit();  // Returns 98.6°F — passed as if it's °C!
    }
}
// 98.6 passed to Celsius logger → catastrophically wrong.

// FIX: Adapter MUST translate semantics, not just method signatures:
public double getTemperature() {
    double fahrenheit = thermometer.readFahrenheit();
    return (fahrenheit - 32) * 5.0 / 9.0;  // F → C conversion
}

// LESSON: Adapter responsibility is not just method name mapping.
// It MUST correctly translate ALL semantic differences:
//   - units (cm → inches, Fahrenheit → Celsius)
//   - coordinate systems (origin+size vs two-corner)
//   - error codes (String "FAIL:X" vs exception)
//   - null conventions (null vs Optional vs sentinel values)
```

---

### 🔗 Related Keywords

- `Facade Pattern` — simplifies complex subsystem interface (vs Adapter: translates incompatible interface)
- `Decorator Pattern` — adds behavior, same interface (vs Adapter: changes interface to match target)
- `Proxy Pattern` — same interface, controls access (vs Adapter: translates between interfaces)
- `Bridge Pattern` — structural separation by design intent, not for post-hoc compatibility
- `Anti-Corruption Layer` — architectural Adapter: prevents legacy model from polluting new domain

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Wrap a class with incompatible interface  │
│              │ to present the expected interface.        │
│              │ Neither client nor adaptee is modified.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Integrating legacy code; third-party lib  │
│              │ interface doesn't match your code;       │
│              │ interface translation without modification │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Both classes can be modified (use         │
│              │ refactoring instead); adapting so many   │
│              │ methods that a rewrite is cleaner        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Travel plug adapter: UK charger works    │
│              │  in EU socket — nothing modified on      │
│              │  either side, just translated."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Facade Pattern → Decorator Pattern →      │
│              │ Proxy Pattern → Anti-Corruption Layer     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In Spring MVC, `HandlerAdapter` is an explicit implementation of the Adapter pattern. The `DispatcherServlet` calls `HandlerAdapter.handle(request, response, handler)` on all registered adapters until one can handle the request. There are adapters for `@Controller`, for `HttpRequestHandler`, for `Servlet`. How does this enable Spring to support multiple programming models for request handling without `DispatcherServlet` knowing about any of them? What is the open/closed principle benefit here?

**Q2.** Java's `Arrays.asList()` and `Collections.unmodifiableList()` return special List implementations that adapt existing data structures to the `List` interface. `Arrays.asList()` returns a fixed-size list backed by the array — the list IS the array, with List interface on top. How is this an example of the Adapter pattern? What are the semantic gotchas (list modifications reflect in the original array; can't add/remove elements)? Is `Arrays.asList()` a proper Adapter or something else?
