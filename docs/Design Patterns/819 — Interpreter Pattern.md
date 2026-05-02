---
layout: default
title: "Interpreter Pattern"
parent: "Design Patterns"
nav_order: 819
permalink: /design-patterns/interpreter-pattern/
number: "819"
category: Design Patterns
difficulty: ★★★
depends_on: "Composite Pattern, Visitor Pattern, Abstract Syntax Tree"
used_by: "Expression evaluators, SQL parsers, rule engines, Spring SpEL, scripting engines"
tags: #advanced, #design-patterns, #gof, #behavioral, #ast, #compiler, #expression
---

# 819 — Interpreter Pattern

`#advanced` `#design-patterns` `#gof` `#behavioral` `#ast` `#compiler` `#expression`

⚡ TL;DR — **Interpreter Pattern** (GoF behavioral) defines a grammar for a language and an interpreter that processes sentences in that grammar — representing grammar rules as classes, each with an `interpret()` method that evaluates in context.

| #819            | Category: Design Patterns                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Composite Pattern, Visitor Pattern, Abstract Syntax Tree                         |                 |
| **Used by:**    | Expression evaluators, SQL parsers, rule engines, Spring SpEL, scripting engines |                 |

---

### 📘 Textbook Definition

**Interpreter Pattern** (Gang of Four, "Design Patterns", 1994, Behavioral Patterns, pp. 243–255): given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language. Participants: AbstractExpression (`interpret(Context)`), TerminalExpression (leaf — maps to grammar terminal symbol), NonTerminalExpression (composite — contains sub-expressions, implements grammar rule), Context (global state available during interpretation). Structure: the AST (Abstract Syntax Tree) is a Composite Pattern of expression objects. Interpreter uses the Composite structure to recursively evaluate. Related: Visitor Pattern used to separate operations from AST structure; parsers (ANTLR, Yacc) generate ASTs that Interpreter then evaluates.

---

### 🟢 Simple Definition (Easy)

A rule engine for business rules: "Customer is eligible if: age > 18 AND (accountBalance > 1000 OR isPremiumMember)". Parse this expression into a tree: AND(GreaterThan(age, 18), OR(GreaterThan(balance, 1000), Equals(premium, true))). Each node is an Expression object with an `evaluate(customer)` method. `AND` evaluates left and right, returns both true. `GreaterThan` compares the field. Walk the tree and evaluate. That's the Interpreter Pattern: grammar rules as classes, evaluation as tree traversal.

---

### 🔵 Simple Definition (Elaborated)

Spring Expression Language (SpEL): `#{customer.age > 18 && (customer.balance > 1000 || customer.isPremium())}`. Spring parses this string → builds an AST → evaluates using Interpreter Pattern internally. Each operator (`>`, `&&`, `||`) is a NonTerminalExpression. Each literal (`18`, `1000`) and property access (`customer.age`) is a TerminalExpression. SpEL evaluates the tree against the provided context (the `customer` object). The Interpreter Pattern is what enables configuration-driven expression evaluation — rules defined as strings at runtime, not compiled Java code.

---

### 🔩 First Principles Explanation

**Complete Interpreter Pattern implementation: SQL WHERE clause evaluator:**

