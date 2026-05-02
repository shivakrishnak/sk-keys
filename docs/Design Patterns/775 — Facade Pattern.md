---
layout: default
title: "Facade Pattern"
parent: "Design Patterns"
nav_order: 775
permalink: /design-patterns/facade-pattern/
number: "775"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Adapter Pattern, SOLID Principles"
used_by: "API simplification, Legacy subsystem wrapping, SDK design, Home theater example"
tags: #intermediate, #design-patterns, #structural, #oop, #simplification
---

# 775 — Facade Pattern

`#intermediate` `#design-patterns` `#structural` `#oop` `#simplification`

⚡ TL;DR — **Facade** provides a simplified, unified interface to a complex subsystem — hiding the complexity of multiple interacting classes behind a single, easy-to-use entry point, so clients don't need to understand the internal workings of the subsystem.

| #775            | Category: Design Patterns                                                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Object-Oriented Programming, Adapter Pattern, SOLID Principles                  |                 |
| **Used by:**    | API simplification, Legacy subsystem wrapping, SDK design, Home theater example |                 |

---

### 📘 Textbook Definition

**Facade** (GoF, 1994): a structural design pattern that provides a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use. The facade doesn't prevent clients from using subsystem classes directly if they need fine-grained control — it just provides a simpler default path. GoF intent: "Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use." Distinguished from: **Adapter** (makes incompatible interface compatible — translates; Facade simplifies without translation). **Mediator** (coordinates communication between objects — Facade coordinates access TO a subsystem). **Proxy** (same interface, controls access — Facade uses a different, simpler interface).

---

### 🟢 Simple Definition (Easy)

A car. You press Start button, push the gas pedal, and steer. You don't manually: engage the fuel injector, trigger the ignition coil, manage the throttle body, coordinate the transmission, control the alternator. The car's dashboard/controls ARE the facade — a simplified interface hiding the engine, fuel, electrical, and transmission subsystems. If you want, you can open the hood (access subsystem directly). Most people just use the facade.

---

### 🔵 Simple Definition (Elaborated)

A `HomeTheaterFacade.watchMovie("Inception")` method: (1) Amplifier.on(), (2) Amplifier.setVolume(5), (3) DVDPlayer.on(), (4) DVDPlayer.play("Inception"), (5) Projector.on(), (6) Projector.setWidescreen(), (7) Lights.dim(10), (8) PopcornMaker.on(). Eight steps across 5 objects. Without facade: every client must orchestrate all 8. With facade: `homeTheater.watchMovie("Inception")` — one call. Clients don't know any subsystem classes exist. The facade's `endMovie()` reverses the sequence.

---

### 🔩 First Principles Explanation

**How Facade reduces coupling and complexity for common use cases:**

