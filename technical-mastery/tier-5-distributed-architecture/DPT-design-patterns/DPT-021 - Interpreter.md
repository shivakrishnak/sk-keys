---
id: DPT-021
title: Interpreter
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-014
used_by: DPT-064
related: DPT-014, DPT-027, DPT-020
tags:
  - pattern
  - behavioral
  - advanced
  - language
  - parsing
  - dsl
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/design-patterns/interpreter/
---

⚡ TL;DR - Interpreter represents a grammar as a class
hierarchy and defines an interpreter that uses this
representation to evaluate sentences in the language -
enabling custom DSLs and expression evaluation without
a full parser generator.

| #21 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-014 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-014, DPT-027, DPT-020 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A report builder must support filter expressions like
`age > 30 AND (city = "London" OR city = "Paris")`.
Without Interpreter: a giant if/else chain parsing
the string character-by-character, or a fragile regular
expression that breaks on nested parentheses. Each new
operator or keyword requires modifying the core parsing
code.

**THE BREAKING POINT:**
A new requirement: support `NOT (age < 18)`. The
parser must be rewired to handle NOT. A different service
wants the same filter language but with added SQL operators.
The monolithic parser cannot be reused; each service
reimplements it.

**THE INVENTION MOMENT:**
Interpreter: represent each grammar rule as a class.
`AndExpression`, `OrExpression`, `NotExpression`, and
`GreaterThanExpression` are each a class with an `interpret(context)`
method. The parser builds a TREE of these objects. To
evaluate: call `interpret()` on the root - it recursively
evaluates child expressions. Adding `NOT`: one new class.

**EVOLUTION:**
Spring Expression Language (SpEL) is an Interpreter.
Apache Lucene query parsing builds an expression tree.
SQL WHERE clause evaluation, rule engines (Drools), and
boolean search systems (Elasticsearch query DSL) all use
the Interpreter pattern. Every programming language
runtime interprets an AST (Abstract Syntax Tree) -
an Interpreter tree.

---

### 📘 Textbook Definition

The **Interpreter** pattern is a Behavioral design pattern
that defines a grammatical representation for a language
and provides an interpreter to deal with that grammar.
Each grammar rule is represented as a class; sentences
in the language are represented as trees of these rule
objects. The interpreter evaluates a sentence by calling
the `interpret()` method on the root of the tree,
which recursively evaluates the tree. The pattern is
suited for simple grammars where efficiency is not a
primary concern; complex or performance-critical grammars
should use dedicated parser generators (ANTLR, JavaCC).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Interpreter turns grammar rules into classes so a complex
expression tree can evaluate itself by calling `interpret()`
recursively.

**One analogy:**
> A calculator where each operator is an object. `3 + (4 × 2)`
> becomes a tree: `PlusExpr(NumberExpr(3), MultiplyExpr(NumberExpr(4), NumberExpr(2)))`.
> Calling `root.interpret()` evaluates: Multiply(4,2)=8,
> then Plus(3,8)=11. Each rule-object knows only its own
> operation; the tree structure handles precedence and
> grouping.

**One insight:**
Interpreter externalizes the grammar so extending the
language means adding a new class, not modifying the
parser. This is the Open/Closed Principle applied to
language design.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each grammar rule becomes exactly one class with an
   `interpret(context)` method.
2. Terminal expressions (leaves) read from the context
   but do not have children.
3. Non-terminal expressions (composites) have children
   that they evaluate before computing their own result.

**DERIVED DESIGN:**
Two expression types:
- **Terminal Expression** (leaf): represents a basic
  symbol in the grammar (variable, literal). `interpret()`
  reads or produces a value.
- **Non-terminal Expression** (composite): represents
  a grammar rule composed of other expressions
  (`AndExpression`, `OrExpression`). `interpret()` evaluates
  children, combines results.

The **Context** holds global state or input that terminal
expressions read (e.g., variable bindings, the string
being matched).

**TRADE-OFFS:**

**Gain:** Adding new expressions is one new class
(Open/Closed). The grammar is explicit in the class
hierarchy. Easy to compose expressions.

**Cost:** Performance is poor for complex grammars
(each `interpret()` call traverses the tree). Class
proliferation for large grammars. Does not scale to
production programming languages (use ANTLR/JavaCC).

---

### 🧪 Thought Experiment

**SETUP:**
A configuration system lets users define access rules:
`role = "ADMIN" AND (env = "prod" OR env = "staging")`.
This expression must be evaluated at runtime against
a user context.

**WITH INTERPRETER:**
Build: `AndExpr(EqualExpr("role","ADMIN"), OrExpr(EqualExpr("env","prod"), EqualExpr("env","staging")))`

