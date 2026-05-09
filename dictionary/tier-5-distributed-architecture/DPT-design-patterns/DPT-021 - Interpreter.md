---
layout: default
title: "Interpreter"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /design-patterns/interpreter/
id: DPT-021
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - advanced
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-021 - Interpreter

⚡ TL;DR - Interpreter defines a grammar for a language and an interpreter to evaluate sentences in that language using a tree of expression objects.

| DPT-021 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Composite, Recursion, Abstract Syntax Tree, Formal Grammar | |
| **Used by:** | Query Language Parsers, Rule Engines, Expression Evaluators, DSL Interpreters | |
| **Related:** | Composite, Visitor, Command, Iterator | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A business rules engine needs to evaluate conditions like: `(age > 18 AND country = "US") OR isPremiumMember`. This expression varies per customer segment - new expressions arrive monthly from the business team as text strings. Without an interpreter, each new rule requires a developer to write Java code: `if (customer.getAge() > 18 && customer.getCountry().equals("US") || customer.isPremium())`. This is hard-coded business logic. Changing a rule requires a code change, test, and deployment - a 3-day cycle for a business rule update.

**THE BREAKING POINT:**
Business rules belong to business people, not to code. Hardcoding them violates the separation of concerns. Every new condition requires a developer. A/B testing rule variations requires deployments. The system cannot adapt to business changes at business speed - only at deployment speed.

