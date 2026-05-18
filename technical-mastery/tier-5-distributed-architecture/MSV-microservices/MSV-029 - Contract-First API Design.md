---
id: MSV-029
title: Contract-First API Design
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-012, MSV-002, MSV-070
used_by: MSV-026, MSV-027, MSV-028, MSV-061
related: MSV-026, MSV-027, MSV-028, MSV-061, MSV-070
tags:
  - microservices
  - api
  - intermediate
  - design
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/microservices/contract-first-api-design/
---

⚡ TL;DR - Contract-First API Design means the API
contract (OpenAPI spec, gRPC proto, Avro schema) is
defined and agreed BEFORE any implementation begins.
The contract becomes the single source of truth: code
is generated from it, tests are derived from it, and
both provider and consumer teams work from it in parallel.
This is the inverse of "code-first" (implement first,
generate spec from annotations).

| #029 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | API Gateway, Microservices Architecture, Service Contract | |
| **Used by:** | Backward Compatibility, Versioning Strategy, Microservices Testing Strategy, Consumer-Driven Contract Testing | |
| **Related:** | Backward Compatibility, Versioning Strategy, Microservices Testing Strategy, Consumer-Driven Contract Testing, Service Contract | |

---

### 🔥 The Problem This Solves

**CODE-FIRST ANTI-PATTERN IN MICROSERVICES:**
Order Service needs an endpoint from Payment Service.
Payment team implements the endpoint (code-first: code
first, annotate for OpenAPI). Three weeks later:
Order Service integrates. Discovers that the field is
`amount_cents` (Integer) but Order Service expected
`amount` (BigDecimal dollars). Payment Service PUT
accepts a `currency` field Order Service doesn't send.
Two teams wasted partial integration work. Payment
team must change the API (or Order Service must
adapt). The discovery of the mismatch happens at
integration time - the most expensive moment.

**CONTRACT-FIRST SOLUTION:**
Before any code is written, both teams write the OpenAPI
spec together. Field names, types, required vs optional,
error responses are all agreed in a 1-hour design review.
API spec is committed to Git. Order Service team generates
client stubs from the spec immediately and begins
development. Payment Service team generates server stubs
and implements the endpoint. Both teams can work in
parallel. Integration is smooth because both implemented
the same spec.

---

### 📘 Textbook Definition

**Contract-First API Design** is an approach to service
development where the API interface specification (the
"contract") is designed and documented before any
implementation code is written. The contract defines:
all endpoints, request/response formats, status codes,
error formats, and authentication. Technologies:
OpenAPI 3.0 (REST), Protocol Buffers (gRPC), AsyncAPI
(event-driven), Avro (Kafka). The contract serves as:
the team agreement document, the input to code generators
(server stubs, client SDKs), the basis for contract tests,
and the API documentation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Contract-First means: agree on the API spec first,
then everyone builds to that spec - no surprises
at integration time.

**One analogy:**
> A construction project: the architect draws the blueprint
> (API contract) before any construction begins. Plumbers,
> electricians, and carpenters all work from the same
> blueprint simultaneously. No one discovers at assembly
> time that the plumbing holes don't match the electrical
> conduit positions. The blueprint is the single source
> of truth. Code-First is like each contractor designing
> their own section without coordination: integration
> problems guaranteed.