```
Context: { role="ADMIN", env="prod" }
root.interpret(ctx):
  AndExpr: left.interpret() AND right.interpret()
    EqualExpr("role","ADMIN"): ctx["role"] == "ADMIN" →
      true
    OrExpr:
      EqualExpr("env","prod"): ctx["env"] == "prod" → true
      → short-circuit: true
    → true AND true → true
Result: user has access
```

Adding `NOT`: add `NotExpression` class. No other change.

---

### 🧠 Mental Model / Analogy

> Interpreter is a LEGO GRAMMAR. Each language construct
> is a LEGO brick with a standard connector (`interpret()`).
> A sentence is a structure built from bricks. Evaluating
> the sentence: shake the root brick - it rattles its children,
> which rattle their children, collecting and combining
> results up the chain. New language feature = new brick shape.

- "Brick" = Expression class
- "Connector" = interpret(Context) method
- "Building from bricks" = constructing the parse tree
- "Shaking the root" = calling root.interpret()

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Interpreter lets you define a mini-language by making each
word or rule in the language a class. To evaluate a
sentence, you build a tree of these class-objects and
evaluate the tree.

**Level 2 - How to use it (junior developer):**
Define an `Expression` interface with `interpret(Context ctx)`.
Create one class per grammar rule: `NumberExpression`,
`AddExpression(left, right)`, `VariableExpression`.
To evaluate `3 + x`: build the tree manually:
`new AddExpression(new NumberExpression(3), new VariableExpression("x"))`.
Set `ctx.set("x", 5)`. Call `root.interpret(ctx)` → 8.

**Level 3 - How it works (mid-level engineer):**
Spring Expression Language (SpEL) uses Interpreter internally.
`ExpressionParser parser = new SpelExpressionParser()`.
`Expression exp = parser.parseExpression("user.age > 18")`.
`exp.getValue(context)` evaluates the expression against a
context object. SpEL builds an AST (Interpreter tree) from
the expression string; `getValue` traverses the AST calling
each node's interpretation logic. The AST nodes are SpEL's
ConcreteExpression classes.

**Level 4 - Why it was designed this way (senior/staff):**
Interpreter solves the extension problem for DSLs (Domain
Specific Languages). When a system needs user-configurable
logic (filter rules, validation expressions, query languages),
hard-coding all possible combinations is impossible.
Interpreter lets the system define a grammar, parse user
input into an expression tree, and evaluate it at runtime.
This is why rule engines, search query parsers, and report
filters use Interpreter: the language needs to be extensible
by configuration, not code changes.

**Level 5 - Mastery (distinguished engineer):**
The Interpreter pattern's class hierarchy IS a grammar
in the sense of formal language theory. Each non-terminal
production rule maps to a non-terminal expression class;
each terminal maps to a terminal expression class. The
`interpret()` method performs attribute evaluation on
the parse tree - this is "attributed grammars" from
compiler theory. Production programming language runtimes
(JVM bytecode interpreter, V8 JavaScript engine's AST
evaluator) use the same structure with optimizations
(method dispatch tables, JIT compilation). The GoF
Interpreter pattern is the conceptual foundation;
production language runtimes add performance optimizations
on top of the same core structure.

---

### ⚙️ How It Works (Mechanism)

```
Interpreter Structure
┌─────────────────────────────────────────────────────────┐
│ Expression (interface)                                  │
│   + interpret(Context): boolean                         │
│                                                         │
│ TerminalExpression (leaf)                               │
│   - field: String                                       │
│   - value: String                                       │
│   + interpret(ctx): return ctx.get(field).equals(value) │
│                                                         │
│ AndExpression (non-terminal)                            │
│   - left: Expression                                    │
│   - right: Expression                                   │
│   + interpret(ctx):                                     │
│     return left.interpret(ctx) && right.interpret(ctx)  │
│                                                         │
│ OrExpression (non-terminal)                             │
│   - left: Expression                                    │
│   - right: Expression                                   │
│   + interpret(ctx):                                     │
│     return left.interpret(ctx) || right.interpret(ctx)  │
│                                                         │
│ Parse Tree for: role="ADMIN" AND env="prod"             │
│         AND                                             │
│        /   \                                            │
│   role=ADMIN  env=prod                                  │
│   (terminal)  (terminal)                                │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Input: "role = ADMIN AND env = prod"
Step 1 - Parse: build expression tree
  AND(Equal("role","ADMIN"), Equal("env","prod"))

Step 2 - Set context:
  ctx = { role="USER", env="prod" }

Step 3 - Interpret: root.interpret(ctx)
  AndExpression.interpret():
    left = Equal("role","ADMIN").interpret(ctx)
         = ctx.get("role") == "ADMIN"
         = "USER" == "ADMIN" → false
    short-circuit: false AND ? → false (right not
      evaluated)
  Result: false (access denied)
```