**THE INVENTION MOMENT:**
This is exactly why the Interpreter pattern was created. Define a grammar for rule expressions. Build an `Expression` object tree (Abstract Syntax Tree) representing each rule. Evaluate the tree against a context object. The business rule `(age > 18 AND country = "US")` becomes `new AndExpression(new GreaterThanExpression("age", 18), new EqualsExpression("country", "US"))`. New rules are loaded from a database, not from code. The interpreter evaluates any valid expression without redeployment.

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
evaluators (Spring's `${...}` placeholder resolution).

---

### 📘 Textbook Definition

The **Interpreter** pattern is a behavioural design pattern that, given a language, defines a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language. Each rule of the grammar corresponds to a class; sentences are represented as Abstract Syntax Trees (ASTs) composed of these classes. The interpreter evaluates a sentence by traversing its AST recursively. The pattern is an application of the Composite pattern where each node in the tree is an expression that evaluates to a value.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A tree of objects where each node knows how to evaluate one piece of a language rule.

**One analogy:**
> Reading a recipe. "Take 2 eggs AND mix them OR substitute with (1 cup flour AND 1/2 tsp salt)." The recipe's structure (AND, OR, parentheses) directly maps to a tree: AND is a branch with two children; OR is a branch; ingredients are leaves. "Interpreting" the recipe means evaluating the tree: substitute? check the OR branch. Both children of AND must be available.

**One insight:**
Interpreter works because grammars are inherently recursive: an expression can contain expressions. This recursion maps exactly to Composite - a tree where each node evaluates itself by recursively evaluating its children. Adding a new operation to the language (e.g., XOR) is one new class, not a change to any existing class.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A language (formal grammar) can be represented as a set of rules, where each rule is either a terminal (leaf) or a non-terminal (composition of other rules).
2. Evaluation of any expression in the language reduces recursively to evaluation of its component sub-expressions.
3. The context (environment) for interpretation - variable values, database connections, lookup tables - is separate from the expression structure.

**DERIVED DESIGN:**
Given invariant 1: create an `AbstractExpression` interface with `interpret(Context ctx)`. Create `TerminalExpression` (leaf) implementations for literals, variables, and simple predicates. Create `NonTerminalExpression` (composite) implementations for AND, OR, NOT, addition, etc. Given invariant 2: each non-terminal's `interpret()` recursively calls `interpret()` on its children and combines the results. Given invariant 3: `Context` holds the runtime variable values passed through the tree.

The parser (converting text to the AST) is separate from the interpreter (evaluating the AST). The pattern covers only the interpreter phase; parsing is a compiler-construction concern.

**THE TRADE-OFFS:**
**Gain:** New grammar rules = new classes (Open/Closed); easy to change and extend the interpreted language; grammar is explicit in the class structure; supports complex recursive structures naturally.
**Cost:** Performance degrades for complex grammars (deep recursion); not suitable for production-grade SQL or programming language parsers (too slow); grammar complexity > 5–10 rule types becomes hard to manage; parser construction is separate and non-trivial; Visitor pattern is often needed alongside Interpreter to add operations without modifying expression classes.

---

### 🧪 Thought Experiment

**SETUP:**
A fraud detection system must evaluate: `(transactionAmount > 500 AND countryOfOrigin != "US") OR (velocity > 3 AND timeDelta < 60)`. New rules arrive from the fraud team weekly.

**WHAT HAPPENS WITHOUT INTERPRETER:**
A developer writes Java `if` statements for each rule. Fraud team submits a ticket. Developer writes code. PR review. Deploy. 3-day cycle per rule change. The fraud team cannot test rule variations independently. False-positive rate stays high because rapid iteration is impossible.

**WHAT HAPPENS WITH INTERPRETER:**
Rules are stored in a database as expression trees (or serialised DSL text parsed into trees). Fraud team modifies rules through a UI. The interpreter evaluates `rule.interpret(context)` for each transaction. Rule changes take effect in minutes, not days. A/B testing different rule thresholds is possible without deployment.

**THE INSIGHT:**
Interpreter separates the LANGUAGE of rules (what can be expressed) from the POLICY (which specific rules are currently active). The language is stable code; the policy is runtime data. Changing the policy doesn't require changing the code.

---

### 🧠 Mental Model / Analogy

> The Interpreter pattern is like a syntax tree in a calculator app. You type "3 + (4 × 5)". The calculator builds a tree: `+` with children `3` and `×`; `×` with children `4` and `5`. Evaluating the tree: evaluate `×`(4, 5) = 20, then evaluate `+`(3, 20) = 23. Each node knows only its own operation. The tree structure encodes the precedence and grouping.

- "3, 4, 5" → TerminalExpression (NumberExpression)
- "+" and "×" → NonTerminalExpression (operators)
- "Evaluating the tree" → calling `interpret(context)`
- "Building the tree from text" → the parser (separate from Interpreter)
- "5 different calculator operators" → 5 expression classes

Where this analogy breaks down: a simple calculator has a small grammar. The pattern scales poorly to full programming languages (Java, Python) where grammars have hundreds of rules - dedicated parser generators (ANTLR, Yacc) are used instead.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Interpreter is a recipe for reading a simple "language" - a set of rules with defined meaning. You represent the language structure as a tree of objects. To "evaluate" something in the language, you walk the tree, and each node computes its part of the answer. Adding a new word to the language: add one new type of tree node.

**Level 2 - How to use it (junior developer):**
Define an `Expression` interface with `boolean interpret(Context ctx)`. Implement `VariableExpression(String name)` - looks up `name` in `Context` and returns its value. Implement `AndExpression(Expression left, Expression right)` - returns `left.interpret(ctx) && right.interpret(ctx)`. Implement `OrExpression`, `NotExpression`. Build the tree manually or via a parser. Call `rootExpression.interpret(context)`.

**Level 3 - How it works (mid-level engineer):**
The AST is a Composite (Section 774): `NonTerminalExpression` IS-A `Expression` AND HAS-A `List<Expression>` children. Terminal nodes are Composite leaves. Evaluation is depth-first: the root calls `interpret()`, which calls children recursively. Short-circuit evaluation (AND stops on first false) is implementable: `left.interpret(ctx) && right.interpret(ctx)` uses Java's natural short-circuit. For mutable context (tracking intermediate results, counting evaluations), the `Context` object accumulates state as evaluation progresses. Performance: each `interpret()` call is a virtual dispatch + possible object allocation. For simple grammars evaluated frequently, flatten the AST to bytecode or use just-in-time compilation (as production rule engines do - Drools compiles rules to bytecode).

**Level 4 - Why it was designed this way (senior/staff):**
The GoF Interpreter pattern is rarely used for full programming languages because it doesn't address parsing (transforming text to AST) or optimisation (transforming the AST for efficient evaluation). In production rule engines (Drools, CLIPS), rules are compiled to optimised Rete networks - vastly more efficient than recursive AST traversal. Where Interpreter genuinely excels: small, stable domain-specific languages with 5–20 rules (SQL WHERE clause expression trees, mathematical expression evaluators, configuration expression parsers). The "Visitor" pattern is the natural companion: since adding operations (type-check, optimise, serialise) to an Interpreter requires modifying many expression classes, Visitor externalises those operations. Understanding Interpreter is foundational for understanding compilers, rule engines, and query planners - the architectural insights transfer even when the pattern itself is not directly used.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────────────┐
│  INTERPRETER - AST FOR: (age > 18) AND (country="US") │
│                                                       │
│                  AndExpression                        │
│                  /           \                        │
│  GreaterThanExpression    EqualsExpression             │
│   left: VarExpr("age")    left: VarExpr("country")    │
│   right: NumExpr(18)      right: StrExpr("US")         │
│                                                       │
│  Context: { age=25, country="US", premium=true }      │
│                                                       │
│  Evaluation (depth-first):                            │
│  AndExpression.interpret(ctx):                        │
│    left.interpret(ctx):                               │
│      GreaterThan.interpret: 25 > 18 → true            │
│    right.interpret(ctx):                              │
│      Equals.interpret: "US" == "US" → true            │
│    true && true → true                                │
└───────────────────────────────────────────────────────┘
```

**Adding a new rule type:**
```
To add XOR expression:
  new class XorExpression implements Expression:
    interpret(ctx):
      boolean l = left.interpret(ctx);
      boolean r = right.interpret(ctx);
      return l ^ r;  // exactly XOR semantics
// Zero changes to existing expression classes
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (fraud detection rule evaluation):**
```
Transaction arrives
  → FraudService.evaluate(transaction)
  → Load rule from RuleRepository
  → Parse rule text to Expression AST (parser step)
  → context = new Context(transaction)
  → rule.interpret(context)    ← YOU ARE HERE
     → recursive AST traversal
     → each expression evaluates itself
     → returns boolean result
  → if true: flag transaction as suspicious
  → else: allow transaction
```

**FAILURE PATH:**
```
Expression.interpret(ctx) throws NullPointerException
  → VariableExpression looks up "age" in context
  → "age" key not present → null returned
  → GreaterThan(null, 18) → NullPointerException
Fix: Context provides getOrDefault(); expressions
  handle null gracefully (return false for comparisons)
```

**WHAT CHANGES AT SCALE:**
At 100,000 evaluations/second, recursive tree traversal creates GC pressure from stack frames. Optimisations: (1) cache parsed ASTs (parse once, evaluate many times); (2) compile to `Predicate<Context>` lambda at parse time (JIT-friendly); (3) use Drools or equivalent compiled rule engine for production-scale rule evaluation.

---

### 💻 Code Example

**Example 1 - Boolean expression interpreter:**
```java
// Context carries evaluation variables
public class Context {
    private final Map<String, Object> variables;

    public Context(Map<String, Object> vars) {
        this.variables = vars;
    }

    public Object get(String name) {
        return variables.getOrDefault(name, null);
    }
}

// Abstract expression
public interface Expression {
    boolean interpret(Context ctx);
}

// Terminal: variable lookup + comparison
public class NumberGreaterThanExpression
        implements Expression {
    private final String varName;
    private final double threshold;

    public NumberGreaterThanExpression(
            String varName, double threshold) {
        this.varName   = varName;
        this.threshold = threshold;
    }

    @Override
    public boolean interpret(Context ctx) {
        Object val = ctx.get(varName);
        if (!(val instanceof Number)) return false;
        return ((Number) val).doubleValue() > threshold;
    }
}

// Terminal: string equality check
public class StringEqualsExpression implements Expression {
    private final String varName;
    private final String expected;

    public StringEqualsExpression(
            String varName, String expected) {
        this.varName  = varName;
        this.expected = expected;
    }

    @Override
    public boolean interpret(Context ctx) {
        return expected.equals(ctx.get(varName));
    }
}

// Non-terminal: AND
public class AndExpression implements Expression {
    private final Expression left, right;

    public AndExpression(Expression l, Expression r) {
        this.left  = l;
        this.right = r;
    }

    @Override
    public boolean interpret(Context ctx) {
        // Short-circuit: no right evaluation if left=false
        return left.interpret(ctx)
            && right.interpret(ctx);
    }
}

// Non-terminal: OR
public class OrExpression implements Expression {
    private final Expression left, right;

    public OrExpression(Expression l, Expression r) {
        this.left  = l;
        this.right = r;
    }

    @Override
    public boolean interpret(Context ctx) {
        return left.interpret(ctx)
            || right.interpret(ctx);
    }
}

// Build and evaluate:
// Rule: (age > 18 AND country = "US") OR isPremium
Expression rule = new OrExpression(
    new AndExpression(
        new NumberGreaterThanExpression("age", 18),
        new StringEqualsExpression("country", "US")
    ),
    new StringEqualsExpression("premium", "true")
);

Map<String, Object> vars = Map.of(
    "age", 25, "country", "US", "premium", "false");
Context ctx = new Context(vars);

boolean result = rule.interpret(ctx); // true
System.out.println("Eligible: " + result);
```

**Example 2 - Simple arithmetic interpreter:**
```java
// Arithmetic expressions
public interface ArithExpr {
    double evaluate(Context ctx);
}

public class NumberExpr implements ArithExpr {
    private final double value;
    public NumberExpr(double v) { this.value = v; }
    public double evaluate(Context ctx) { return value; }
}

public class VariableExpr implements ArithExpr {
    private final String name;
    public VariableExpr(String n) { this.name = n; }
    public double evaluate(Context ctx) {
        return ((Number) ctx.get(name)).doubleValue();
    }
}

public class AddExpr implements ArithExpr {
    private final ArithExpr left, right;
    public AddExpr(ArithExpr l, ArithExpr r) {
        this.left = l; this.right = r;
    }
    public double evaluate(Context ctx) {
        return left.evaluate(ctx) + right.evaluate(ctx);
    }
}

// (x + 5) + (y + 3):
ArithExpr expr = new AddExpr(
    new AddExpr(new VariableExpr("x"),
                new NumberExpr(5)),
    new AddExpr(new VariableExpr("y"),
                new NumberExpr(3)));

Context c = new Context(Map.of("x", 10.0, "y", 7.0));
System.out.println(expr.evaluate(c)); // 25.0
```

---

### ⚖️ Comparison Table

| Approach | Grammar Size | Performance | Extensibility | Best For |
|---|---|---|---|---|
| **Interpreter (AST)** | Small (< 20 rules) | Moderate (recursive) | High (one class per rule) | Business rules, config DSLs |
| Visitor on AST | Small–Medium | Better (no virtual dispatch) | Medium (Visitor per operation) | Compilers (type checking) |
| Compiled rule engine (Drools) | Large | High (Rete network) | Medium (proprietary DSL) | Production enterprise rules |
| Parser generator (ANTLR) | Any size | High | Custom | Programming language parsers |
| if-else ladder | Fixed at compile time | High | None | 2–3 hardcoded rules |

How to choose: use Interpreter for small, stable DSLs (5–15 grammar rules) where extensibility and domain ownership matter more than performance. Use a parser generator (ANTLR) for large grammars. Use a compiled rule engine (Drools) for production scale with dynamic rule loading.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Interpreter pattern includes parsing (text to AST) | Interpreter covers only the EVALUATION phase (AST to result). Parsing (text to AST) is a separate concern usually handled by parser generators or hand-written recursive descent parsers |
| Interpreter is appropriate for SQL or Java parser | Those grammars are too large and complex (hundreds of rules). Visitor-based AST + parser generator is the standard approach for production language tools |
| Interpreter and Visitor are alternatives | They are complements. Interpreter defines the grammar via expression classes. Visitor adds new operations (type checking, optimisation) to the existing expression classes without modifying them |
| Adding a new grammar rule is free | A new terminal or non-terminal expression class is needed. If you also use the Visitor pattern, every existing Visitor must be updated to handle the new expression type |
| Interpreter performance is always poor | Small grammars with immutable trees (cached ASTs) can be fast. The performance concern applies primarily to deep trees evaluated very frequently |

---

### 🚨 Failure Modes & Diagnosis

**1. Grammar Too Large - Class Explosion**

**Symptom:** The rule engine has grown to 50 expression classes. Adding a new operator now requires examining all 50 classes to ensure consistent handling.

**Root Cause:** Interpreter was applied to a grammar that grew beyond its sweet spot (typically > 15 rule types). The class-per-rule design becomes unmanageable.

**Diagnostic:**
```bash
find src -name "*Expression.java" | wc -l
# If > 20: grammar has outgrown the pattern
# Consider: Visitor pattern to centralise operations,
# or switch to ANTLR + visitor-based AST walker
```

**Fix:**
Introduce the Visitor pattern: one `ExpressionVisitor` interface consolidates operations (evaluate, type-check, serialize) currently scattered across expression classes. Or migrate to ANTLR-generated parser with a clean visitor.

**Prevention:** When grammar exceeds 10–12 expression types, evaluate whether a parser generator is more appropriate.

---

**2. Context Mutation During Evaluation - Side Effect Bug**

**Symptom:** Evaluating rule A produces different results depending on the order in which rules are evaluated. Rules appear to "interact" even though they should be independent.

**Root Cause:** An expression's `interpret()` modifies the `Context` object as a side effect. Subsequent expressions see the modified context.

**Diagnostic:**
```java
// Add immutability check:
public class Context {
    private final Map<String, Object> variables;
    // Use unmodifiableMap to detect mutation:
    public Context(Map<String, Object> vars) {
        this.variables = Collections.unmodifiableMap(vars);
    }
    // Any expression trying to ctx.put() will throw
}
```

**Fix:**
Make `Context` immutable. If expressions need to accumulate results, pass a separate mutable `EvaluationResult` object alongside the immutable `Context`.

**Prevention:** Declare `Context` as effectively immutable from the start. Expressions should only READ context, never write it.

---

**3. Stack Overflow on Deeply Nested Expressions**

**Symptom:** A very complex business rule (50+ levels of nesting) causes `StackOverflowError` during evaluation.

**Root Cause:** Recursive `interpret()` calls create one stack frame per tree level. JVM default stack depth is ~1,000 frames.

**Diagnostic:**
```java
// Measure tree depth before evaluation:
public int depth(Expression expr) {
    if (expr instanceof TerminalExpression) return 1;
    return 1 + ((NonTerminalExpression) expr)
        .getChildren().stream()
        .mapToInt(this::depth)
        .max().orElse(0);
}
// Log warning if depth > 100
```

**Fix:**
Convert the recursive evaluator to an iterative evaluator using an explicit `Deque<StackFrame>` that simulates the call stack. Or: enforce a maximum nesting depth at parse time (reject deeply nested rules before they can cause a stack overflow).

**Prevention:** Cap maximum expression nesting depth at rule creation time. Document the cap in API documentation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Composite` - Interpreter is Composite applied to grammar rules; understanding Composite's tree structure is essential
- `Recursion` - Interpreter's core evaluation mechanism is recursive tree traversal; comfort with recursive algorithms is required
- `Abstract Syntax Tree` - the data structure Interpreter produces and traverses; understanding AST structure is foundational

**Builds On This (learn these next):**
- `Visitor` - essential companion: adds operations (type-checking, optimisation, serialisation) to Interpreter expression classes without modifying them
- `Rule Engine Pattern` - production-scale Interpreter: compiled rule evaluation using Rete algorithm (Drools, Camunda Rules)
- `Domain-Specific Language (DSL)` - Interpreter enables embedding a mini-language in your application; understanding DSL design drives better grammar design

**Alternatives / Comparisons:**
- `Visitor` - complements Interpreter by adding new operations; use together, not instead
- `Strategy` - selects one of several algorithms; simpler than Interpreter when the "language" has only one dimension of variation
- `Command` - encapsulates one action; Interpreter composes many operations in a language structure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Grammar defined by a class hierarchy;     │
│              │ sentences evaluated as recursive AST      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Business rules hard-coded in Java; cannot │
│ SOLVES       │ change without developer + deployment     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Grammar = class hierarchy (Composite);    │
│              │ evaluation = recursive interpret(ctx)     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Small (< 15 rules), stable domain         │
│              │ language configurable at runtime          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Grammar > 20 rules; performance-critical; │
│              │ or language complexity requires ANTLR     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Extensible, self-describing grammar vs    │
│              │ poor performance and class proliferation  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Rules as trees - evaluation is just      │
│              │  recursion all the way down."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Visitor → Rule Engine (Drools) →          │
│              │ ANTLR Parser Generator                    │
└──────────────────────────────────────────────────────────┘
```


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
  term; `|` is the composition operator.

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
hierarchies -- rather than production DSL implementation.
---

### 🧠 Think About This Before We Continue

**Q1.** A fraud detection system uses Interpreter to evaluate 500 different customer eligibility rules simultaneously on every transaction (10,000 transactions/second = 5,000,000 rule evaluations/second). Each rule is a 10-level deep AST. Profile the CPU cost: estimate the number of virtual method dispatch calls per second, and describe three optimisations (at the pattern, JVM, and architecture levels) that can reduce the evaluation cost by 10× without changing the business logic.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** Your Interpreter has 12 expression classes. The team wants to add three new operations to every expression: `typeCheck(TypeContext)`, `optimise(OptimisationContext)`, and `serialise(StringBuilder)`. The naive approach adds three methods to the `AbstractExpression` interface and implements all 36 methods (12 classes × 3 methods). Explain why this approach violates the Open/Closed Principle and describe how applying the Visitor pattern solves this problem - including the exact structure of the Visitor interface and the accept() method in the expression hierarchy.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A team must evaluate user-defined
filter expressions like `age > 18 AND (country = 'US' OR
premium = true)` against a stream of user objects. Compare:
(1) Interpreter pattern with a class per grammar rule,
(2) a parser using a library like ANTLR, (3) embedding a
scripting engine (Groovy, MVEL). State the decision criteria
for each approach.

*Hint: The AVOID WHEN criteria in the Quick Reference Card
and the Level 4 explanation both address grammar complexity
thresholds. Map each option to the correct complexity tier.*