**One insight:**
The primary benefit is not the contract itself - it's
the forcing function to have the design conversation
before any code is written. Once code exists, design
decisions become legacy decisions ("we can't change it,
other services already depend on it"). Before code
exists, the design is free to be optimal.

---

### 🔩 First Principles Explanation

**CONTRACT-FIRST vs CODE-FIRST:**

```
CODE-FIRST WORKFLOW:
  1. Implement endpoint (Spring Boot controller)
  2. Add SpringDoc/Swagger annotations (@Operation,
    @Schema)
  3. Generate OpenAPI spec from annotations
  4. Share spec with consumers
  5. Consumers build to spec
  
  PROBLEM: Design decisions baked in before review.
  Spec is generated from code: spec accuracy depends on
  annotation completeness. Annotations drift (code changed,
  annotation not updated -> spec wrong). Consumer teams
  start late (waiting for spec). Discovery of design
  issues: late (at integration time).

CONTRACT-FIRST WORKFLOW:
  1. Design API spec (OpenAPI YAML) collaboratively
  2. Review spec with consumer teams
  3. Commit spec to Git
  4. Generate server stubs from spec (openapi-generator)
  5. Generate client SDKs from spec (both teams)
  6. Implement server stubs (business logic only)
  7. Consumer team uses generated client SDK
  8. Contract tests validate implementation matches spec
  
  BENEFIT: Both teams develop in parallel.
  Design reviewed before implementation (cheap to change).
  Spec is the truth (code must match spec, not spec
  generated from possibly-wrong code annotations).
  Breaking change detection: compare old spec to new spec
  (openapi-diff) - automated in CI.
```

**WHAT THE CONTRACT DEFINES:**

```yaml
# OpenAPI 3.0 contract (excerpt)
openpai: '3.0.3'
info:
  title: Payment API
  version: '1.0'
paths:
  /api/v1/payments:
    post:
      operationId: createPayment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreatePaymentRequest'
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaymentResponse'
        '400':
          description: Validation error
        '422':
          description: Payment processing failed
components:
  schemas:
    CreatePaymentRequest:
      type: object
      required: [orderId, amount, currency]
      properties:
        orderId:
          type: string
          format: uuid
        amount:
          type: number
          format: double
          minimum: 0.01
        currency:
          type: string
          enum: [USD, EUR, GBP]
    PaymentResponse:
      type: object
      required: [paymentId, status]
      properties:
        paymentId:
          type: string
          format: uuid
        status:
          type: string
          enum: [PENDING, PROCESSING, COMPLETED, FAILED]
```

---

### 🧪 Thought Experiment

**PARALLEL DEVELOPMENT ENABLED BY CONTRACT-FIRST:**

```
WEEK 1:
  Order + Payment team: 2-hour contract design session
  Output: payment-api.yaml committed to Git
  
  Order Service team:
    openapi-generator generate -g java \
      -i payment-api.yaml \
      --library=feign
    # Client SDK generated: PaymentApiClient.java
    # Order Service can write unit tests with mocked client
    # Development starts immediately
  
  Payment Service team:
    openapi-generator generate -g spring \
      -i payment-api.yaml
    # Server stub generated: PaymentApiDelegate.java
    # Team implements business logic in delegate
    # No API design decisions needed - contract is fixed

WEEK 4:
  Both teams complete independently
  Integration: Order Service's client SDK calls
  Payment Service's controller - same spec, no mismatch

VS CODE-FIRST WITHOUT CONTRACT:
  Week 1-3: Payment team implements endpoint
  Week 4: Payment team generates spec, shares with Order
    team
  Week 5: Order team discovers field name issue
  Week 5-6: Payment team changes API, Order team
    re-integrates
  Week 7: Working integration
  => 3 weeks slower, design mismatch cost
```

---

### 🧠 Mental Model / Analogy

> Contract-First is the API equivalent of Test-Driven
> Development (TDD). In TDD: write the test (desired
> behaviour) first, then implement the code to make the
> test pass. In Contract-First: write the API spec
> (desired interface) first, then implement the code to
> match the spec. Both approaches share the key benefit:
> they force you to think about the desired outcome
> before you commit to an implementation - when changes
> are cheapest.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Contract-First means you write down exactly how your
API will work (what URL, what fields, what responses)
before you start coding. Everyone agrees on the "rules"
first, then builds to those rules.

**Level 2 - How to use it (junior developer):**
Create an OpenAPI YAML file. Review it with the consumer
team. Check it into Git. Use `openapi-generator` to
generate client stubs (for consumers) and server stubs
(for providers). Implement the server stub's delegate
interface with your business logic.

**Level 3 - How it works (mid-level engineer):**
In a Spring Boot project: (1) Create `src/main/resources/
api/payment-api.yaml`. (2) Add `openapi-generator-maven-
plugin` to pom.xml. (3) Configure the plugin: generate
spring stubs with `delegatePattern=true`. (4) The
`PaymentApiDelegate` interface is generated - implement
it. (5) The controller, request/response models are
generated - do not edit them. (6) CI adds openapi-diff:
calculate diff between current spec and PR spec, fail
build if breaking change detected. (7) Spec-first:
annotations on the generated code must match the spec;
if not, the spec is wrong and needs updating.

**Level 4 - Why it was designed this way (senior/staff):**
Contract-First solves the "consumer-provider coupling at
design time" problem. In microservices: consumer teams
need to start development before the provider implements.
Code-First forces sequential development (provider first,
consumer after spec is available). Contract-First enables
parallel development. For internal APIs with known
consumers, this is valuable. For public APIs with
unknown consumers, it's essential: you cannot change
public APIs without versioning, so designing the contract
correctly before release is critical.

**Level 5 - Mastery (distinguished engineer):**
Beyond REST/OpenAPI: AsyncAPI for event-driven microservices.
Kafka topic contracts defined in AsyncAPI spec before
producers and consumers are implemented. Schema Registry
(Confluent, AWS Glue) enforces schema compatibility:
consumers' Avro schema compatibility mode (BACKWARD,
FORWARD, FULL) is checked at publish time. Contract-First
for events: define the event schema (Avro or JSON Schema),
register in schema registry, generate producer and
consumer stubs. This extends contract-first from HTTP
APIs to event-driven messaging.

