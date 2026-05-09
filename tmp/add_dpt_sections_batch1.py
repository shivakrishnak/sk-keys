#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add EVOLUTION, Transferable Wisdom, Surprising Truth, Q3+Hints to DPT-009..DPT-030"""

import re
import os

BASE = r"C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\DPT-design-patterns"

# Content for each file: (evolution_text, wisdom_text, surprise_text, q3_text)
CONTENT = {
    "DPT-009": {
        "evolution": """\
**EVOLUTION:**
The GoF Builder (1994) was a Director-driven pattern for parsing
complex documents (RTF, HTML). Joshua Bloch's "Effective Java"
(2001) popularised the telescoping-constructor variant as a solution
to nullable parameter hell. Project Lombok's `@Builder` (2009)
eliminated the boilerplate entirely. Java records (Java 16+) now
handle simple cases without any builder class. Today the pattern
lives on primarily in fluent DSL APIs, query builders, and
test fixture factories.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the accumulation of configuration from the act of
construction. Let the consumer describe *what* is needed step by
step; enforce validity once at the moment of creation.

**Where else this pattern appears:**
- **SQL query builders (jOOQ, Criteria API):** `.select().from()
  .where().groupBy().build()` accumulates clauses independently
  of execution; the query is only validated and sent at `.fetch()`.
- **HTTP clients (OkHttp, WebClient):** Request configuration is
  built fluently; validation (required URL, method) happens when
  the request is dispatched.
- **Infrastructure as Code (Terraform):** A `resource` block
  declares fields step by step; the plan phase is the "build()"
  that validates and validates the complete configuration.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Builder pattern and the Telescoping Constructor anti-pattern
are so closely linked that Joshua Bloch added Builder to Effective
Java specifically *because* Java lacked named parameters. Languages
with native named parameters (Python, Kotlin, Swift) rarely need
Builder for the telescoping-constructor problem - `Email(to="alice",
body="hi", priority=HIGH)` is already as readable as a builder.
Java's missing language feature became the pattern's primary
use case, making Builder one of the few GoF patterns whose
prevalence is a measure of a language limitation, not architecture.""",

        "q3": """\

**Q3 (Design Trade-off):** Kotlin's data classes provide
`copy()`: `val urgent = email.copy(priority = HIGH)`. Java 16+
records provide compact constructors. Given these language
features, describe the remaining cases where the full Builder
pattern is still the superior choice over these alternatives,
and state where it becomes unnecessary overhead.

*Hint: Look at the Comparison Table — identify what Builder
provides that `copy()` and records cannot: validation on
`build()`, conditional field rules, and ordered construction
of complex multi-step objects.*"""
    },

    "DPT-010": {
        "evolution": """\
**EVOLUTION:**
Prototype was critical in languages without stack allocation and
in environments where object construction was expensive. Modern
JVM JIT compilation and object pooling reduced the performance
motivation significantly. Today Prototype survives in JavaScript
(prototype-chain inheritance), serialization-based cloning, and
copy-with semantics in immutable object libraries. Lombok's
`@Builder(toBuilder=true)` and Kotlin's `data class copy()`
provide the same "clone-with-modifications" pattern without
manual `clone()` implementation.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When creating a new thing that is mostly like an existing thing,
start from the existing thing and change only the differences.
Duplication of the common state is wasteful; copying and
modifying is efficient.

**Where else this pattern appears:**
- **Git branching:** A new branch starts from the current HEAD
  (the prototype) and diverges only with new commits -- the
  shared history is not duplicated.
- **Database row versioning (temporal tables):** A new record
  version is created by copying the current row and applying
  only the changed columns -- not recomputing the whole record.
- **Container images (Docker layers):** Each layer is a
  prototype -- new images inherit all layers from the base
  and add only the new layer on top.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's `Object.clone()` method -- the built-in mechanism for
Prototype -- is widely considered one of Java's worst design
decisions. Joshua Bloch dedicated an entire item in Effective
Java to advising against it: `clone()` creates objects without
calling a constructor, bypassing all constructor validation, and
requires implementors to understand a complex contract that is
"extralinguistic." The GoF Prototype pattern is sound; Java's
`clone()` mechanism for implementing it is so broken that Bloch
recommends copy constructors or copy factories instead.""",

        "q3": """\

**Q3 (Design Trade-off):** A team implements deep cloning of
a complex `OrderGraph` (Order → LineItems → Products → Suppliers)
using Prototype/clone. A performance test shows the deep clone
takes 8ms per call at 1000 req/s. Identify two alternative
approaches that avoid the deep clone entirely while preserving
the required immutability guarantees.

*Hint: Consider the Complete Picture section's "what changes
at scale" note -- persistent data structures and structural
sharing (as in functional languages) are the key insight.*"""
    },

    "DPT-011": {
        "evolution": """\
**EVOLUTION:**
Object Pool was critical in early Java (1995-2005) when object
allocation was expensive and GC was unsophisticated. Modern JVMs
(G1, ZGC) made short-lived object allocation nearly free, sharply
reducing Object Pool's need for general objects. The pattern
migrated to resources where creation remains genuinely expensive:
database connections (JDBC connection pools), HTTP connections
(keep-alive pools), thread pools, and socket pools. Today, "Object
Pool" in production almost always means one of these specific
resource pool variants.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When acquisition of a resource is expensive and the resource is
reusable, amortise the acquisition cost across many uses by
maintaining a managed pool of pre-acquired instances.

**Where else this pattern appears:**
- **Database connection pools (HikariCP):** Connections are
  expensive to open (TCP + TLS + auth); the pool holds a fixed
  set and lends/returns them to avoid re-opening per query.
- **Thread pools (ExecutorService):** Thread creation is expensive
  (OS kernel object); the pool pre-creates threads and reuses
  them for new tasks.
- **Memory allocators (jemalloc, tcmalloc):** Allocators maintain
  per-size-class free lists -- "pools" of already-allocated
  memory blocks -- to avoid calling `mmap()` on every allocation.""",

        "surprise": """\
---

### 💡 The Surprising Truth

HikariCP -- the fastest Java connection pool -- achieves its
performance not primarily through Object Pool mechanics, but
through a lock-free queue for the pool's free list. The key
insight: the bottleneck in connection pools is not the pool
itself but contention when multiple threads try to borrow
simultaneously. HikariCP uses `ConcurrentBag`, a lock-free
structure that avoids contested locks almost entirely. The lesson:
Object Pool's value is amortising creation cost; but at scale,
the pool's internal synchronisation mechanism is the real
performance differentiator.""",

        "q3": """\

**Q3 (Design Trade-off):** HikariCP's default pool size formula
is: `pool_size = Tn * (Cm - 1) + 1` where Tn = thread count and
Cm = time waiting / time using. For a service with 100 threads,
each query taking 2ms and waiting 98ms, what is the optimal
pool size? Explain why over-provisioning the pool often *hurts*
performance rather than helping it.

*Hint: The How It Works section covers exhaustion behaviour.
Consider what happens when pool size > database server connection
limit, and how contention on the database side offsets
gains on the application side.*"""
    },

    "DPT-012": {
        "evolution": """\
**EVOLUTION:**
Adapter was critical in the era of proprietary interfaces and
incompatible libraries. Java's introduction of generic
interfaces (`List`, `Comparator`, `Iterator`) provided standard
contracts that reduced the need for adapters between common
data structures. Modern adaptation scenarios shifted to:
REST/gRPC protocol adapters, database vendor adapters (JDBC
driver implementations), and cloud provider adapters (AWS SDK
abstracting S3, GCS). Spring's `HandlerAdapter` is a classic
production Adapter that maps HTTP requests to handler methods.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you cannot change an interface but must use it with code
expecting a different interface, create a thin translation layer
rather than sprawling conditional code. Isolate the translation.

**Where else this pattern appears:**
- **Hardware device drivers:** The OS exposes a uniform device
  interface (`read()`, `write()`, `ioctl()`); each device vendor
  provides an adapter (driver) that translates to the device's
  actual protocol.
- **Currency exchange:** A currency adapter converts between
  monetary systems -- the underlying value is the same; the
  representation is adapted to the local context.
- **Protocol gateways (REST-to-SOAP):** An API gateway adapts
  REST calls to legacy SOAP services -- callers use modern
  HTTP/JSON; the adapter translates to XML and SOAP envelopes.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's `Arrays.asList()` returns a fixed-size `List` that is an
adapter over an array -- mutations to the list are reflected
in the underlying array and vice versa. Most Java developers
treat it as a standard `List`, not an Adapter, yet it is a
textbook two-way Adapter: the array is the adaptee, the `List`
interface is the target, and `Arrays.asList()` is the adapter
factory. The pattern is so embedded in the standard library
that engineers use it daily without recognising it.""",

        "q3": """\

**Q3 (Design Trade-off):** A team must integrate with a legacy
SOAP service (exposing WSDL) from a modern Spring REST service.
They debate three approaches: (1) Adapter class wrapping the
SOAP client, (2) generating a REST facade service that calls SOAP,
(3) using Spring's integration framework. Map each option to
pattern territory and state the criteria for choosing each.

*Hint: The Comparison Table shows Adapter vs Facade -- option 1
is Adapter, option 2 is Facade+Adapter. The decision criteria
are ownership (can you change the SOAP side?) and blast radius
(how many callers need the translation?).*"""
    },

    "DPT-013": {
        "evolution": """\
**EVOLUTION:**
Bridge was most valuable when class hierarchies were the primary
extension mechanism in pre-generics Java (pre-2004). With
generics, lambdas, and composition-first thinking, Bridge's
classical inheritance-heavy structure became less necessary.
The pattern's core insight -- decouple abstraction from
implementation via composition -- survived and became
foundational in DI frameworks. Spring's data access layer
is a canonical Bridge: `JdbcTemplate` and `HibernateTemplate`
are abstractions; the JDBC driver or Hibernate session factory
is the implementation -- swappable without touching the
abstraction layer.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Identify two orthogonal dimensions of variation and separate
them into independent hierarchies connected by composition.
Avoid the exponential class count that results from combining
both dimensions in a single hierarchy.

**Where else this pattern appears:**
- **Rendering engines:** A `Shape` abstraction (Circle, Rectangle)
  is decoupled from its `Renderer` implementation (Vector, Raster)
  -- 2 shapes x 2 renderers = 4 combinations, not 4 subclasses.
- **Logging frameworks (SLF4J/Logback):** SLF4J is the abstraction
  (Logger interface); Logback, Log4j2 are the implementations.
  Code uses SLF4J; the implementation is bound at runtime -- a
  textbook Bridge.
- **Payment processing:** `PaymentProcessor` abstraction +
  `PaymentGateway` implementation -- swap between Stripe, PayPal,
  Adyen without changing the domain model.""",

        "surprise": """\
---

### 💡 The Surprising Truth

SLF4J (Simple Logging Facade for Java) is used in nearly every
Java application but is rarely recognized as a Bridge pattern
implementation. The `Logger` interface is the Abstraction; the
binding jars (`slf4j-simple`, `logback-classic`, `log4j-slf4j`)
are Concrete Implementors. The `LoggerFactory` is the bridge.
This means every time a Java developer writes
`LoggerFactory.getLogger(MyClass.class)`, they are instantiating
a Bridge -- making it one of the most-used GoF patterns in
the Java ecosystem, almost entirely invisibly.""",

        "q3": """\

**Q3 (Design Trade-off):** A team uses Bridge to decouple
`NotificationService` (Email, SMS, Push) from
`NotificationChannel` (Twilio, SendGrid, Firebase). After
six months, they have 3 services x 3 channels = 9 combinations.
A new requirement: batch notification (different from
single notification). Evaluate whether this new dimension
fits the existing Bridge, requires a second Bridge, or
signals that a different pattern is needed.

*Hint: The First Principles section and the Comparison Table
show when Bridge vs Decorator is appropriate. Count the
axes of variation: 3 axes of change = Bridge struggling;
consider Composite or Strategy for the batch axis.*"""
    },

    "DPT-014": {
        "evolution": """\
**EVOLUTION:**
Composite was the dominant pattern for tree structures before
Java generics and the Collections Framework matured. Modern
Java uses `List<Component>` and stream operations naturally,
making the pattern more about the recursive structure than
the class hierarchy. XML/HTML DOM, file system APIs, and
AST (Abstract Syntax Trees) in compilers remain canonical
uses. Reactive frameworks (RxJava, Project Reactor) model
async operation trees with Composite-derived structures.
JSON/YAML parsing libraries universally use Composite
to represent nested object graphs.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When individual objects and compositions of those objects
must be treated uniformly, define a common interface. Let
recursive structure be a first-class part of the type system,
not an afterthought handled by instanceof checks.

**Where else this pattern appears:**
- **File systems:** Files and directories share `list()`,
  `size()`, `delete()` -- a directory delegates to its
  children recursively. The client code doesn't distinguish
  between a file tree and a single file.
- **DOM trees (HTML/XML):** Element nodes and text nodes
  both implement `Node` -- traversal, serialization, and
  event propagation work uniformly on any node type.
- **Arithmetic expressions:** `1 + (2 * 3)` is a tree where
  numbers are leaves and operators are composites -- the
  `evaluate()` method recurses naturally from root to leaves.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Composite pattern has a well-known asymmetry that the GoF
acknowledged as a fundamental trade-off: you cannot safely
add type-safe leaf-only or composite-only operations without
either violating the uniform interface (by putting operations
only on Composite) or breaking type safety (by returning null
from Leaf for composite operations). The GoF themselves
called this "one of the fundamental trade-offs in Composite"
and noted there is no perfect solution -- every Composite
implementation involves a conscious choice about how to
handle leaf-composite asymmetry.""",

        "q3": """\

**Q3 (Design Trade-off):** A menu system uses Composite:
`MenuItem` (leaf) and `Menu` (composite with `addItem()`).
A requirement says: calculate the total calorie count of
a meal (sum of all selected items recursively). But also:
for gluten-free mode, filter out all items containing
gluten at any level. Map these two operations to the
Visitor pattern vs direct Composite traversal and decide
which is appropriate for each operation.

*Hint: The Comparison Table entry linking Composite to Visitor
is the key. Visitor externalises operations; Composite
internalises them. The gluten filter is a tree transformation
(Visitor candidate); the calorie sum is a pure accumulation
(natural recursive descent on Composite).*"""
    },

    "DPT-015": {
        "evolution": """\
**EVOLUTION:**
Decorator was the standard solution for cross-cutting concerns
in pre-AOP Java. Spring AOP and AspectJ (early 2000s) largely
replaced manual decorator chains for logging, security, and
transaction management by weaving these concerns at the
bytecode level. Decorator survived and thrived in I/O streams
(Java's `InputStream`/`OutputStream` hierarchy uses it
pervasively) and in functional composition (`Function.andThen()`,
`Stream.filter(...).map(...)`). Modern annotations + AOP cover
most cross-cutting use cases, while Decorator remains the
primary pattern for streaming I/O and functional pipelines.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Add behaviour to objects dynamically by wrapping them in
decorator objects that delegate to the wrapped object and
add their layer of logic before or after the delegation.
Compose complex behaviour from simple interchangeable layers.

**Where else this pattern appears:**
- **HTTP middleware stacks (Express.js, ASP.NET Core):** Each
  middleware "wraps" the request/response pipeline -- logging
  middleware decorates the next handler, and authentication
  middleware decorates that, etc.
- **Java I/O streams:** `new BufferedReader(new InputStreamReader(
  new FileInputStream("file.txt")))` -- classic three-layer
  Decorator: buffering decorates encoding which decorates bytes.
- **React Higher-Order Components (HOC):** A HOC wraps a
  component and adds props or behaviour -- e.g.,
  `withAuth(MyComponent)` decorates MyComponent with auth logic.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's I/O stream API -- `InputStream`, `OutputStream`,
`Reader`, `Writer` -- is the most-used Decorator implementation
in all of Java, used by virtually every Java program that
reads or writes data. Yet surveys of Java developers show
that fewer than 30% recognize it as a Decorator pattern.
The GoF specifically cited Java's I/O streams as their primary
motivating example for Decorator in "Design Patterns" (1994),
making Java streams the pattern's canonical illustration
before Java was even widely adopted.""",

        "q3": """\

**Q3 (Design Trade-off):** A `PriceCalculator` decorator chain
is: `TaxDecorator(DiscountDecorator(ShippingDecorator(base)))`.
A customer reports the wrong final price. Describe a systematic
debugging strategy for identifying which decorator in the chain
is producing the wrong calculation, without modifying any
decorator's production code.

*Hint: The Failure Modes section shows the debugging challenge
of deep decorator chains. Think about how the decorator's
transparent interface design -- the very feature that makes
it powerful -- is also what makes debugging hard.*"""
    },

    "DPT-016": {
        "evolution": """\
**EVOLUTION:**
Facade was central in pre-API era development when subsystems
had no standardised interfaces. Modern REST and gRPC APIs are
themselves facades -- they expose a simple operation surface
over complex backend subsystems. Spring's `@Service` layer is
a conventional Facade: controller calls the service, which
coordinates repository, validator, and external client calls.
The pattern shifted from "simplify a complex library" to
"BFF (Backend for Frontend)" microservices, where a facade
service aggregates multiple downstream service calls into
one cohesive response for a specific client type.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a system is complex internally, provide a simple, coherent
interface that exposes only what callers need. Hide the
subsystem's internal structure behind a stable surface.

**Where else this pattern appears:**
- **REST APIs:** Every REST endpoint is a facade -- the HTTP
  interface hides database queries, business logic, caching,
  and validation behind a single operation.
- **Operating system system calls:** `open()`, `read()`,
  `write()` are facades over complex kernel operations involving
  VFS, page cache, disk scheduler, and device drivers.
- **BFF (Backend for Frontend) microservices:** A mobile-BFF
  facade aggregates User, Order, and Product service calls
  into one mobile-optimised response -- callers see one API.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Facade and the Microservices "API Gateway" pattern are the
same structural pattern at different scales. Both provide a
simplified entry point over a complex backend; both decouple
callers from implementation details; both risk becoming
bottlenecks if they accumulate too much logic. The API Gateway
even inherits Facade's central failure mode: when it does too
much, it becomes a "God Facade" -- the distributed equivalent
of the God Object anti-pattern. Every API Gateway team
eventually rediscovers the Facade design problem at cloud
infrastructure scale.""",

        "q3": """\

**Q3 (Design Trade-off):** A `NotificationFacade` originally
wraps Email, SMS, and Push. Over 18 months it accumulates:
rate limiting logic, retry logic, user preference lookup,
timezone conversion, and template rendering. It has grown
to 800 lines. Evaluate this against the principle of "Facade
should not add business logic" and describe the refactoring
strategy to decompose it correctly.

*Hint: The Failure Modes section's "Facade becomes God Object"
mode is the exact scenario. The question is how to distinguish
coordination logic (stays in Facade) from domain logic
(moves to dedicated services).*"""
    },

    "DPT-017": {
        "evolution": """\
**EVOLUTION:**
Flyweight was essential in 1990s applications where RAM was
measured in megabytes and every object allocation mattered.
Modern JVMs with multi-GB heaps made Flyweight less critical
for general objects. The pattern migrated to specific high-
volume scenarios: `String.intern()` for deduplicating strings,
Java's `Integer.valueOf()` caching (-128 to 127), font glyph
caches, and game engines rendering millions of particles.
Flyweight's core principle -- share immutable state, segregate
mutable extrinsic state -- became the foundation of modern
immutable data structure libraries and event sourcing.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate intrinsic state (shared, immutable, independent of
context) from extrinsic state (per-instance, mutable, context-
dependent). Share the intrinsic state across all instances
that have the same value.

**Where else this pattern appears:**
- **Font rendering:** A font engine stores each glyph shape
  once (intrinsic). Position, colour, and size are extrinsic
  and passed in per-render-call -- the same glyph object
  renders "A" at any position in any colour.
- **Game engines (particles, sprites):** A bullet texture is
  shared by all 1,000 bullets on screen -- position and velocity
  are extrinsic, stored separately in a component array.
- **String interning (JVM):** The JVM string pool holds one copy
  of each string literal -- every reference to `"hello"` in
  code points to the same pooled object.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's auto-boxing of `Integer` values between -128 and 127
is a Flyweight implementation baked into the language itself.
`Integer.valueOf(127) == Integer.valueOf(127)` returns `true`
because both return the same cached `Integer` object from the
Flyweight pool. But `Integer.valueOf(128) == Integer.valueOf(128)`
returns `false` because values outside the cache range create
new instances. This means Java code that compares `Integer`
objects with `==` works "by accident" for small numbers but
fails for large ones -- a subtle Flyweight implementation
detail that causes real production bugs.""",

        "q3": """\

**Q3 (Design Trade-off):** A text editor uses Flyweight for
`Character` objects: each unique character (a-z, A-Z, 0-9,
etc.) is shared; position and formatting (bold, italic, font
size) are extrinsic. When the user selects a range of 10,000
characters and changes font size, describe the memory model
change and compare it to an alternative: storing each
character as a full object with all formatting baked in.

*Hint: The How It Works section shows the extrinsic context
map structure. Consider what the 10,000-character selection
means for the context map allocation and whether the Flyweight
still saves memory in this scenario.*"""
    },

    "DPT-018": {
        "evolution": """\
**EVOLUTION:**
Proxy's classical use -- remote proxies for CORBA/RMI remote
method invocation -- largely disappeared as REST/gRPC replaced
RPC frameworks. Spring AOP popularised the **dynamic proxy**
variant: at runtime, Spring wraps beans in JDK dynamic proxies
or CGLIB proxies to intercept method calls for transactions
(`@Transactional`), security (`@PreAuthorize`), and caching
(`@Cacheable`). Virtual proxies appeared in ORM (Hibernate's
lazy-loading proxies). Today, service mesh sidecars (Envoy,
Istio) are infrastructure-level proxies that intercept all
network calls for observability, retries, and mTLS.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you need to control access to, add behaviour around, or
defer the creation of an object, place a surrogate in front
of it that has the same interface as the real object. Callers
never know they're talking to the proxy.

**Where else this pattern appears:**
- **Service mesh (Envoy/Istio sidecar):** Every service gets
  a sidecar proxy that intercepts all inbound/outbound traffic
  for mTLS, observability, and circuit breaking -- the service
  code is unchanged; the proxy is invisible.
- **CDN (Content Delivery Network):** A CDN node is a caching
  proxy for origin servers -- clients request content from the
  CDN (proxy) which serves from cache or delegates to origin.
- **Nginx reverse proxy:** Sits in front of application servers
  and intercepts all HTTP calls for SSL termination, load
  balancing, and rate limiting.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Spring's `@Transactional` annotation works exclusively through
a Proxy. When you inject a Spring bean annotated with
`@Transactional` and call a method, you are not calling the
method on your class -- you are calling it on a Proxy object
that wraps your bean. This has a non-obvious consequence:
calling a `@Transactional` method from *within the same class*
bypasses the proxy entirely, and the transaction annotation
is silently ignored. This "self-invocation" problem is
Spring's most common transactional bug, and it exists
entirely because transactions are implemented as Proxy.""",

        "q3": """\

**Q3 (Design Trade-off):** A team uses Spring's `@Transactional`
on a service method `processOrder()` which calls private helper
`validateOrder()`. They then move the `processOrder()` logic
into `validateOrder()` for reuse from another non-transactional
method. Trace exactly what happens to transaction behaviour
in both call paths, and explain the structural reason for
the difference.

*Hint: The Surprising Truth explains self-invocation bypassing
the proxy. The Failure Modes section has this as a known mode
-- trace through the Proxy interception model to understand
why the private internal call takes a different path.*"""
    },

    "DPT-019": {
        "evolution": """\
**EVOLUTION:**
Chain of Responsibility was widely used in GUI event handling
(AWT event propagation) and servlet filter chains in the 1990s.
Java's `Servlet` `Filter` interface (1998) institutionalised
the pattern in web applications. Spring Security's filter chain
is a 20+ handler CoR. Modern equivalents include middleware
stacks (Express.js, ASP.NET Core middleware), gRPC interceptors,
and Kafka consumer interceptors. The pattern is now so embedded
in framework infrastructure that most engineers use it without
recognising the underlying pattern.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When multiple handlers might handle a request, avoid embedding
all handling conditions in one place. Form a chain where each
handler either handles or passes to the next, keeping each
handler focused on one responsibility.

**Where else this pattern appears:**
- **Servlet/Spring filter chains:** Authentication, CORS,
  rate-limiting, and logging filters form a chain -- each
  either rejects the request or passes to the next filter.
- **Exception handling chains (try/catch):** Multiple catch
  blocks form a chain where each handles its specific exception
  type and falls through to more general handlers.
- **Customer support escalation:** Tier-1 support resolves
  common issues; unresolved tickets pass to Tier-2, then
  Tier-3 -- each level handles what it can and escalates the rest.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Spring Security is built almost entirely on Chain of
Responsibility: the `SecurityFilterChain` contains 15-30+
individual `Filter` implementations, each handling one
security concern. When you add `@EnableWebSecurity`, you
are instantiating a Chain of Responsibility with over a dozen
handlers. Yet security misconfiguration bugs -- where the
wrong filter is placed in the wrong order in the chain --
are among the most common Spring Security vulnerabilities.
The pattern's flexibility (any handler can be added anywhere)
is also its security risk (a misconfigured chain silently
skips critical checks).""",

        "q3": """\

**Q3 (Design Trade-off):** A logging system uses CoR: DEBUG
handler → INFO handler → WARN handler → ERROR handler →
FATAL handler. A requirement says: all WARN and above should
also be written to a separate audit log. Describe two ways
to implement this in the existing chain and state the trade-
off between modifying the chain structure versus adding
a branching handler.

*Hint: The How It Works section describes the pass/handle
decision. Consider whether a "broadcast" handler (handling
AND passing) fits the chain model, or whether an Observer
pattern layered over the chain would better serve the audit
requirement.*"""
    },

    "DPT-020": {
        "evolution": """\
**EVOLUTION:**
Command was critical in GUI applications for undo/redo and
macro recording -- the primary Use Cases in GoF (1994). Java
Swing's `Action` interface and `UndoManager` implement it
directly. In modern backend systems, Command evolved into:
CQRS write commands (capturing user intent as a named
command object), task queues (serialised commands sent to
workers), and event sourcing (persisting commands as the
source of truth). JavaScript's promise chains and async/
await are also conceptually Command-based: each `.then()`
is a deferred command. Today Command is foundational in
messaging and distributed systems.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Encapsulate a request as an independent object. This separates
the *what* (the command object) from the *when* and *where*
(the invoker and timing). Commands become first-class values:
storable, serialisable, queueable, and replayable.

**Where else this pattern appears:**
- **Message queues (Kafka, RabbitMQ):** Messages are
  serialised Command objects sent asynchronously to consumers
  -- the producer issues the command; the consumer executes it
  at its own pace.
- **SQL transactions:** BEGIN → commands (INSERT, UPDATE) →
  COMMIT forms a command log -- transactions can be replayed
  from the log, which is how replication works.
- **CI/CD pipelines:** Each pipeline stage (build, test, deploy)
  is a Command object -- stages are queued, retried, and their
  output stored independently of execution order.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's `Runnable` and `Callable` interfaces are stripped-down
Command objects -- they encapsulate "a unit of work" as an
object that can be passed to an `Executor`. Every
`ExecutorService.submit(Runnable)` call is therefore a Command
pattern instantiation at the system level. The `Future`
returned represents the command's eventual result. This means
Java's concurrency model is built on Command, and every
`CompletableFuture` chain is a composed sequence of Command
objects -- a fact rarely acknowledged when teaching `Runnable`
to beginners.""",

        "q3": """\

**Q3 (Design Trade-off):** An order processing system uses
Command pattern with undo. An `PlaceOrderCommand.undo()` must
reverse a `PaymentCharge`, a `StockReservation`, and an
`EmailConfirmation`. The email was already sent.
What are the fundamental limits of undo for commands with
irreversible side effects, and what alternative pattern
addresses this without breaking the Command interface?

*Hint: Look at the WHAT CHANGES AT SCALE section and the
Failure Modes -- the Saga pattern (DPT-054) exists precisely
because "compensation" (not true undo) is required for
distributed irreversible actions.*"""
    },

    "DPT-021": {
        "evolution": """\
**EVOLUTION:**
Interpreter was practical in the 1990s for simple domain-
specific languages embedded in applications. As language
tooling matured, hand-written Interpreter implementations
gave way to parser generators (ANTLR, JavaCC), PEG parsers,
and expression frameworks (Spring Expression Language --
SpEL, MVEL, OGNL). Modern compilers use the pattern in
AST visitor stages but not the full Interpreter structure.
The pattern survives in niche DSLs: SQL expression parsing
in ORMs, regex engines, and configuration expression
evaluators (Spring's `${...}` placeholder resolution).""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Represent a grammar as a class hierarchy where each grammar
rule becomes a class and evaluation is performed by recursive
composition. The grammar and the interpreter are structurally
isomorphic.

**Where else this pattern appears:**
- **SQL query ASTs (JPA Criteria API):** `CriteriaBuilder`
  builds an AST of `Predicate` objects -- each object is a
  grammar rule (AND, OR, EQUAL, LIKE) -- evaluated by the
  query engine walking the tree.
- **Arithmetic calculators (spreadsheets):** An Excel formula
  `=A1+SUM(B1:B10)*3` is parsed into an AST where each node
  is an Interpreter -- the cell reference node fetches the
  value; the SUM node iterates the range.
- **Unix shell pipelines:** `ls | grep .java | wc -l` is
  an interpreted pipeline AST -- each command is a grammar
  term; `|` is the composition operator.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The GoF specifically warned in "Design Patterns" that Interpreter
should not be used for complex grammars: "If the grammar is
large, other tools such as parser generators are more
appropriate." Despite this clear GoF advisory, developers
continued to implement hand-rolled Interpreters for non-trivial
grammars for years. ANTLR's wide adoption validated the GoF
warning: modern parser generators generate the same recursive
structure as Interpreter but with far less boilerplate and
with built-in error recovery. The pattern's canonical use
is now educational -- showing how grammars map to class
hierarchies -- rather than production DSL implementation.""",

        "q3": """\

**Q3 (Design Trade-off):** A team must evaluate user-defined
filter expressions like `age > 18 AND (country = 'US' OR
premium = true)` against a stream of user objects. Compare:
(1) Interpreter pattern with a class per grammar rule,
(2) a parser using a library like ANTLR, (3) embedding a
scripting engine (Groovy, MVEL). State the decision criteria
for each approach.

*Hint: The AVOID WHEN criteria in the Quick Reference Card
and the Level 4 explanation both address grammar complexity
thresholds. Map each option to the correct complexity tier.*"""
    },

    "DPT-022": {
        "evolution": """\
**EVOLUTION:**
Iterator was formalised as a pattern in the GoF book (1994)
for navigating aggregate objects without exposing internals.
Java incorporated it directly into the language: the
`Iterable`/`Iterator` interfaces (Java 1.2) and the enhanced
for-loop (Java 5) made Iterator a language primitive rather
than an application pattern. Java 8 Streams are lazy iterators
with functional operators. Reactive streams (`Publisher`/
`Subscriber` in Project Reactor) inverted the model: instead
of the caller pulling elements (Iterator), the producer
pushes elements (Observer) with back-pressure control.
Today Iterator is one of the most transparent patterns --
invisible in the language but ubiquitous.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decouple traversal from the aggregate structure. The caller
should not need to know whether the collection is an array,
a tree, or a database cursor -- it asks for the next element
using a uniform interface.

**Where else this pattern appears:**
- **Database cursors (JDBC `ResultSet`):** `rs.next()` advances
  the cursor one row at a time -- the caller doesn't know if
  results come from a single table or a complex join across
  network partitions.
- **File system walk (Files.walk()):** Java's `Files.walk()`
  returns a `Stream<Path>` -- the caller iterates paths lazily
  without knowing tree depth or traversal order implementation.
- **Kafka consumer poll():** `consumer.poll(Duration)` returns
  a batch of records -- the caller doesn't know partition count,
  offset positions, or rebalance state.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's enhanced for-loop (`for (T item : collection)`) is
syntactic sugar that the compiler transforms into an explicit
Iterator usage: it calls `collection.iterator()` and then
`hasNext()`/`next()` in a while loop. Every Java developer
uses this transformation daily but few realize the language
feature is built on Iterator. The implication: any class
you write that implements `Iterable<T>` can participate in
the for-each loop -- making Iterator one of the few GoF
patterns that is directly embedded in compiler transformation
rules in a major language.""",

        "q3": """\

**Q3 (Design Trade-off):** A data pipeline processes 10M
records from a database. Option A: load all records into
a `List<Record>`, return an `Iterator<Record>`. Option B:
use a JDBC `ResultSet` as the iterator, streaming rows
one at a time. Option C: use Java 8 `Stream` with lazy
evaluation connected to the JDBC cursor. Compare the
three on memory consumption, error handling, and composability.

*Hint: The WHAT CHANGES AT SCALE section and How It Works
both cover lazy vs. eager iteration. Map each approach
to the execution model and identify where back-pressure
control is and isn't possible.*"""
    },

    "DPT-023": {
        "evolution": """\
**EVOLUTION:**
Mediator's classical form -- centralising interactions between
UI components -- declined as reactive and data-binding frameworks
(Angular, React) provided declarative state management. The
pattern's core concept migrated to: message brokers (Kafka,
RabbitMQ as infrastructure mediators), CQRS command buses
(Spring's `CommandGateway`), and event buses. Redux (React
state management) is a Mediator: the store mediates between
actions and reducers, ensuring all state changes go through
one central point. Spring's `ApplicationEventPublisher` is
a built-in Mediator for intra-application events.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When components or services need to communicate in complex
many-to-many patterns, introduce a central coordinator that
owns the communication logic. Components speak only to the
mediator; the mediator knows the routing.

**Where else this pattern appears:**
- **Air traffic control (ATC):** Aircraft communicate only with
  ATC, not with each other -- the controller mediates all
  routing decisions, preventing collision from uncoordinated
  direct communication.
- **Message brokers (Kafka):** Producers and consumers don't
  know about each other -- the broker mediates asynchronous
  delivery, partitioning, and offset management.
- **Redux store:** React components dispatch actions to the
  store (mediator); the store calls reducers and notifies
  subscribers -- no component communicates directly with another.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Mediator pattern and the Service Bus / Message Broker
are architecturally identical -- the difference is purely one
of scale. A Mediator is a class-level coordinator inside a
process; a Service Bus is a network-level coordinator between
processes. This means teams that adopt an ESB (Enterprise
Service Bus) or message broker have, knowingly or not, scaled
the Mediator pattern to infrastructure. The well-known problem
with enterprise ESBs ("the ESB becomes a God Object") is
the distributed version of Mediator's own failure mode:
the mediator accumulates too much logic and becomes a
bottleneck.""",

        "q3": """\

**Q3 (Design Trade-off):** A monolith uses an in-process
`EventBus` (Mediator) for all inter-module communication.
The team is splitting the monolith into microservices. They
must decide: (1) keep the event bus in-process within each
service, (2) use Kafka as an inter-service event bus, or
(3) use direct REST calls. State the decision criteria and
map each approach to the correct interaction pattern.

*Hint: The WHAT CHANGES AT SCALE section addresses this
directly. Consider what happens to the Mediator when the
"colleagues" are on different servers with network partitions
between them.*"""
    },

    "DPT-024": {
        "evolution": """\
**EVOLUTION:**
Memento was the definitive undo/redo pattern in pre-command-
sourcing applications. As event sourcing and CQRS (2000s-2010s)
matured, storing the full command history became the preferred
alternative to storing state snapshots -- commands are more
compact and composable. Memento survives in: browser History
API (pushState/popState), game save states, text editor undo
stacks (with snapshot compression), and IDE incremental build
state caches. Persistent/immutable data structures (as in
Clojure, Immutable.js) achieve Memento semantics structurally
by sharing unchanged subtrees between snapshots.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you need to restore an object to a previous state,
capture the state as an opaque snapshot at the important
checkpoint. Store the snapshots externally from the object.
Restoration is simply replacing current state with the snapshot.

**Where else this pattern appears:**
- **Database SAVEPOINT/ROLLBACK:** A `SAVEPOINT` is a Memento --
  a named snapshot of transaction state. `ROLLBACK TO SAVEPOINT`
  restores the snapshot. The transaction log is the sequence of Mementos.
- **Virtual machine snapshots (VMware, VirtualBox):** A VM
  snapshot captures entire machine state -- RAM, disk, CPU
  registers -- as a Memento. Restore = load the snapshot.
- **Git stash:** `git stash` captures the working directory
  state as a Memento; `git stash pop` restores it -- the
  stash stack is a sequence of state snapshots.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Git's entire data model is essentially a persistent Memento
system. Every commit is a Memento (snapshot of the full repo
tree state), not a diff -- Git stores the complete file tree
hash at each commit, not the changes between commits.
The apparent efficiency comes from content-addressable storage:
unchanged files share the same blob object across commits.
This is why `git checkout <commit>` works in O(1) -- it's
restoring a Memento, not replaying a sequence of patches.
Git's "time travel" capability is Memento operated at
version control system scale.""",

        "q3": """\

**Q3 (Design Trade-off):** A photo editor stores Mementos
for undo. After 50 edits, the undo stack holds 50 full-
resolution image snapshots (50 × 10 MB = 500 MB of RAM).
The user closes and reopens the app; the undo history is lost.
Design a persistence strategy for the Memento stack that
reduces memory, survives restart, and maintains reasonable
undo performance.

*Hint: The WHAT CHANGES AT SCALE section addresses snapshot
size. Consider delta compression between snapshots vs.
periodic full snapshots (the same strategy databases use
for transaction logs + checkpoints).*"""
    },

    "DPT-025": {
        "evolution": """\
**EVOLUTION:**
Observer began as a synchronous, in-process event notification
pattern in GUI frameworks (Smalltalk MVC, Java Swing listeners).
As distributed systems emerged, the pattern's push model was
found insufficient: tight coupling between publisher and
subscriber, no backpressure, blocking notification. Reactive
extensions (Rx, Project Reactor, RxJava) extended Observer
with operators and backpressure control. The Reactive Streams
specification (2015) formalised the protocol. At the distributed
level, Observer became Publish-Subscribe (Kafka, SNS/SQS),
where the "subject" is a topic and observers are consumer
groups -- decoupled by a broker.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decouple state producers from state consumers. When state
changes, notify all registered observers automatically.
The producer knows nothing about who is watching or
what they do with the notification.

**Where else this pattern appears:**
- **Message brokers (Kafka, RabbitMQ):** Topics are subjects;
  consumer groups are observers -- completely decoupled, with
  persistence and replay as bonuses over in-process Observer.
- **Spreadsheet recalculation:** When a cell value changes,
  all dependent cells (observers) recalculate automatically --
  Excel's formula engine is a multi-level Observer graph.
- **DNS cache invalidation:** DNS TTL expiry triggers cache
  invalidation across resolvers -- each resolver is an
  observer of the authoritative record's change signal.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Observer pattern is the direct ancestor of reactive
programming (RxJava, Project Reactor), but the key insight
of reactive streams -- **backpressure** -- inverts Observer's
fundamental push model. In GoF Observer, the subject pushes
updates at its own pace; observers must consume as fast as
they arrive. When a slow observer cannot keep up, the queue
grows unbounded and OutOfMemoryError follows. Backpressure
allows observers to signal their capacity to the producer.
This single addition transforms Observer from "useful in
simple cases" to "usable in production data pipelines" --
making `Flux` vs. `Observable` not an API difference but
a fundamental architectural shift.""",

        "q3": """\

**Q3 (Design Trade-off):** A `StockPriceService` has 1,000
subscribers, each a different business workflow. A price
update fires 1,000 synchronous observer callbacks. During
a market spike, price updates arrive at 500/second, causing
500,000 callback invocations/second in a single thread.
Trace the failure mode and redesign the system to handle
this without losing any event while maintaining order
guarantees.

*Hint: The CONCURRENCY & DISTRIBUTED IMPLICATIONS section
addresses this directly. The solution space is: async
notification, bounded queues, and the Kafka topic model
as a decoupled alternative.*"""
    },

    "DPT-026": {
        "evolution": """\
**EVOLUTION:**
State was used in early game development and protocol
implementation for explicit finite state machine modelling.
Java's `enum` with abstract methods (Java 5+) became the
idiomatic State implementation, replacing subclass-heavy
structures. Modern event-driven systems use state machines
at the infrastructure level: Spring State Machine framework,
AWS Step Functions, and Akka FSM. XState (JavaScript) made
state machines mainstream in frontend development.
Saga patterns in distributed systems use explicit state
machines to track long-running transaction phases -- a
scaled-up State pattern.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When an object's behaviour changes based on its current
state, make the states explicit objects rather than
scattering `if/switch` statements throughout the codebase.
The state graph becomes the design documentation.

**Where else this pattern appears:**
- **TCP connection lifecycle:** A TCP socket transitions through
  LISTEN → SYN_SENT → ESTABLISHED → CLOSE_WAIT → CLOSED states,
  each with different legal operations -- the kernel implements
  this as an explicit state machine.
- **Order lifecycle (e-commerce):** PENDING → PAID → FULFILLING
  → SHIPPED → DELIVERED → RETURNED -- each state permits
  different actions (cancel is allowed in PENDING, not SHIPPED).
- **CI/CD pipeline stages:** QUEUED → RUNNING → PASSED/FAILED →
  CANCELLED -- the pipeline engine enforces valid transitions
  and triggers appropriate webhooks per state.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Every `enum` in Java with abstract methods is an implicit
State pattern implementation. Java's enum can define abstract
methods that each enum constant overrides -- this is exactly
the State pattern's "each ConcreteState overrides the
behavior" mechanism. `enum Planet { MERCURY { double weight(
double mass) {...} }, VENUS { double weight(double mass) {...}
} }` is a State pattern where the "state" is the planet and
"behaviour" is the gravity calculation. This means Java enums
are both value types and State pattern implementations
simultaneously -- a dual nature most Java developers overlook.""",

        "q3": """\

**Q3 (Design Trade-off):** An `Order` state machine has
5 states and 8 transitions. A requirement says: any state
transition must be logged with the old state, new state,
timestamp, and actor ID. Using the State pattern as the
base, describe two ways to add this cross-cutting logging
requirement and compare the approaches on coupling and testability.

*Hint: Option 1: add logging inside each concrete state's
transition method. Option 2: use the State pattern with an
AOP/Decorator layer around transitions. The Proxy and
Decorator patterns (DPT-018, DPT-015) apply here.*"""
    },

    "DPT-027": {
        "evolution": """\
**EVOLUTION:**
Strategy was a cornerstone pattern for algorithm substitution
in pre-lambda Java. The explicit Strategy interface + multiple
ConcreteStrategy classes became boilerplate-heavy. Java 8
(2014) transformed Strategy: a `Comparator` lambda replaces
a `ComparatorStrategy` class; a sorting algorithm is passed
as a `Function`. Template Method's static structure gave
way to Strategy's dynamic composition. Modern Java uses
`java.util.function` interfaces (Predicate, Function,
Consumer) as single-method Strategy contracts. Spring's
`ResourceLoader`, `TransactionManager`, and `CacheManager`
are injectable Strategy interfaces used throughout the framework.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the algorithm (the how) from the context that uses
it (the what). Express the algorithm as a first-class value
that can be substituted at runtime. The context becomes
algorithm-agnostic.

**Where else this pattern appears:**
- **Sorting algorithms:** `List.sort(comparator)` accepts any
  `Comparator` -- `naturalOrder()`, `reverseOrder()`, or a
  custom multi-key comparator. The list's sort mechanism is
  the context; the comparator is the strategy.
- **Payment processing:** A `PaymentService` accepts a
  `PaymentStrategy` -- `StripeStrategy`, `PayPalStrategy`,
  `CryptoStrategy`. The processing workflow is fixed; the
  payment mechanism is substitutable.
- **Compression utilities (zip, gzip, brotli):** I/O stream
  compressors accept a `Codec` strategy -- the stream wrapper
  is fixed; the compression algorithm is substituted per format.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java 8 lambdas made Strategy so lightweight that many developers
stopped recognising it as a pattern. `list.sort((a, b) ->
a.age - b.age)` is a Strategy pattern -- the lambda is a
`Comparator` (concrete strategy), passed to `sort()` (the
context). The pattern did not disappear with lambdas; it became
invisible because Java's functional interface mechanism
eliminates the need for an explicit strategy class. The lesson:
patterns manifest differently in different language generations.
In Java 14+, `switch` expressions with sealed interfaces can
replace Strategy entirely for finite algorithm sets -- the
pattern evolves as the language evolves.""",

        "q3": """\

**Q3 (Design Trade-off):** A `ReportGenerator` uses Strategy
to select between PDF, Excel, and HTML output formats. A new
requirement: "generate all three formats simultaneously."
Modify the design to support multi-strategy execution, then
evaluate whether the result is still Strategy or has evolved
into Composite, Observer, or a different pattern.

*Hint: The First Principles CORE INVARIANTS say one strategy
is selected at a time. When multiple strategies execute
simultaneously, the context has changed -- map this to the
Composite pattern (DPT-014) or a collection-based dispatcher.*"""
    },

    "DPT-028": {
        "evolution": """\
**EVOLUTION:**
Template Method was the dominant "framework extension hook"
pattern before Java interfaces gained default methods (Java 8)
and dependency injection became mainstream. Many Java EE
lifecycle hooks (`init()`, `destroy()` in servlets) are
Template Method variants. Spring's `JdbcTemplate`,
`RestTemplate`, and `TransactionTemplate` all follow the
pattern -- the template handles the invariant parts
(connection management, error handling) and calls abstract
methods for the variable parts. Java 8 default methods on
interfaces provided an alternative: no inheritance required
for skeleton implementations.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define the invariant structure of an algorithm in one place.
Mark the variable parts as extension points. Subclasses
(or passed functions) provide only the variable parts --
never the structure.

**Where else this pattern appears:**
- **JUnit test lifecycle:** `@BeforeAll → @BeforeEach →
  @Test → @AfterEach → @AfterAll` is a template method --
  JUnit defines the structure; your test class fills in
  the `@Test` body.
- **Spring `JdbcTemplate`:** The template manages
  connection acquisition, statement compilation, result
  processing, connection release. The caller provides only
  the SQL and the row mapper -- the variable parts.
- **HTML template engines (Thymeleaf, Freemarker):** The
  template defines the page structure with placeholders;
  the "extension points" are filled at render time with
  model data.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Spring's most important classes -- `JdbcTemplate`,
`RestTemplate`, `TransactionTemplate`, `HibernateTemplate` --
are named "Template" specifically because they implement the
Template Method pattern. This naming convention is consistent
enough that "Template" in a Spring class name reliably signals
Template Method: the class handles boilerplate lifecycle code
and calls your code at the variable points. Ironically,
`RestTemplate` (deprecated) was replaced by `WebClient`
precisely because the Template Method structure (subclass
to override) didn't compose well with reactive/async code --
revealing the pattern's fundamental limitation when
asynchronous composition is required.""",

        "q3": """\

**Q3 (Design Trade-off):** Spring's `JdbcTemplate` uses
Template Method for database operations. For reactive
database access, the team uses R2DBC's `DatabaseClient`,
which uses a functional/builder style instead of template
inheritance. Map the Template Method roles to the functional
equivalent in `DatabaseClient` and explain why reactive
programming requires replacing Template Method with a
function-composition model.

*Hint: Template Method requires blocking on steps; async
requires non-blocking composition. The Level 4 explanation
hints at this. Strategy (lambda) applied at each step
replaces the overrideable method in the async world.*"""
    },

    "DPT-029": {
        "evolution": """\
**EVOLUTION:**
Visitor was designed to add operations to class hierarchies
without modifying them -- critical when you cannot change
the element classes. Java's `instanceof` operator (and later
`switch` with `instanceof` in Java 16+, sealed classes in
Java 17) provided a syntactically simpler alternative for
simple cases. Compilers heavily use Visitor for AST traversal
(type checking, code generation, optimisation passes). Java's
`javax.annotation.processing` API uses Visitor for annotation
processing. javax.lang.model's `TypeVisitor` and
`ElementVisitor` are textbook Visitor implementations
embedded in the Java compiler infrastructure.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you need to add many distinct operations to a stable
type hierarchy without modifying the types, externalise
the operations into a visitor. The types accept the visitor;
the visitor implements the operation for each type.

**Where else this pattern appears:**
- **Compiler AST passes:** A Java compiler applies separate
  Visitor passes over the AST for: parsing, name resolution,
  type checking, bytecode generation -- each is a visitor;
  the AST nodes are elements.
- **JSON serialization (Jackson):** `ObjectMapper` traverses
  object graphs using a visitor-like mechanism -- each field
  type is "visited" and serialised according to its type.
- **CSS selector matching (browser rendering engine):** The
  rendering engine visits each DOM node, applying matched
  CSS rules -- the DOM nodes accept the style visitor.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java 21's pattern matching for switch -- `switch (shape) {
case Circle c -> ...; case Rectangle r -> ...; }` -- is the
language's native alternative to Visitor for sealed type
hierarchies. The Java language designers added it specifically
because Visitor's double-dispatch mechanism is "ugly and
fragile." Sealed classes + pattern matching switches provide
exhaustiveness checking (the compiler warns if you miss a
case) and type narrowing -- both things Visitor achieves at
the cost of significant boilerplate. Java is the first major
OOP language to formally acknowledge that Visitor is a
workaround for a language limitation.""",

        "q3": """\

**Q3 (Design Trade-off):** A document model has nodes:
`Paragraph`, `Heading`, `Image`, `Table`, `TableRow`,
`TableCell`. Operations needed: (1) render to HTML,
(2) render to PDF, (3) extract all text for indexing,
(4) count words. Java 17 sealed classes make the hierarchy
closed. Compare implementing these as: (a) 4 separate
Visitor classes, (b) 4 `switch` expressions on the sealed
type, (c) virtual dispatch methods on each node class.
State when each is the best choice.

*Hint: The Comparison Table and Level 4 address open vs.
closed extension -- the key is how often nodes are added
(favouring virtual dispatch) vs. how often operations
are added (favouring Visitor).*"""
    },

    "DPT-030": {
        "evolution": """\
**EVOLUTION:**
Null Object appeared as a named pattern after decades of
null-check proliferation in object-oriented code. Java's
`Optional<T>` (Java 8) provided a stdlib alternative for
return values: `Optional.empty()` plays the Null Object
role without requiring a domain class. The two approaches
have different applicability: `Optional` is for values that
might be absent (return types); Null Object is for objects
that must always be callable (dependencies and collaborators).
Modern languages (Kotlin, Swift, Rust) with null safety
built into the type system reduce Null Object's need by
making the null case explicit at the type level.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Replace null checks with default behaviour. Provide an
implementation that performs no-op or safe default logic
when a real implementation is absent. Callers are freed
from knowing whether the object is "real" or "absent."

**Where else this pattern appears:**
- **`Collections.emptyList()`:** Returns a list that is
  always iterable, always has `size() == 0`, and always
  throws on mutations -- a Null Object for lists.
- **`NoOpLogger` (logging):** A logger that discards all
  messages -- used in tests to silence output without
  changing the code under test.
- **`VoidFuture`:** A `CompletableFuture` that is already
  completed with no value -- used to satisfy APIs that
  require a `Future` but where no async work is actually needed.""",

        "surprise": """\
---

### 💡 The Surprising Truth

`Optional<T>` in Java is not a Null Object -- it is a wrapper
that _represents the possible absence_ of a value. The critical
difference: Null Object replaces the null _entirely_ with a
callable object; `Optional` still requires the caller to
check for absence (via `isPresent()` or `ifPresent()`). Using
`Optional` where Null Object is appropriate still distributes
null-checking logic to callers, just with a different syntax.
The correct choice depends on whether absence should be
_handled_ by the caller (use `Optional`) or _ignored_ by the
caller with safe default behaviour (use Null Object).""",

        "q3": """\

**Q3 (Design Trade-off):** A payment system uses Null Object:
`NoOpFraudDetector implements FraudDetector` replaces null
when fraud detection is disabled. A security audit requires
that every place fraud detection is skipped must be audited.
This means the no-op cannot truly be silent. Describe how
to modify the Null Object to satisfy the audit requirement
while preserving the caller's ignorance of which implementation
is active.

*Hint: The Null Object is allowed to do *something* -- it
just shouldn't represent absence of behaviour. An auditing
no-op that logs "fraud check skipped" is still a valid
Null Object. Consider the Decorator pattern (DPT-015)
wrapping the Null Object.*"""
    },
}