```
GRAMMAR (simplified SQL WHERE):

  Expression    := AndExpression | OrExpression | ComparisonExpression
  AndExpression := Expression 'AND' Expression
  OrExpression  := Expression 'OR' Expression
  ComparisonExpression := field operator value
  operator      := '=' | '>' | '<' | '>='

STRUCTURE:

  AbstractExpression (interface):
    boolean interpret(Map<String, Object> context)

  TerminalExpression (leaf node — no children):
    EqualsExpression: field = value
    GreaterThanExpression: field > value
    LessThanExpression: field < value

  NonTerminalExpression (composite node — has children):
    AndExpression: left.interpret(ctx) && right.interpret(ctx)
    OrExpression: left.interpret(ctx) || right.interpret(ctx)
    NotExpression: !expression.interpret(ctx)

JAVA IMPLEMENTATION:

  // Abstract Expression:
  @FunctionalInterface
  public interface Expression {
      boolean interpret(Map<String, Object> context);
  }

  // Terminal Expressions:
  public class EqualsExpression implements Expression {
      private final String field;
      private final Object value;

      public EqualsExpression(String field, Object value) {
          this.field = field;
          this.value = value;
      }

      @Override
      public boolean interpret(Map<String, Object> context) {
          return value.equals(context.get(field));
      }
  }

  public class GreaterThanExpression implements Expression {
      private final String field;
      private final Comparable<Object> value;

      @SuppressWarnings("unchecked")
      public GreaterThanExpression(String field, Comparable<?> value) {
          this.field = field;
          this.value = (Comparable<Object>) value;
      }

      @Override
      public boolean interpret(Map<String, Object> context) {
          Object fieldValue = context.get(field);
          return fieldValue instanceof Comparable
              && value.compareTo(fieldValue) < 0;   // value < fieldValue → fieldValue > value
      }
  }

  // Non-Terminal Expressions (Composite):
  public class AndExpression implements Expression {
      private final Expression left;
      private final Expression right;

      public AndExpression(Expression left, Expression right) {
          this.left = left;
          this.right = right;
      }

      @Override
      public boolean interpret(Map<String, Object> context) {
          return left.interpret(context) && right.interpret(context);
      }
  }

  public class OrExpression implements Expression {
      private final Expression left;
      private final Expression right;

      public OrExpression(Expression left, Expression right) {
          this.left = left;
          this.right = right;
      }

      @Override
      public boolean interpret(Map<String, Object> context) {
          return left.interpret(context) || right.interpret(context);
      }
  }

  // Build AST manually (parser would generate this from a string):
  // Rule: age > 18 AND (balance > 1000 OR premium = true)
  Expression rule = new AndExpression(
      new GreaterThanExpression("age", 18),
      new OrExpression(
          new GreaterThanExpression("balance", 1000.0),
          new EqualsExpression("premium", true)
      )
  );

  // Evaluate against different customers:
  Map<String, Object> customer1 = Map.of("age", 25, "balance", 500.0, "premium", false);
  Map<String, Object> customer2 = Map.of("age", 25, "balance", 500.0, "premium", true);
  Map<String, Object> customer3 = Map.of("age", 16, "balance", 5000.0, "premium", true);

  System.out.println(rule.interpret(customer1));   // false (balance not > 1000, not premium)
  System.out.println(rule.interpret(customer2));   // true  (age > 18 AND premium = true)
  System.out.println(rule.interpret(customer3));   // false (age NOT > 18, even though premium)

SPRING SpEL USAGE (built-in Interpreter Pattern):

  @Service
  public class EligibilityService {
      private final ExpressionParser parser = new SpelExpressionParser();

      public boolean evaluate(String ruleExpression, Customer customer) {
          // SpEL internally: parses → AST → interprets against context
          Expression spel = parser.parseExpression(ruleExpression);
          EvaluationContext context = new StandardEvaluationContext(customer);
          return Boolean.TRUE.equals(spel.getValue(context, Boolean.class));
      }
  }

  // Usage:
  eligibilityService.evaluate("age > 18 && (balance > 1000 || premium)", customer);
  // SpEL handles parsing; you provide the grammar as a string.
  // For complex or performance-critical rules: build your own AST instead of SpEL.

VISITOR PATTERN INTEGRATION (operation separation):

  // Add new operation (print rule) without modifying expression classes:
  interface ExpressionVisitor {
      void visit(EqualsExpression expr);
      void visit(GreaterThanExpression expr);
      void visit(AndExpression expr);
      void visit(OrExpression expr);
  }

  class ExpressionPrinter implements ExpressionVisitor {
      @Override public void visit(EqualsExpression e) {
          System.out.println(e.field + " = " + e.value);
      }
      @Override public void visit(AndExpression e) {
          e.left.accept(this); System.out.println("AND"); e.right.accept(this);
      }
      // ... etc.
  }
  // Interpreter Pattern provides the structure; Visitor Pattern adds operations.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Interpreter:

- Business rules hardcoded in Java if-else chains: changing rules requires recompilation and redeployment
- New operators or combinations require new code paths
- Rules cannot be stored in a database or configured at runtime

WITH Interpreter:
→ Rules expressed as a grammar; stored as strings or AST serializations; interpreted at runtime. New rule: build new AST, no Java code change. Rule changes: update the database — no deployment.

---

### 🧠 Mental Model / Analogy

> A musical score. The conductor (interpreter context) and musicians (expression evaluators) read a musical score (the AST). Each symbol on the score (quarter note, rest, fermata) has a specific meaning and action. A measure (bar) is a composite expression: evaluate each note in sequence. A repeat sign is a non-terminal: evaluate the bracketed section twice. The score is data (the grammar). The musicians interpret the score (runtime evaluation). The same conductor + musicians can play different pieces: different ASTs (different rule expressions) interpreted by the same evaluator classes.

"Musical score" = the AST (Abstract Syntax Tree) — the grammar represented as data
"Each note symbol" = TerminalExpression (leaf: direct value / field comparison)
"A measure (bar)" = NonTerminalExpression (AND/OR — composite of sub-expressions)
"Conductor and musicians" = Interpreter context + expression `interpret()` methods
"Playing different pieces" = evaluating different rule expressions without code changes

---

### ⚙️ How It Works (Mechanism)

```
INTERPRETER PATTERN TREE TRAVERSAL:

  Rule: age > 18 AND (balance > 1000 OR premium = true)

  AST:
  AndExpression
  ├── GreaterThanExpression("age", 18)       [Terminal]
  └── OrExpression
      ├── GreaterThanExpression("balance", 1000)  [Terminal]
      └── EqualsExpression("premium", true)       [Terminal]

  Evaluation (customer: age=25, balance=500, premium=false):

  AndExpression.interpret(ctx):
    left = GreaterThanExpression("age", 18).interpret(ctx)
           → ctx["age"]=25 > 18 → TRUE
    right = OrExpression.interpret(ctx):
              left = GreaterThanExpression("balance", 1000).interpret(ctx)
                     → ctx["balance"]=500 > 1000 → FALSE
              right = EqualsExpression("premium", true).interpret(ctx)
                      → ctx["premium"]=false == true → FALSE
              → FALSE || FALSE → FALSE
    → TRUE && FALSE → FALSE

  Result: customer not eligible.

  Traversal: depth-first, post-order (children evaluated before parent).