---

### ⚙️ How It Works (Mechanism)

**OPENAPI GENERATOR IN SPRING BOOT (pom.xml):**

```xml
<plugin>
  <groupId>org.openapitools</groupId>
  <artifactId>openapi-generator-maven-plugin</artifactId>
  <version>7.2.0</version>
  <executions>
    <execution>
      <id>generate-payment-api</id>
      <goals><goal>generate</goal></goals>
      <configuration>
        <inputSpec>${project.basedir}/src/main/resources/
          api/payment-api.yaml</inputSpec>
        <generatorName>spring</generatorName>
        <configOptions>
          <delegatePattern>true</delegatePattern>
          <useSpringBoot3>true</useSpringBoot3>
          <interfaceOnly>false</interfaceOnly>
          <useTags>true</useTags>
          <dateLibrary>java8</dateLibrary>
        </configOptions>
        <apiPackage>com.example.api</apiPackage>
        <modelPackage>com.example.model</modelPackage>
      </configuration>
    </execution>
  </executions>
</plugin>
```

```java
// Generated interface (DO NOT EDIT)
public interface PaymentApiDelegate {
    ResponseEntity<PaymentResponse> createPayment(
        CreatePaymentRequest request);
}

// YOUR implementation (only business logic here)
@Service
public class PaymentApiDelegateImpl
        implements PaymentApiDelegate {

    private final PaymentService paymentService;

    @Override
    public ResponseEntity<PaymentResponse> createPayment(
            CreatePaymentRequest request) {
        Payment p = paymentService.create(
            request.getOrderId(),
            request.getAmount(),
            request.getCurrency().getValue());
        return ResponseEntity.status(201)
            .body(PaymentResponse.from(p));
    }
}
// The controller is generated - no @RequestMapping needed
// URL, HTTP method, request/response types all in spec
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CONTRACT-FIRST DEVELOPMENT LIFECYCLE:**

```
1. DESIGN SESSION (both teams, 1-2 hours):
   - Define endpoints, request/response schemas
   - Agree on field names, types, required/optional
   - Define error responses (400, 404, 422, 500)
   - Output: payment-api.yaml

2. CONTRACT REVIEW (async, 24-48 hours):
   - PR in shared API spec repository
   - Consumer teams review: does this meet our needs?
   - API design team review: consistent with other APIs?
   - Changes agreed before merging

3. PARALLEL DEVELOPMENT:
   Provider: implement PaymentApiDelegate
   Consumer: generate client from spec, write unit tests
             with mocked client

4. CONTRACT TESTS:
   Pact consumer tests derived from spec expectations
   Provider CI: runs consumer Pact tests against
                implementation to verify spec compliance