---

### 💻 Code Example

**Example - Boolean filter expression interpreter:**

```java
// BAD: hard-coded if/else chain for filter logic
boolean evaluate(User u, String filter) {
    if (filter.equals("admin-only"))
        return u.role().equals("ADMIN");
    if (filter.equals("prod-and-admin"))
        return u.role().equals("ADMIN")
            && u.env().equals("prod");
    // Adding new filter: modify this method
    throw new IllegalArgumentException("Unknown: " + filter);
}

// GOOD: Interpreter pattern - extensible, composable

interface Expression {
    boolean interpret(Map<String, String> ctx);
}

// Terminal: checks a single field-value pair
class EqualExpression implements Expression {
    private final String field, value;

    EqualExpression(String field, String value) {
        this.field = field;
        this.value = value;
    }

    @Override
    public boolean interpret(Map<String, String> ctx) {
        return value.equals(ctx.get(field));
    }
}

// Non-terminal: AND combinator
class AndExpression implements Expression {
    private final Expression left, right;

    AndExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public boolean interpret(Map<String, String> ctx) {
        return left.interpret(ctx) && right.interpret(ctx);
    }
}

// Non-terminal: OR combinator
class OrExpression implements Expression {
    private final Expression left, right;

    OrExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public boolean interpret(Map<String, String> ctx) {
        return left.interpret(ctx) || right.interpret(ctx);
    }
}

// Non-terminal: NOT (adding new operator = new class only)
class NotExpression implements Expression {
    private final Expression expr;

    NotExpression(Expression expr) {
        this.expr = expr;
    }

    @Override
    public boolean interpret(Map<String, String> ctx) {
        return !expr.interpret(ctx);
    }
}

// Build tree for: role="ADMIN" AND (env="prod" OR env="staging")
Expression rule = new AndExpression(
    new EqualExpression("role", "ADMIN"),
    new OrExpression(
        new EqualExpression("env", "prod"),
        new EqualExpression("env", "staging")
    )
);

// Evaluate
Map<String, String> ctx = Map.of("role","ADMIN","env","prod");
boolean allowed = rule.interpret(ctx); // true

// Adding NOT without changing existing code:
Expression notProd = new NotExpression(
    new EqualExpression("env", "prod")
);
```

**How to test/verify correctness:**
Test each expression class independently: terminal expressions
return expected value from context; composite expressions
combine children correctly. Test the full tree with known
inputs. Test edge cases: short-circuit evaluation in AND/OR,
nested NOT.

---

### ⚖️ Comparison Table

| Approach | Extensible | Grammar in code | Performance | When to use |
|---|---|---|---|---|
| **Interpreter** | Yes (new class) | Yes (explicit) | Poor at scale | Simple grammars, DSLs |
| Hard-coded if/else | No | Implicit | Good | Single, fixed logic |
| ANTLR/JavaCC | Yes | Separate grammar file | Excellent | Complex languages |
| Visitor on AST | Yes | Separate | Good | Production parsers |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Interpreter pattern builds parsers | Interpreter assumes a parser already built the tree. The pattern is about EVALUATING the tree, not PARSING text into a tree. Parsing text into the tree is a separate concern (often done manually or with a parser library) |
| Interpreter is for programming languages only | Interpreter applies wherever a configurable "mini language" is needed: filter expressions, access rules, formula evaluation, query DSLs, workflow conditions |
| SpEL parses expressions, so it is not Interpreter | SpEL IS Interpreter: SpEL builds an AST from expression text, then walks the AST with each node's interpretation method - exactly the Interpreter pattern |
| Interpreter and Visitor are the same on trees | Interpreter: each node class knows how to interpret ITSELF (behavior in the node). Visitor: a separate Visitor class provides behavior for each node type (behavior outside the node). Visitor is preferred when many different operations need to be performed on the same tree |

---

### 🚨 Failure Modes & Diagnosis

**Deep Recursion Causes StackOverflowError**

**Symptom:**
Evaluating a deeply nested expression `((((a AND b) AND c) AND d) AND ...)` with 1,000 levels causes `java.lang.StackOverflowError`.

**Root Cause:**
Each `interpret()` call adds a stack frame. Deep trees
exhaust the JVM stack.

**Diagnostic Signal:**
StackOverflowError with stack frames all showing
`interpret()` at various expression classes.

**Fix:**
For production use: convert to an iterative evaluation
using an explicit stack (Deque). Or: validate maximum
expression depth before building the tree.

**Prevention:**
Limit expression depth at parse time. Reject or flatten
expressions deeper than a configurable threshold (e.g., 50 levels).

---