```
WITHOUT FACADE — client knows the subsystem:

  class MovieNight {
      void watchMovie(String title) {
          amplifier.on();
          amplifier.setVolume(5);
          amplifier.setSurroundSound();
          dvdPlayer.on();
          dvdPlayer.setVolume(5);
          dvdPlayer.play(title);
          projector.on();
          projector.setInput(dvdPlayer);
          projector.setWidescreen();
          lights.dim(10);
          popcorn.on();
          popcorn.pop();
      }
  }

  // PROBLEMS:
  // - Every client of the home theater must know all 5 subsystem classes.
  // - Every client must know the correct sequence (amplifier before DVDPlayer, etc.)
  // - Changes to subsystem classes (e.g., new projector model) affect ALL clients.

FACADE SOLUTION:

  // SUBSYSTEM CLASSES (unchanged):
  class Amplifier {
      void on() { ... }
      void off() { ... }
      void setVolume(int level) { ... }
      void setSurroundSound() { ... }
  }

  class DVDPlayer {
      void on() { ... }
      void off() { ... }
      void play(String movie) { ... }
      void stop() { ... }
      void eject() { ... }
  }

  class Projector {
      void on() { ... }
      void off() { ... }
      void setInput(DVDPlayer player) { ... }
      void setWidescreen() { ... }
  }

  class Lights { void dim(int level) { ... } void on() { ... } }
  class PopcornMaker { void on() { ... } void off() { ... } void pop() { ... } }

  // FACADE — simplified interface:
  class HomeTheaterFacade {
      private final Amplifier amp;
      private final DVDPlayer dvd;
      private final Projector projector;
      private final Lights lights;
      private final PopcornMaker popcorn;

      HomeTheaterFacade(Amplifier amp, DVDPlayer dvd, Projector projector,
                        Lights lights, PopcornMaker popcorn) {
          this.amp = amp; this.dvd = dvd;
          this.projector = projector; this.lights = lights; this.popcorn = popcorn;
      }

      void watchMovie(String title) {
          System.out.println("Get ready to watch a movie...");
          popcorn.on();
          popcorn.pop();
          lights.dim(10);
          projector.on();
          projector.setInput(dvd);
          projector.setWidescreen();
          amp.on();
          amp.setVolume(5);
          amp.setSurroundSound();
          dvd.on();
          dvd.play(title);
      }

      void endMovie() {
          System.out.println("Shutting movie theater down...");
          popcorn.off();
          lights.on();
          projector.off();
          amp.off();
          dvd.stop();
          dvd.eject();
          dvd.off();
      }
  }

  // CLIENT:
  HomeTheaterFacade homeTheater = new HomeTheaterFacade(amp, dvd, proj, lights, popcorn);
  homeTheater.watchMovie("Inception");   // 1 call. Client knows only HomeTheaterFacade.
  homeTheater.endMovie();

  // If client needs fine-grained control: can still use subsystem classes directly.
  // Facade doesn't hide them — just provides a convenient shortcut.

FACADE AS PACKAGE BOUNDARY IN JAVA:

  // Spring's JdbcTemplate is a Facade over JDBC:
  // Without JdbcTemplate:
  Connection conn = dataSource.getConnection();
  try {
      PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
      ps.setLong(1, userId);
      ResultSet rs = ps.executeQuery();
      if (rs.next()) {
          return new User(rs.getLong("id"), rs.getString("name"));
      }
      return null;
  } catch (SQLException e) { throw new RuntimeException(e); }
  finally { try { conn.close(); } catch (Exception e) { ... } }

  // With JdbcTemplate (Facade):
  return jdbcTemplate.queryForObject(
      "SELECT * FROM users WHERE id = ?",
      (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("name")),
      userId
  );
  // JdbcTemplate hides: connection management, exception translation,
  //   ResultSet iteration, resource cleanup. Facade reduces JDBC ceremony.

FACADE vs ADAPTER:

  ADAPTER:    "I have a UK plug. I need it to fit in an EU socket."
              Translates an existing interface to a different expected interface.
              Wraps ONE class. Intent: interface compatibility.

  FACADE:     "This system is too complex. I want a simpler API."
              Provides a simplified interface to MULTIPLE classes.
              Wraps a SUBSYSTEM. Intent: simplification.

  KEY: Adapter changes interface. Facade simplifies interface (but doesn't change it to satisfy a pre-existing contract).

FACADE LAYERS IN MICROSERVICES — BFF (BACKEND FOR FRONTEND):

  // A BFF (Backend for Frontend) is an architectural Facade:
  // Mobile app needs: user profile + recent orders + recommendations — in one call.
  // Without BFF: mobile makes 3 separate API calls to 3 microservices.
  // With BFF: mobile calls BFF, BFF calls 3 services, aggregates, returns one response.
  // BFF = Facade over multiple microservices, tailored for the mobile client.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Facade:

- Client must know and coordinate 5 subsystem classes with correct call order
- Changes to subsystem propagate to all clients (high coupling)

WITH Facade:
→ Client knows one class: `HomeTheaterFacade`. Subsystem can change internally; facade isolates clients.
→ Common use cases: one call. Power users: can still access subsystem directly.

---

### 🧠 Mental Model / Analogy

> A travel agent. You want a vacation: flights, hotel, car rental, travel insurance, guided tours. Without an agent: 5 separate systems to navigate — airline website, hotel booking, car rental, insurance provider, tour operator. All with different interfaces, different confirmation flows. The travel agent (facade) takes: "2 weeks in Italy, budget $3000" — handles everything, gives you one confirmation. You CAN book everything yourself (access subsystems directly) — the agent just makes the common case easy.

"Travel agent" = Facade
"Airline, hotel, car, insurance, tour" = subsystem classes
"2 weeks in Italy, $3000" = simplified, high-level interface
"Returns one confirmation" = Facade returns aggregated result
"You CAN book yourself" = Facade doesn't prevent direct subsystem access

---

### ⚙️ How It Works (Mechanism)

```
FACADE STRUCTURE:

  Client → Facade.operation()
               → SubsystemA.step1()
               → SubsystemB.step2()
               → SubsystemC.step3()
               → SubsystemA.step4()
               → return result

  Subsystem classes exist and are still accessible.
  Facade coordinates their use for common scenarios.
  Complex clients may bypass facade for fine-grained control.