5. SPEC EVOLUTION (CI gate):
   PR to change spec: openapi-diff detects breaking changes
   Breaking change: must follow versioning policy
   Non-breaking: no version bump needed
   All consumers' Pact tests must pass

6. DOCUMENTATION:
   Spec published to developer portal (Stoplight,
     SwaggerUI)
   Auto-generated from committed YAML: always current
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: code-first vs contract-first**

```java
// BAD: Code-First - implementation drives the contract
@RestController
@RequestMapping("/payments")
public class PaymentController {
    @PostMapping
    @Operation(summary = "Create payment")  // annotation AFTER code
    public PaymentDTO createPayment(
            @RequestBody CreatePaymentDTO dto) {
        // Implementation details drive API shape
        // Consumers must wait for this to be implemented
        // and annotated before they can start
        // No design review opportunity before code is written
    }
}
// Problem: spec generated from annotations may be incomplete
// Problem: sequential - consumers can't start until provider done
// Problem: API shape decided by implementer, not consumer needs
```

```java
// GOOD: Contract-First - spec drives implementation
// 1. payment-api.yaml exists with agreed contract
// 2. Generated by openapi-generator:
//    - PaymentApiDelegate interface
//    - CreatePaymentRequest / PaymentResponse models
//    - PaymentApiController (DO NOT EDIT)
// 3. Developer only writes:
@Service
public class PaymentApiDelegateImpl
        implements PaymentApiDelegate {
    @Override
    public ResponseEntity<PaymentResponse> createPayment(
            CreatePaymentRequest request) {
        // Pure business logic - no HTTP concerns
        // Contract enforced by generated code
        // Consumer team already developing in parallel
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Contract-First | Code-First |
|---|---|---|
| **When spec is ready** | Before coding starts | After implementation |
| **Parallel development** | Yes - both teams work from spec | No - consumer waits for provider |
| **Design review** | Before code, easy to change | After code, expensive to change |
| **Spec accuracy** | Spec is truth, code verified against it | Spec generated from code (may be incomplete) |
| **Breaking change detection** | CI: diff old spec vs new spec | Manual review required |
| **Consumer SDK** | Generated from spec before provider exists | Generated after provider implements |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Contract-First means more upfront work | Contract-First moves design work earlier (before coding) and eliminates integration rework (expensive). Total work is less; it's distributed differently. The 2-hour design session replaces 2-3 weeks of integration debugging. |
| The generated code is boilerplate I need to maintain | The generated code is the framework - you never edit it (it's regenerated when the spec changes). You only write the business logic in the delegate. The generated code is the benefit, not the burden. |
| Contract-First only works for REST APIs | Contract-First applies to any inter-service contract: gRPC uses Proto files (contract-first by nature), Kafka uses AsyncAPI + Avro Schema Registry, GraphQL uses schema-first SDL. The principle is universal. |

---

### 🚨 Failure Modes & Diagnosis

**Spec drift: implementation diverges from contract**

**Symptom:**
Payment Service was contract-first. Over 6 months,
developers made small changes directly to the controller
(code-first changes) without updating the spec. The
Generated OpenAPI spec in developer portal shows
`currency: string` but the actual API now returns
`currency: {code: USD, symbol: $}` (nested object).
New consumers build to the spec. Integration fails.

**Root Cause:**
No enforcement: nothing in CI prevents implementing
beyond the contract. Developers took shortcuts,
changing response objects without updating the spec.

**Diagnostic:**
```bash
# Generate the actual spec from running service
curl http://payment-service/v3/api-docs > actual-spec.yaml
# Compare with committed spec
diff payment-api.yaml actual-spec.yaml
# Shows: currency field type diverged
```

**Permanent Fix:**
1. Add spec compliance test in CI:
   - Start service in test context
   - Generate OpenAPI from running service
   - Diff against committed spec
   - Fail build if any difference found
2. Add openapi-diff to PR process:
   - Detect any change to the spec in PR
   - Block PR if spec changed without following
     the change management process
3. Developer guidelines: all API changes must update
   spec first (contract-first discipline enforced socially
   AND by tooling)

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `API Gateway` - the gateway enforces API contracts
  and routes by version
- `Service Contract` - the formal agreement between
  service teams; contract-first produces this artifact

**Builds On This:**
- `Backward Compatibility` - contract-first enables
  automated backward compatibility checking (openapi-diff)
- `Versioning Strategy` - new API versions defined
  as new contract files
- `Microservices Testing Strategy` - contract tests
  derived from the contract spec
- `Consumer-Driven Contract Testing` - Pact tests
  are the runtime verification that implementation
  matches the contract

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WORKFLOW     │ Design spec -> review -> commit -> build │
│              │ (both teams start implementing in paralle│
├──────────────┼──────────────────────────────────────────┤
│ TOOLS        │ OpenAPI 3.0 (REST), Proto (gRPC)         │
│              │ AsyncAPI (events), Avro (Kafka)          │
│              │ openapi-generator, openapi-diff          │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Agree on API spec before writing code - │
│              │  parallel dev, no integration surprises" │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Consumer-Driven Contract Testing → Pact  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Contract-First: define OpenAPI spec before writing
   implementation code. Both teams work from the spec.
2. Use `openapi-generator` to generate server stubs
   and client SDKs - implement only the business logic.
3. CI gate: `openapi-diff` detects breaking changes
   in spec before they reach consumers.

**Interview one-liner:**
"Contract-First means the OpenAPI spec is written and
agreed before implementation. Benefit: parallel development
(consumer and provider both start from spec on day 1),
design review when changes are cheap, generated client
SDKs and server stubs from spec (implement only business
logic), and automated breaking-change detection via
openapi-diff in CI. Alternative to Code-First which
generates spec from annotations after the fact."

---

### 💡 The Surprising Truth

The most valuable aspect of Contract-First is not the
spec or the code generation - it's the conversation it
forces. When two teams sit down to write the OpenAPI
spec together before any code exists, they discover
disagreements in terminology, mental models, and
business rules that would have surfaced as bugs 4 weeks
later. "What do you mean by `amount` - is that cents
or dollars? What currency?" - this question, asked
before coding, saves a day of debugging. Asked after
4 weeks of divergent implementation, it costs a week
of rework. The contract spec is the mechanism that
makes this conversation happen at the right time.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **WRITE** Design a complete OpenAPI 3.0 spec for a
   new endpoint: paths, components/schemas, requestBody,
   responses (201, 400, 404, 422, 500), with correct
   `required` arrays and `$ref` usage.
2. **GENERATE** Configure `openapi-generator-maven-plugin`
   to generate Spring Boot delegate-pattern server stubs
   from an OpenAPI spec, and implement the delegate.
3. **ENFORCE** Set up `openapi-diff` in CI that fails
   the build when a breaking change is detected in the
   spec between the current branch and main.
4. **REVIEW** Given a PR that changes an API spec,
   classify each change as safe or breaking and explain
   the rationale.
5. **EXTEND** Apply contract-first to Kafka: write an
   AsyncAPI spec for a new event, register the Avro
   schema in Confluent Schema Registry, and generate
   producer/consumer stubs.

---

### 🧠 Think About This Before We Continue

**Q1.** Your team currently uses Code-First with
SpringDoc annotations. The API spec is often out of
date. You want to migrate to Contract-First. Design
the migration plan: how do you generate the initial
spec from the current code, validate it, commit it,
and then enforce that future changes go spec-first?

**Q2.** A new service has 3 consumers. Each consumer
has different needs from the same API. Consumer A wants
`amount` in cents, Consumer B in dollars. Design the
contract that satisfies both consumers without multiple
endpoint versions. Discuss the trade-offs between
flexibility in the spec and simplicity.

**Q3.** Your team wants to use Contract-First for a
Kafka event-driven system, not just REST APIs. Describe
how AsyncAPI and Avro Schema Registry provide contract-
first capabilities for events. How does schema registry
compatibility enforcement differ from openapi-diff for
REST APIs?