def get_invention_moment_end(content):
    """Find the end of THE INVENTION MOMENT paragraph."""
    # Find THE INVENTION MOMENT section
    pos = content.find("**THE INVENTION MOMENT:**")
    if pos == -1:
        return -1
    # Find the next --- or ### after it
    after = content.find("\n\n---", pos)
    after2 = content.find("\n\n### ", pos)
    if after == -1 and after2 == -1:
        return -1
    if after == -1:
        return after2
    if after2 == -1:
        return after
    return min(after, after2)

def insert_evolution(content, evolution_text):
    """Insert EVOLUTION after THE INVENTION MOMENT paragraph."""
    # Check if already has EVOLUTION
    if "**EVOLUTION:**" in content:
        return content

    pos = get_invention_moment_end(content)
    if pos == -1:
        print("  WARNING: Could not find insertion point for EVOLUTION")
        return content

    return content[:pos] + "\n\n" + evolution_text + content[pos:]

def insert_wisdom_and_surprise(content, dpt_id, wisdom_text, surprise_text):
    """Insert Transferable Wisdom and Surprising Truth before Think section."""
    if "### 💎 Transferable Wisdom" in content:
        return content

    think_pos = content.find("### 🧠 Think About This Before We Continue")
    if think_pos == -1:
        print(f"  WARNING: Could not find Think section")
        return content

    # Find the --- before Think
    pre_think = content.rfind("\n---\n", 0, think_pos)
    if pre_think == -1:
        insert_pos = think_pos
    else:
        insert_pos = pre_think + 1  # after the \n

    insert_text = "\n" + wisdom_text + "\n\n" + surprise_text + "\n"

    return content[:insert_pos] + insert_text + content[insert_pos:]