**Performance Degradation Under Heavy Evaluation Load**

**Symptom:**
An access-control system using Interpreter evaluates
the same rule expressions for millions of requests per
second. CPU usage spikes; evaluation time is 10ms per
request.

**Root Cause:**
Interpreter tree traversal is O(tree size) per evaluation.
With millions of evaluations, the constant factor matters.
Each `interpret()` call involves virtual method dispatch
on every node.

**Fix:**
Compile the expression tree to a more efficient form:
a predicate function (once) evaluated many times, or
a compiled bytecode representation. Spring SpEL supports
this: use compiled SpEL expressions (`SpelCompilerMode.IMMEDIATE`)
which compiles the SpEL AST to JVM bytecode on first
evaluation and directly invokes the bytecode subsequently.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Composite` - DPT-014; the expression tree IS a Composite
  pattern; understanding tree structure of Composite
  clarifies how the Interpreter tree is built

**Builds On This (learn these next):**
- `Visitor` - DPT-029; Visitor is the next evolution
  of tree processing; where Interpreter puts behavior
  in each node, Visitor puts behavior in a separate class

**Alternatives / Comparisons:**
- `Strategy` - Strategy selects one algorithm from many;
  Interpreter evaluates a composed expression tree

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Grammar as class hierarchy; sentences    │
│              │ as expression trees; interpret() walks   │
├──────────────┼──────────────────────────────────────────┤
│ KEY CLASSES  │ Terminal (leaf: field check, literal)    │
│              │ Non-terminal (And, Or, Not, composite)   │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ Spring SpEL, Drools rule engine,         │
│              │ Elasticsearch query DSL parsing          │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Deep trees cause StackOverflow;          │
│              │ performance poor for high-volume eval    │
├──────────────┼──────────────────────────────────────────┤
│ VS VISITOR   │ Interpreter: node knows how to eval self │
│              │ Visitor: separate class evaluates nodes  │
├──────────────┼──────────────────────────────────────────┤
│ WHEN NOT TO  │ Complex grammars, high performance req.  │
│              │ → use ANTLR/JavaCC instead               │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Iterator → Mediator → Memento → Observer │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Each grammar rule becomes a class with `interpret(Context)`;
   sentences are trees of these classes; evaluating the
   tree evaluates the sentence
2. Spring SpEL, SQL WHERE clause evaluation, and boolean
   search query parsers are all Interpreter implementations
3. Use Interpreter for simple DSLs; use ANTLR or JavaCC for
   complex grammars where performance matters

**Interview one-liner:**
"Interpreter represents grammar rules as a class hierarchy
where each rule has an interpret() method; sentences are
trees of these rule objects evaluated recursively. Spring
SpEL and boolean filter expression engines use this pattern.
The key limitation: performance degrades for complex grammars
or deep trees - use ANTLR for production language processing."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When users or configuration need to express logic
(filters, rules, conditions), don't hard-code all cases -
define a mini-language with the Interpreter pattern.
The grammar is explicit, the language is extensible by
adding classes, and the evaluation is automatically
recursive.

**Where else this pattern appears:**
- **SQL query engines** - SQL WHERE clause is an
  Interpreter tree; AND/OR/NOT/comparison operators
  are non-terminal and terminal expressions; the query
  optimizer walks the tree
- **Spring SpEL** - every `@PreAuthorize("hasRole('ADMIN')")`,
  `@Value("#{systemProperties['user.home']}")`, and
  `@Cacheable(key = "#root.method.name")` uses SpEL,
  which is an Interpreter implementation

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [DISTINGUISH] Explain the difference between Interpreter
   and Visitor on an expression tree - one sentence for
   where the evaluation behavior lives
2. [IMPLEMENT] Build an Interpreter for a simple boolean
   filter expression supporting AND, OR, NOT, and equality
   checks, evaluating against a Map<String, String> context
3. [IDENTIFY] Recognize Spring SpEL as an Interpreter
   implementation - explain which part is the grammar
   class hierarchy and which part is the context

---

### 🎯 Interview Deep-Dive

**Q1: When would you use the Interpreter pattern vs
a parser generator like ANTLR?**

*Why they ask:* Tests pragmatic judgment on when to apply
the pattern vs when it would hurt.

*Strong answer includes:*
- Interpreter: small grammar (5-20 rules), simple expressions,
  infrequent evaluation, rapid prototyping of a DSL
- ANTLR/JavaCC: large grammar (50+ rules), complex syntax
  (precedence, associativity), high-performance requirement,
  production language implementations
- Interpreter advantage: no external tools, pure Java,
  simple to add new rules as classes
- ANTLR advantage: handles left recursion, operator
  precedence, error recovery; generates optimized parsers
  with O(n) parsing