```

---

### 🔄 How It Connects (Mini-Map)

```
Complex subsystem with many interacting classes
        │
        ▼
Facade Pattern ◄──── (you are here)
(unified simple interface; hides subsystem complexity)
        │
        ├── Adapter: translates one interface to another (vs Facade: simplifies multiple)
        ├── Mediator: coordinates communication between objects (bidirectional vs Facade's one-way)
        ├── BFF Pattern: architectural Facade for microservice aggregation
        └── JdbcTemplate / RestTemplate: Spring's Facade over JDBC and HTTP
```

---

### 💻 Code Example

```java
// Email sending facade — hides SMTP, MIME, template engine, retry logic:
public class EmailFacade {
    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;
    private final RetryPolicy retryPolicy;

    EmailFacade(JavaMailSender mailSender, TemplateEngine templateEngine, RetryPolicy retry) {
        this.mailSender    = mailSender;
        this.templateEngine = templateEngine;
        this.retryPolicy   = retry;
    }

    // SIMPLIFIED interface: callers just provide template name + variables:
    public void sendWelcomeEmail(String toAddress, String userName) {
        sendTemplatedEmail(toAddress, "Welcome to Acme!", "welcome",
                           Map.of("name", userName));
    }

    public void sendPasswordReset(String toAddress, String resetToken) {
        sendTemplatedEmail(toAddress, "Reset your password", "password-reset",
                           Map.of("token", resetToken, "expiry", "24 hours"));
    }

    // Internal method: coordinates template + SMTP + retry (hidden from clients):
    private void sendTemplatedEmail(String to, String subject, String template,
                                    Map<String, Object> variables) {
        retryPolicy.execute(() -> {
            // 1. Render template:
            String htmlBody = templateEngine.render(template + ".html", variables);
            String textBody = templateEngine.render(template + ".txt",  variables);

            // 2. Build MIME message:
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(textBody, htmlBody);

            // 3. Send:
            mailSender.send(message);
        });
    }
}

// CALLER — knows nothing about JavaMailSender, MIME, templates, retry:
@Service
class UserRegistrationService {
    @Autowired EmailFacade email;

    void register(User user) {
        userRepository.save(user);
        email.sendWelcomeEmail(user.getEmail(), user.getName());  // 1 call
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                                                                                                                                                                                                                     |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Facade locks you out of subsystem access | Facade does NOT prevent direct subsystem access — it just doesn't require it. If a client needs fine-grained control over, say, SMTP settings, it can still use JavaMailSender directly. Facade is a convenience layer, not an access control layer (that's Proxy).                                                                         |
| Facade is always a class                 | In practice, Facade can be a class, a service, an API endpoint, a module, or even a microservice (BFF). The principle — provide a simplified interface to a complex system — applies at multiple levels of architecture. JdbcTemplate, RestTemplate, Spring's Facade beans are all Facade pattern at the component level.                   |
| Facade is the same as Mediator           | Facade: coordinates CLIENT access to a subsystem (mostly one-directional — client calls facade). Mediator: coordinates communication BETWEEN subsystem components (the subsystem components communicate through the mediator, not the other way). Facade simplifies external access. Mediator reduces coupling between internal components. |

---

### 🔥 Pitfalls in Production

**Facade becoming a God Object — accumulating too much unrelated logic:**

```java
// ANTI-PATTERN: Facade grows to include unrelated responsibilities:
class ApplicationFacade {
    // Email subsystem:
    void sendWelcomeEmail(String email) { ... }
    void sendPasswordReset(String email) { ... }

    // Order subsystem:
    Order createOrder(Cart cart) { ... }
    void cancelOrder(String orderId) { ... }

    // Payment subsystem:
    Payment processPayment(Order order, CreditCard card) { ... }

    // Inventory subsystem:
    void updateStock(String sku, int delta) { ... }
    List<Product> searchProducts(String query) { ... }

    // Report subsystem:
    Report generateSalesReport(DateRange range) { ... }

    // ... 40 more methods
}
// "Facade" has become a God Object — knows everything, coordinates everything.
// Change in any subsystem affects this class. Not the intent of Facade.

// FIX: Multiple focused facades, each simplifying ONE subsystem:
class EmailFacade    { void sendWelcomeEmail(...); void sendPasswordReset(...); }
class OrderFacade    { Order createOrder(...);    void cancelOrder(...); }
class PaymentFacade  { Payment processPayment(...); }
class InventoryFacade { void updateStock(...); List<Product> search(...); }
// Each facade: single responsibility. Simpler to test, maintain, change.
```

---

### 🔗 Related Keywords

- `Adapter Pattern` — translates one interface to another (vs Facade: simplifies multiple into one)
- `Mediator Pattern` — coordinates between subsystem objects (vs Facade: external client → subsystem)
- `JdbcTemplate` — Spring's Facade over JDBC (canonical production example)
- `BFF (Backend for Frontend)` — architectural Facade: aggregates multiple microservices for a client
- `Service Layer` — application layer Facade: simplifies domain model access for presentation layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Simplified, unified interface to a complex│
│              │ subsystem. Hide the parts; expose only   │
│              │ what clients need for common scenarios.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex subsystem with many interacting  │
│              │ classes; want simple API for common      │
│              │ cases; reducing coupling to subsystem    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Facade accumulates too many responsibilities│
│              │ (becomes God Object); when ALL clients   │
│              │ need fine-grained control — skip the     │
│              │ simplification                            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Travel agent: tell me destination and   │
│              │  budget — get one confirmation. Can still│
│              │  book everything yourself if you want."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Adapter Pattern → Mediator Pattern →      │
│              │ JdbcTemplate → BFF (Backend for Frontend) │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `JdbcTemplate` is a Facade over JDBC. It also handles exception translation (converting `SQLException` to Spring's `DataAccessException` hierarchy). Is this exception translation part of the Facade responsibility, or is it Adapter behavior? Where does Facade end and Adapter begin in JdbcTemplate? Consider that Adapter is about interface translation and Facade is about simplification.

**Q2.** In a hexagonal architecture (Ports and Adapters), the "application service layer" acts as a Facade: `OrderApplicationService.placeOrder(PlaceOrderCommand)` coordinates domain objects, repositories, and event publishing. Is this the same as Facade pattern? In hexagonal architecture, what are the "ports" and what are the "adapters"? Does the Service Layer (Facade) violate hexagonal architecture's principle of keeping business logic in the domain, or does it complement it?