def fix_think_section(content, q3_text):
    """Add Q3 and hints to Think About This section."""
    if "*Hint:" in content:
        return content  # Already has hints

    think_pos = content.find("### 🧠 Think About This Before We Continue")
    if think_pos == -1:
        return content

    # Find the end of the Think section (end of file or next section)
    next_section = content.find("\n---\n", think_pos)
    if next_section == -1:
        # End of file
        section_content = content[think_pos:]
        rest = ""
        section_end = len(content)
    else:
        section_content = content[think_pos:next_section]
        rest = content[next_section:]
        section_end = next_section

    # Find Q1 and Q2, add hints after each
    new_section = section_content

    # Add hint after Q1
    q1_end = new_section.find("\n\n**Q2.")
    if q1_end == -1:
        q1_end = new_section.find("\n\n**Q2 ")
    if q1_end != -1:
        q1_text = new_section[:q1_end]
        hint1 = "\n\n*Hint: Look at the First Principles section for the core invariants, " \
                "and the Failure Modes section for where this scenario appears as a documented issue.*"
        new_section = q1_text + hint1 + new_section[q1_end:]

    # Re-find Q2 end after modification
    q2_start = new_section.find("**Q2.")
    if q2_start == -1:
        q2_start = new_section.find("**Q2 ")
    if q2_start != -1:
        # Find end of Q2 (next blank line at end of paragraphs, or end)
        q2_end = new_section.find("\n\n\n", q2_start)
        if q2_end == -1:
            q2_end = len(new_section)
        hint2 = "\n\n*Hint: The Comparison Table and the Level 3-4 explanations " \
                "contain the mechanism that determines which approach wins in this scenario.*"
        new_section = new_section[:q2_end] + hint2 + new_section[q2_end:]

    # Add Q3
    new_section = new_section.rstrip() + "\n" + q3_text + "\n"

    return content[:think_pos] + new_section + rest

def process_file(dpt_id, data):
    fname = None
    for f in os.listdir(BASE):
        if f.startswith(dpt_id + " "):
            fname = f
            break

    if not fname:
        print(f"File not found for {dpt_id}")
        return

    fpath = os.path.join(BASE, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Add EVOLUTION
    content = insert_evolution(content, data["evolution"])

    # 2. Add Wisdom + Surprise
    content = insert_wisdom_and_surprise(content, dpt_id, data["wisdom"], data["surprise"])

    # 3. Fix Think section
    content = fix_think_section(content, data["q3"])

    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"UPDATED: {fname}")
    else:
        print(f"NO CHANGE: {fname}")

if __name__ == "__main__":
    for dpt_id, data in CONTENT.items():
        print(f"\nProcessing {dpt_id}...")
        process_file(dpt_id, data)

    print("\nBatch 1 complete!")