```

---

### 🔄 How It Connects (Mini-Map)

```
Need runtime-configurable rules or language evaluation
        │
        ▼
Interpreter Pattern ◄──── (you are here)
(grammar as classes; AST = Composite Pattern; interpret() for evaluation)
        │
        ├── Composite Pattern: AST IS a Composite Pattern (tree of expressions)
        ├── Visitor Pattern: adds operations (print, optimize) to the AST without changing nodes
        ├── Spring SpEL: built-in Interpreter Pattern implementation
        └── Rule Engine (Drools): full-scale Interpreter Pattern with rich rule grammar
```

---

### 💻 Code Example

(See First Principles — complete Java implementation: EqualsExpression, GreaterThanExpression, AndExpression, OrExpression, AST construction, and evaluation against a context map.)

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Interpreter Pattern requires building a parser          | The Interpreter Pattern only covers the AST structure and evaluation mechanism. Building a parser (turning a string into an AST) is a separate concern: ANTLR, parser combinators, or manual recursive descent parsers. The GoF pattern assumes the AST is already constructed. In practice: if you need to parse rule strings, use ANTLR or SpEL; if you already have structured rule data (e.g., from a JSON rule definition), build the AST directly from the structure. |
| Interpreter Pattern scales to complex languages         | GoF explicitly notes: "Interpreter is not suitable for complex grammars. The class hierarchy becomes too large and hard to maintain." For simple DSLs (10-20 grammar rules): Interpreter Pattern works well. For SQL, Java, HTML (hundreds of grammar rules): use a purpose-built parser generator (ANTLR) and a separate evaluation/compilation framework. SpEL, OGNL, and similar work because they have a bounded, carefully designed grammar.                           |
| Interpreter and Strategy Pattern solve the same problem | Strategy Pattern: selects one algorithm from a fixed, known set at runtime. Interpreter Pattern: evaluates a composable expression built from a grammar — unlimited combinations of grammar rules. Strategy: "which algorithm?" (choice). Interpreter: "evaluate this expression" (computation from structure). A rule engine: Interpreter (composable rules). Feature flags: Strategy (one of N fixed strategies).                                                         |

---

### 🔥 Pitfalls in Production

**Rule injection leading to arbitrary code execution via SpEL:**

```java
// CRITICAL SECURITY VULNERABILITY — SpEL injection:

@RestController
public class FilterController {
    private final ExpressionParser parser = new SpelExpressionParser();

    @GetMapping("/filter")
    public boolean filter(@RequestParam String rule, @RequestParam Long customerId) {
        Customer customer = customerRepo.findById(customerId).orElseThrow();

        // DANGEROUS: user-provided rule string evaluated as SpEL expression:
        Expression spel = parser.parseExpression(rule);   // INJECTION RISK!
        // Attacker sends rule = "T(java.lang.Runtime).getRuntime().exec('rm -rf /')"
        // SpEL T() operator accesses any Java class → remote code execution!
        return Boolean.TRUE.equals(spel.getValue(customer, Boolean.class));
    }
}

// FIX 1 — Use SimpleEvaluationContext (restricts SpEL to property access only):
@GetMapping("/filter")
public boolean filter(@RequestParam String rule, @RequestParam Long customerId) {
    Customer customer = customerRepo.findById(customerId).orElseThrow();

    // SimpleEvaluationContext: only allows property access, no Java class invocation:
    ExpressionParser parser = new SpelExpressionParser();
    EvaluationContext restrictedContext =
        SimpleEvaluationContext.forReadOnlyDataBinding().withRootObject(customer).build();

    Expression spel = parser.parseExpression(rule);
    return Boolean.TRUE.equals(spel.getValue(restrictedContext, Boolean.class));
    // T(java.lang.Runtime).getRuntime()... → EvaluationException (Type access not allowed)
}

// FIX 2 — Never evaluate user-provided rule strings; use a structured rule DSL:
// Accept rule as JSON: {"field":"age","op":"GT","value":18}
// Build AST from JSON structure (not from a string):
Expression rule = buildExpressionFromJson(ruleJson);
rule.interpret(customerContext);
// No string parsing → no injection surface.
```

---

### 🔗 Related Keywords

- `Composite Pattern` — AST is a Composite Pattern; Interpreter Pattern depends on it
- `Visitor Pattern` — adds operations (printing, optimization, compilation) to an AST
- `Spring SpEL` — Spring Expression Language: production Interpreter Pattern implementation
- `Rule Engine (Drools)` — full-scale Interpreter Pattern with forward-chaining rule evaluation
- `Abstract Syntax Tree (AST)` — data structure produced by parsers, consumed by interpreters

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Grammar rules as classes; AST as         │
│              │ Composite tree; interpret() recurses     │
│              │ through the tree to evaluate.            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple DSL or rule language;             │
│              │ runtime-configurable rules;              │
│              │ expression evaluation from stored data   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex grammar (hundreds of rules);     │
│              │ user-provided rule strings (injection);  │
│              │ performance-critical hot paths           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Musical score: each symbol = an         │
│              │  expression class. Conductor = context. │
│              │  Musicians evaluate the score at runtime."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Composite Pattern → Visitor Pattern →    │
│              │ Spring SpEL → ANTLR → Drools              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Interpreter Pattern uses recursive tree traversal — depth-first, evaluating children before parents. For a deeply nested expression tree (e.g., 1000 levels deep), recursive traversal risks a StackOverflowError. How would you convert the recursive `interpret()` traversal to an iterative traversal using an explicit stack, and in what production scenarios (deeply nested rules from user input, compiled expressions from a database) might this matter?

**Q2.** Spring SpEL uses `SimpleEvaluationContext` to restrict expression evaluation to safe property access. But even property access can expose sensitive data (a SpEL expression like `password` against a User object returns the password field). How do you design a rule expression system that: (1) restricts evaluation to a safe subset of the object graph; (2) prevents access to sensitive fields; (3) limits allowed operators (whitelist `>`, `<`, `=`, `AND`, `OR` — disallow method calls); and (4) validates rule expressions before storing them in the database?
