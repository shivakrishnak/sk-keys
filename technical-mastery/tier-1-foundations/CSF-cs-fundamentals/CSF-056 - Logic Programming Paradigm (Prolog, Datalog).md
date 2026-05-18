---
id: CSF-056
title: "Logic Programming Paradigm (Prolog, Datalog)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-025, CSF-026
used_by: CSF-068
related: CSF-025, CSF-026, CSF-068
tags: [prolog, datalog, logic-programming, unification, backtracking]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/csf/logic-programming-paradigm/
---

⚡ TL;DR - Logic programming = declare facts and rules,
then query. Prolog: Horn clauses + unification + backtracking
search. Datalog: subset of Prolog (Datomic, CodeQL, Bloom).
You say WHAT is true; the engine finds HOW to prove it.
The engine is the algorithm. Used in: AI, static analysis,
distributed query languages.

| #056 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-025 (Declarative Programming), CSF-026 (Functional Programming) | |
| **Used by:** | CSF-068 (Category Theory for Programmers) | |
| **Related:** | CSF-025 (Declarative), CSF-026 (Functional), CSF-068 (Category Theory) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A compiler writer needs to implement type inference for
a statically typed language. Imperative approach: write
a type-checking algorithm that traverses the AST, maintains
a symbol table, performs unification manually, detects
cycles, and handles error cases. Thousands of lines of
complex, stateful, error-prone code. Similarly, a knowledge
base system (expert system, semantic reasoner) needs to
answer queries over thousands of facts and rules.
Imperative code must implement its own search strategy,
backtracking, and indexing. The result is complex and brittle.

**THE BREAKING POINT:**

For reasoning problems (what follows from what, what satisfies
these constraints, what can be derived), the ALGORITHM
is always the same: (1) try to prove the query goal,
(2) match it against known facts and rule heads,
(3) if matched a rule, try to prove the rule's body,
(4) backtrack if a path fails, try another. This search
algorithm is universal for logic reasoning. The developer
should declare the PROBLEM (facts + rules), not implement
the search algorithm.

**THE INVENTION MOMENT:**

Robert Kowalski (1974) articulated the principle
"Algorithm = Logic + Control." In logic programming,
you provide the Logic (facts and rules). The interpreter
provides the Control (search strategy). Prolog (Alain Colmerauer,
1972) was the first practical logic programming language:
Horn clauses (a restricted form of first-order logic),
unification (pattern matching with variable binding),
and depth-first search with backtracking. Datalog (1988)
is a Prolog subset without function terms: guaranteed
termination, safe recursive queries, used in databases
and static analysis. CodeQL (GitHub) uses a Datalog-like
language for security vulnerability analysis. Datomic
uses Datalog for database queries.

---

### 📘 Textbook Definition

**Logic programming:** A programming paradigm where a program
is a set of logical facts and rules. Computation = query
resolution by the inference engine via unification and backtracking.
Declarative: the developer specifies WHAT is true, not HOW
to derive it.

**Horn clause:** A logical formula of the form:
`head :- body1, body2, ..., bodyN` (read: "head is true IF
body1 AND body2 AND ... are all true"). Facts are Horn
clauses with no body. Rules have a head and a body.
Example:
- Fact: `parent(tom, bob).` (tom is a parent of bob)
- Rule: `grandparent(X, Z) :- parent(X, Y), parent(Y, Z).`
  (X is grandparent of Z if X is parent of Y AND Y is parent of Z)

**Unification:** Pattern matching with variable binding.
`parent(X, bob)` unifies with `parent(tom, bob)` by binding X = tom.
Variables start uppercase in Prolog. Ground terms (no variables)
unify only with identical terms.

**Backtracking:** When a proof attempt fails (no clause matches
a goal), the engine backtracks to the last choice point
and tries the next alternative. Depth-first search with
backtracking is Prolog's default control strategy.

**Datalog:** Prolog restricted to: no function terms (no
nested structure), no procedural extensions (no cut !),
guaranteed termination for any query (because no infinite
terms), safe recursive queries. Used as a query language
for databases and graph reasoning.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Logic programming = declare facts ("alice is parent of bob")
and rules ("grandparent(X,Z) if parent(X,Y) and parent(Y,Z)"),
then query ("who are alice's grandchildren?") - the engine
does the search.

**One analogy:**

> SQL is declarative for TABLE data: "give me all users
> where age > 30." Prolog/Datalog is declarative for
> KNOWLEDGE GRAPH data: "give me all ancestors of Bob."
> In SQL, you write: SELECT * FROM users WHERE age > 30.
> In Prolog, you declare: `adult(X) :- age(X, A), A > 30.`
> and query: `?- adult(Who).`
> The engine finds all X that satisfy the rule.

**One insight:**

Unification is more powerful than equality checking.
In Java: `x.equals(y)` checks if two values are equal.
In Prolog: `parent(X, bob) = parent(tom, bob)` SUCCEEDS
and BINDS X to tom. Unification solves equations over
structured terms. This is why Prolog can do pattern matching,
type inference, and constraint solving: the "assignment"
mechanism (unification) works bidirectionally. You can
say "I know the shape of the answer: `parent(tom, Y)` -
what is Y?" and Prolog finds the answer by searching
the knowledge base.

---

### 🔩 First Principles Explanation

**ALGORITHM = LOGIC + CONTROL:**

```
┌──────────────────────────────────────────────────────┐
│ In imperative programming:                           │
│   Algorithm = Logic + Control (you write both)       │
│   quicksort = pivot logic + partition control + recursion│
│                                                      │
│ In logic programming:                                │
│   You write: Logic (facts + rules)                   │
│   Engine provides: Control (search + backtracking)   │
│                                                      │
│ Prolog example - family relationships:               │
│   % Facts                                            │
│   parent(tom, bob).                                  │
│   parent(bob, ann).                                  │
│   parent(bob, pat).                                  │
│                                                      │
│   % Rule: grandparent                                │
│   grandparent(X,Z) :- parent(X,Y), parent(Y,Z).     │
│                                                      │
│   % Query: who is a grandparent of ann?              │
│   ?- grandparent(Who, ann).                          │
│   Who = tom. % Engine found this via unification     │
│                                                      │
│ The search (try each parent fact, unify, recurse):   │
│   the engine did this automatically.                 │
│   You wrote the LOGIC. Engine did the SEARCH.        │
└──────────────────────────────────────────────────────┘
```

**UNIFICATION ALGORITHM:**

```
┌──────────────────────────────────────────────────────┐
│ unify(T1, T2) with current substitution S:           │
│                                                      │
│ Case 1: T1 is variable not in S -> bind T1 to T2.   │
│ Case 2: T2 is variable not in S -> bind T2 to T1.   │
│ Case 3: T1 and T2 are atoms -> succeed iff T1 == T2. │
│ Case 4: T1=f(a1..an), T2=f(b1..bn) (same functor):  │
│         unify each ai with bi simultaneously.        │
│ Case 5: Otherwise -> FAIL (cannot unify).            │
│                                                      │
│ Example:                                             │
│ unify(parent(X, bob), parent(tom, bob)):             │
│   parent/2 = parent/2 ✓ (same functor, same arity)  │
│   unify(X, tom) -> X = tom ✓                        │
│   unify(bob, bob) -> ✓                               │
│   Result: X = tom. Success.                          │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**PROLOG AS TYPE INFERENCE ENGINE:**

Type inference (Hindley-Milner) is fundamentally a constraint
solving + unification problem. In Prolog:
```prolog
% Type rules as Horn clauses:
type(int_literal(N), int) :- integer(N).
type(add(E1, E2), int) :-
    type(E1, int), type(E2, int).
type(if(Cond, Then, Else), T) :-
    type(Cond, bool),
    type(Then, T),
    type(Else, T). % then/else must have same type T

% Query: what is the type of (3 + 4)?
?- type(add(int_literal(3), int_literal(4)), T).
T = int. % Prolog inferred the type!
```

A real type inference algorithm is this Prolog program,
plus handling of type variables (polymorphism) and occurs
check (prevent infinite types). GHC's (Haskell's) type
checker is essentially a highly optimized version of
this logic programming approach.

---

### 🎯 Mental Model / Analogy

**THE DETECTIVE ANALOGY:**

Prolog is Sherlock Holmes. You give Sherlock the facts
(witness statements, evidence) and the rules of deduction
(motive implies opportunity implies suspect). Sherlock
runs the inference engine: tries all deductive paths,
backtracks from dead ends, finds the conclusion that
is consistent with all the facts.

The developer writes the case file (facts + rules).
Prolog is the detective (search + unification + backtracking).

**DATALOG vs PROLOG:**

```
┌──────────────────────────────────────────────────────┐
│ Prolog: Turing-complete. Can express any computation.│
│   + Flexible: function terms, arithmetic, I/O        │
│   - May not terminate. Cut (!) breaks purity.        │
│   - Order of clauses affects behavior (procedural).  │
│                                                      │
│ Datalog: Prolog subset. Guaranteed to terminate.     │
│   + Safe recursive rules (no function terms)         │
│   + Declarative (order of rules doesn't matter)      │
│   + Can be optimized like SQL (query planning)        │
│   - Less expressive (no arbitrary computation)       │
│   Use Datalog when: database queries, static analysis│
│   Use Prolog when: AI reasoning, theorem proving     │
└──────────────────────────────────────────────────────┘
```

**MEMORY HOOK:**

"Prolog = Horn clauses + unification + backtracking depth-first.
Declare facts and rules; query for solutions.
Datalog = Prolog restricted to flat relations (no functor nesting).
Guaranteed to terminate. Used in: Datomic, CodeQL, Bloom.
Unification is bidirectional pattern matching with variable binding.
Backtracking = depth-first search with undo on failure.
Cut (!) = prune the search space (breaks purity).
Algorithm = Logic (you) + Control (the engine)."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Imagine a rule book: "If A is parent of B, and B is parent
of C, then A is grandparent of C." A detective robot reads
the rule book and the family album, then answers "Is tom
a grandparent of ann?" by checking: "Is tom a parent of
bob? Yes. Is bob a parent of ann? Yes. So tom is a grandparent
of ann." You wrote the rules; the robot did the searching.

**Level 2 - Student:**
```prolog
% Prolog syntax:
% Fact: animal(dog).
% Rule: mammal(X) :- animal(X), warm_blooded(X).
% Query: ?- mammal(What).

% Recursive rule - transitive ancestors:
ancestor(X, Y) :- parent(X, Y).          % base case
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z). % inductive

% ?- ancestor(tom, Who).
% Who = bob ; Who = ann ; Who = pat.  (all descendants)
```

**Level 3 - Professional:**
Datalog in Datomic (Clojure syntax):
```clojure
;; Datomic Datalog query: find all employees in engineering
;; with salary > 100000
(d/q '[:find ?name ?salary
       :where
       [?e :employee/department "engineering"]
       [?e :employee/name ?name]
       [?e :employee/salary ?salary]
       [(> ?salary 100000)]]
     db)
;; This is a Datalog query against an immutable database.
;; Rules are composable:
(def ancestor-rule
  '[[(ancestor ?x ?z) (parent ?x ?z)]
    [(ancestor ?x ?z) (parent ?x ?y) (ancestor ?y ?z)]])
```

**Level 4 - Senior Engineer:**
CodeQL: GitHub's code analysis tool uses Datalog-like queries
to find security vulnerabilities:
```ql
// Find SQL injection: user input flows to database query
import java

from MethodAccess call, RemoteFlowSource source
where
  call.getMethod().getName() = "executeQuery"
  and source.asExpr() = call.getAnArgument()
select call, "Potential SQL injection"
```
This is a Datalog query over the AST (Abstract Syntax Tree)
of Java code. The "facts" are: method calls, data flows,
variable references in the AST. The "rules" derive:
"this call receives untrusted data." The query finds
ALL instances in the codebase. This scales to millions
of lines of code because Datalog can be optimized like
SQL (semi-naive evaluation, tabling).

**Level 5 - Expert:**
Negation-as-failure (NAF) in Prolog: `\+(Goal)` succeeds
if `Goal` fails. This is NOT classical negation (proving
Goal is false) but CLOSED-WORLD ASSUMPTION: what cannot
be proven true is assumed false. Security implication:
`\+(authorized(User, Resource))` succeeds if the authorization
fact CANNOT BE DERIVED from the knowledge base. If the
knowledge base is incomplete (not all authorizations listed),
NAF may incorrectly deny access. In Datalog: negation is
stratified (no recursive negation) to preserve the well-founded
semantics and avoid this ambiguity. Stratified negation:
ensure that any predicate you negate is fully computed
before negation is applied.

---

### ⚙️ How It Works (Formal Basis)

**PROLOG RESOLUTION WITH BACKTRACKING:**

```
┌──────────────────────────────────────────────────────┐
│ Query: ?- grandparent(tom, Who).                     │
│                                                      │
│ Knowledge base:                                      │
│   parent(tom, bob). parent(bob, ann). parent(bob,pat)│
│   grandparent(X,Z) :- parent(X,Y), parent(Y,Z).     │
│                                                      │
│ Resolution:                                          │
│ 1. Goal: grandparent(tom, Who)                       │
│ 2. Match rule: grandparent(X,Z):-parent(X,Y),parent(Y,Z)│
│    Unify: X=tom, Z=Who (Z is free variable)          │
│ 3. New goals: parent(tom, Y), parent(Y, Who)         │
│ 4. Try parent(tom, Y): matches parent(tom, bob). Y=bob│
│ 5. New goals: parent(bob, Who)                       │
│ 6. Try parent(bob, Who): matches parent(bob, ann).   │
│    Who=ann. SUCCESS! Report: Who=ann.                │
│ 7. User asks for more (;) -> backtrack to step 6     │
│ 8. Try next fact: parent(bob, pat). Who=pat.         │
│    Report: Who=pat. SUCCESS!                         │
│ 9. No more parent(bob,_) facts -> backtrack to step 4│
│ 10. No more parent(tom,_) facts -> FAIL. Done.       │
│                                                      │
│ Result: Who=ann; Who=pat (all answers enumerated)    │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Procedural vs Logic Approach**

```prolog
% BAD: Using cut (!) procedurally - breaks purity,
% order-dependent, hard to compose
max(X, Y, X) :- X >= Y, !. % cut prunes alternatives
max(_, Y, Y).               % only reached if first clause cut
% Problem: if clauses are reordered, behavior changes.
% Can't query backwards: ?- max(3, Y, 5). may fail.

% GOOD: Pure declarative max using disjunction
max_pure(X, Y, X) :- X >= Y.
max_pure(X, Y, Y) :- Y > X.
% Pure: order doesn't matter. Bidirectional queries work.
% ?- max_pure(3, Y, 5). -> Y = 5. (correct!)
% More verbose but correct under all query modes.
```

```prolog
% FAILURE: Infinite loop - left recursion
parent(X, Z) :- parent(X, Y), parent(Y, Z). % WRONG
% Prolog's depth-first search will loop infinitely:
% try ancestor rule -> new goal: ancestor + ancestor ->
% try ancestor rule again -> infinite loop

% FIX: Ensure base case is first, avoid left recursion
ancestor(X, Y) :- parent(X, Y).  % base case first
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z). % no left recursion
% Recursion appears on the RIGHT of the conjunction.
% Prolog evaluates left-to-right: parent/2 is tried first
% (ground, terminates), then recursive call.
```

**Example 2 - Datalog for Access Control (Production Pattern)**

```prolog
% Datalog-style access control policy
% (actual Datalog in Oso, OPA, or Datomic)

% Facts (provided at query time):
% role(alice, admin).
% role(bob, viewer).
% resource_owner(alice, document_1).

% Rules:
can_read(User, Resource) :-
    role(User, admin).  % admins can read anything

can_read(User, Resource) :-
    role(User, viewer),
    resource_is_public(Resource).  % viewers: public only

can_write(User, Resource) :-
    role(User, admin).

can_write(User, Resource) :-
    resource_owner(User, Resource). % owners can write

% Query:
% ?- can_read(alice, document_1). -> true (alice is admin)
% ?- can_write(bob, document_1).  -> false (bob is viewer, not owner)
% ?- can_write(alice, document_1).-> true (alice is admin)
%
% This is how OPA (Open Policy Agent) works:
% Rego = a Datalog-like language for policy-as-code.
```

---

### ⚖️ Comparison Table

| Feature | Prolog | Datalog | SQL | Imperative |
|---|---|---|---|---|
| Paradigm | Logic (declarative) | Logic (declarative) | Relational (declarative) | Procedural |
| Recursion | Yes (may loop) | Yes (terminates) | Limited (CTEs) | Yes |
| Function terms | Yes | No | No | Yes |
| Termination | Not guaranteed | Guaranteed | Guaranteed | Not guaranteed |
| Query direction | Bidirectional | Bidirectional | Forward only | Forward only |
| Used in | AI, theorem provers | Datomic, CodeQL, OPA | RDBMS | General programs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Logic programming is for AI only and not used in production" | Datalog-based languages are used in production systems: Datomic (Clojure database) uses Datalog for queries. CodeQL (GitHub) uses a Datalog dialect to find security vulnerabilities in millions of code repositories. OPA (Open Policy Agent) uses Rego (Datalog-inspired) for policy-as-code. The Bloom language (UC Berkeley) used Datalog for distributed systems consistency. Prolog is less common in production but is used in theorem provers and constraint solvers embedded in IDEs and compilers. |
| "Prolog programs are just patterns matched top-to-bottom" | Prolog uses UNIFICATION (bidirectional pattern matching with variable binding), not just top-to-bottom equality checking. A query like `?- parent(tom, Y)` doesn't check if `parent(tom, Y)` equals a fact; it UNIFIES `parent(tom, Y)` with each fact, binding Y to the matching value. Unification is a general equation solver for tree-structured terms: it can unify partially specified structures, bind multiple variables simultaneously, and work bidirectionally. |
| "Backtracking is inefficient and Prolog can't scale" | Prolog's naive backtracking can be exponential in the worst case. However: (1) Tabling (memoization of subgoals, XSB Prolog) converts many exponential searches to polynomial. (2) Datalog evaluation uses semi-naive bottom-up evaluation (fixpoint iteration, not backtracking), which is efficient and can be query-planned like SQL. (3) Modern Prolog systems use constraint propagation to prune the search space. CodeQL runs Datalog queries on billion-line codebases efficiently precisely because it uses optimized Datalog evaluation, not naive Prolog backtracking. |
| "You can't do real computation in Prolog (no I/O, no state)" | Prolog has non-logical extensions: assert/retract (modify the knowledge base at runtime), arithmetic (is/2), I/O predicates (write, read, format), DCG (Definite Clause Grammars for parsing), and constraint libraries (CLP(FD) for finite domain constraint solving). Real Prolog programs (parsers, planners, expert systems) use these. The CORE of Prolog (Horn clauses + unification + backtracking) is pure declarative. The extensions are impure but pragmatically necessary for real programs. Functional programmers face the same tension: pure FP + IO monad = real programs. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Infinite Loop Due to Left Recursion**

**Symptom:** Prolog query hangs indefinitely. No output.
CPU at 100%.

**Root Cause:** Left-recursive rule. Depth-first search
recurses into the rule itself before making progress:
```prolog
% LEFT RECURSIVE - INFINITE LOOP:
ancestor(X, Z) :- ancestor(X, Y), parent(Y, Z). % wrong
% Proof attempt for ancestor(tom, ann):
%   Try rule: ancestor(tom, Y), parent(Y, ann)
%   Try rule: ancestor(tom, Y2), parent(Y2, Y), parent(Y,ann)
%   -> Infinite recursion before any parent is checked
```

**Fix:** Ensure base case is first clause; recursive call
appears to the RIGHT of base facts (right recursion):
```prolog
ancestor(X, Y) :- parent(X, Y).           % base: terminates
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z). % right recursion
% Now: parent(tom, bob) is tried first (ground fact, terminates)
% THEN ancestor(bob, Z) recurses on a STRICTLY SMALLER structure
```

**For Datalog:** Use tabling or switch to Datalog system
(guaranteed to terminate for any safe recursive rule).

---

**Security Note:**

Datalog-based access control (OPA/Rego) has a subtle
security property: the CLOSED-WORLD ASSUMPTION.
If a permission is not in the knowledge base, it is DENIED.
This is the secure default: deny unless explicitly granted.
Contrast with imperative access control where missing checks
default to ALLOW (the bug: developer forgets to check a permission).

In OPA:
```rego
# Default deny - secure by default
default allow = false

# Explicit allow rules:
allow {
    input.role == "admin"
}
allow {
    input.resource.owner == input.user
    input.method == "read"
}
# If no rule fires: allow = false (denied)
```

This is why Datalog-based policy languages (OPA, Cedar)
are preferred for authorization: the declarative closed-world
model is inherently deny-by-default, reducing the risk
of authorization bypass.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Declarative Programming` (CSF-025) - logic programming
  is the most declarative paradigm: specify what, not how
- `Functional Programming` (CSF-026) - contrasts with logic
  programming (both declarative but different models)

**Builds On This (learn these next):**
- `Category Theory for Programmers` (CSF-068) - deep
  mathematical foundations connecting type theory and logic

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ PROLOG       │ Facts + Rules + Queries                 │
│              │ Unification + Backtracking depth-first  │
├──────────────┼─────────────────────────────────────────┤
│ DATALOG      │ Prolog without function terms           │
│              │ Guaranteed termination. Query-optimizable│
├──────────────┼─────────────────────────────────────────┤
│ UNIFICATION  │ Bidirectional pattern match + bind vars │
│              │ parent(X,bob) + parent(tom,bob) -> X=tom│
├──────────────┼─────────────────────────────────────────┤
│ BACKTRACKING │ Depth-first + undo on failure           │
│              │ Try all alternatives, report all answers│
├──────────────┼─────────────────────────────────────────┤
│ CUT (!)      │ Prune search. Procedural. Breaks purity.│
│              │ Avoid in pure Datalog.                  │
├──────────────┼─────────────────────────────────────────┤
│ PRODUCTION   │ Datomic (Datalog), CodeQL, OPA (Rego)   │
│              │ Policy-as-code, static analysis         │
├──────────────┼─────────────────────────────────────────┤
│ SECURITY     │ Closed-world: deny unless explicitly    │
│              │ granted. Secure default for authz.      │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-068 (Category Theory), CSF-025       │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Logic programming = declare facts and rules (Horn clauses);
   the inference engine (Prolog/Datalog) does the search.
   Algorithm = Logic (you write) + Control (engine provides).
   Unification (bidirectional pattern matching with variable
   binding) is the key mechanism. Backtracking = depth-first
   search that undoes bindings when a path fails.
2. Datalog = Prolog restricted to flat relations (no function
   terms). Guaranteed to terminate. Can be query-planned like
   SQL. Used in production: Datomic (database queries), CodeQL
   (security analysis), OPA/Rego (policy-as-code). Datalog's
   closed-world assumption = deny-by-default (secure for authz).
3. Prolog's cut (!) prunes the search space but breaks
   declarative purity (makes the program order-dependent and
   harder to reason about). Pure Prolog = declarative (order
   of clauses doesn't affect results, only efficiency). Use
   Datalog systems for production authorization/analysis;
   use Prolog for AI reasoning, theorem proving, NLP parsing.

**Interview one-liner:**
"Logic programming: declare facts and rules (Horn clauses),
query for solutions; the engine uses unification and backtracking
to find all answers. Prolog: full Turing-complete (may not terminate).
Datalog: restricted subset - terminates, used in Datomic, CodeQL,
OPA. Closed-world assumption = deny by default (secure authz foundation)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Whenever a problem is fundamentally about DERIVING CONCLUSIONS
from a set of facts and rules, consider a declarative logic
approach. The imperative implementation of rule-following
(if-else chains, nested conditions, stateful traversal)
is almost always harder to read, harder to maintain, and
harder to reason about than the declarative equivalent.
Datalog-based policy engines (OPA, Cedar) replace thousands
of lines of imperative authorization code with tens of lines
of declarative rules. The rules are readable, testable,
and auditable. The engine handles the search. Recognize
the pattern: "I have facts; I have rules; I need to find
what follows" = consider logic programming.

**Where else this pattern appears:**

- **Build system dependency resolution** - Build tools (Bazel,
  Pants, Buck) use a Datalog-like reasoning to compute
  build dependencies. "If target A depends on library B,
  and B depends on C, then A transitively depends on C."
  This is a Horn clause over the dependency graph. Datalog's
  recursive rules handle transitive closure correctly and efficiently.
  The developer declares dependencies (facts); the build system
  derives the transitive closure (logic). Maven's dependency
  mediation and Gradle's dependency resolution are approximate
  implementations of this logic programming principle.
- **Semantic web and knowledge graphs** - SPARQL (W3C query
  language for RDF knowledge graphs) shares Prolog's unification
  model: variables in SPARQL patterns (`?person :worksAt ?company`)
  are unified against the knowledge graph facts. OWL (Web
  Ontology Language) uses description logic (related to Datalog)
  for inference over knowledge graphs. Knowledge graph SPARQL
  queries are, computationally, Datalog queries. The same
  techniques (tabling, semi-naive evaluation, query planning)
  apply to both.
- **Program analysis and verification** - Static analysis tools
  (Sonar, SpotBugs, Checkstyle) derive conclusions about
  code from facts about the AST. "This variable is uninitialized
  on some paths" is derived from control flow facts. Formal
  verification tools (TLA+, Alloy) express system invariants
  as logical constraints and verify they hold for all system
  states. Model checkers (SPIN, NuSMV) perform exhaustive
  backtracking search over system states - exactly Prolog's
  execution model applied to system models.

---

### 💡 The Surprising Truth

Prolog was designed in 1972 to be the implementation language
for an AI reasoning system. It became the dominant AI language
through the 1980s. IBM's Watson (Jeopardy champion, 2011)
uses a reasoning engine that, at its core, applies the same
principles as Prolog: match assertions against a knowledge
base using unification, find consistent sets of evidence.
But the most surprising Prolog application in everyday
engineering is hidden in plain sight: SQL. Codd's relational
model (1970) and Prolog's logic programming (1972) were
developed independently, but they are based on the same
mathematical foundation: first-order logic and relational
algebra. SQL's `WHERE` clause is a conjunction of goals
(exactly like Prolog's rule body). SQL's `JOIN` is
unification over relation columns. SQL's `WITH RECURSIVE`
is Datalog's recursive rules. SQL planners and Datalog
evaluators use overlapping optimization techniques
(projection push-down, predicate push-up, index exploitation).
When you write `SELECT u.name FROM users u JOIN orders o ON
u.id = o.user_id`, you are writing a Datalog-like query,
just with different syntax. Logic programming didn't displace
SQL - it became SQL.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[PROLOG]** Write a Prolog knowledge base for a small
   graph: `edge(a,b)`, `edge(b,c)`, `edge(c,d)`. Define a
   recursive `reachable(X, Y)` rule. Query: which nodes are
   reachable from a? Identify the risk of left recursion
   and write the rule to avoid it.

2. **[UNIFICATION]** Given: `f(X, g(Y, 2)) = f(3, g(Z, W))`,
   what is the most general unifier (MGU)? What bindings
   result? (Answer: X=3, Z=Y (or Y=Z), W=2).

3. **[DATALOG]** Write a Datalog access control policy with:
   facts for user roles, resource ownership, resource visibility.
   Define `can_read` and `can_write` rules. Explain why
   the closed-world assumption makes this policy secure-by-default.

4. **[PRODUCTION]** Describe how OPA/Rego uses Datalog principles.
   What is the relationship between Rego rules and Datalog
   Horn clauses? How does OPA's deny-by-default follow from
   the closed-world assumption?

5. **[CONTRAST]** Compare Prolog and SQL on: expressiveness,
   termination guarantees, query optimization, and use cases.
   Identify one thing SQL does that Prolog does poorly and
   one thing Prolog does that SQL does poorly.

---

### 🧠 Think About This Before We Continue

**Q1.** A developer says "Datalog can't express all algorithms,
so it's less powerful than a general-purpose language."
Is this a weakness or a feature?

*Hint: This is a FEATURE for the use cases where Datalog
is appropriate:
(1) Guaranteed termination: Datalog queries ALWAYS terminate.
    A Prolog or imperative program for the same query MIGHT
    loop. For access control (OPA), static analysis (CodeQL),
    and database queries, non-termination is a critical failure.
    Datalog's restricted expressiveness is the price for
    termination guarantees.
(2) Query optimization: Because Datalog is less expressive,
    a Datalog engine can optimize queries like a SQL database
    (predicate push-down, join reordering, index exploitation).
    Turing-complete languages don't admit such general optimization.
(3) Security: Datalog policies are inspectable, auditable,
    and provably terminating. A Turing-complete policy language
    (Lua plugins, Python scripts) could contain infinite loops
    or arbitrary computation - security risk.
The tradeoff: Datalog CANNOT express all computations (no
function terms, no arbitrary recursion). This is deliberately
chosen for safety, efficiency, and analyzability.
Expressive power and analyzability are inversely related:
the more expressive a language, the harder to analyze,
optimize, or guarantee its behavior.*

**Q2.** How does SQL's `WITH RECURSIVE` relate to Datalog's
recursive rules?

*Hint: `WITH RECURSIVE` (Common Table Expressions) is the
SQL-standard way to express recursive queries:
```sql
WITH RECURSIVE ancestor(id, ancestor_id) AS (
    -- Base case (Datalog: ancestor(X,Y) :- parent(X,Y).)
    SELECT id, parent_id FROM parent_of
    UNION ALL
    -- Recursive case (Datalog: ancestor(X,Z) :- parent(X,Y), ancestor(Y,Z).)
    SELECT a.id, p.parent_id
    FROM ancestor a JOIN parent_of p ON a.ancestor_id = p.id
)
SELECT * FROM ancestor WHERE id = 'bob';
```
This is EXACTLY Datalog's recursive rule evaluation using
semi-naive evaluation (fixpoint iteration):
- Compute the base set (direct parents).
- Iteratively add new facts derived from current set + rules.
- Stop when no new facts are added (fixpoint).
SQL CTEs and Datalog recursive rules are semantically equivalent.
The difference: SQL executes bottom-up (fixpoint iteration from
base facts). Prolog executes top-down (goal-directed search
with backtracking). Same results for terminating queries;
different performance profiles; different debugging experiences.
Both implement the same mathematical fixed-point semantics
from Datalog theory.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is unification in logic programming and how does it differ from pattern matching?"**

*Why they ask:* Tests understanding of the core mechanism of Prolog.

*Strong answer includes:*
- Pattern matching (ML, Haskell, Scala): match a VALUE against
  a PATTERN with specific constants. Variables in patterns
  bind to sub-values of the matched structure. Unidirectional:
  match value against pattern.
- Unification: match a TERM against another TERM, where
  BOTH can contain variables. Bidirectional: `parent(X, bob)
  = parent(tom, Y)` unifies with X=tom, Y=bob. Neither term
  is the "value" and neither is the "pattern" - they are
  equal partners. Any variable in either term can be bound.
- Most General Unifier (MGU): the minimal set of variable
  bindings that makes two terms equal. Unification finds
  the MGU.
- Application: Prolog queries are solved by unifying the
  query goal with fact heads (binding variables to values
  in the knowledge base). Type inference (HM, GHC) uses
  unification to solve type equations (e.g., `Int -> ?a = ?b -> Bool`
  -> `?b = Int, ?a = Bool`).

**Q2: "Where is Datalog used in production systems?"**

*Why they ask:* Tests awareness of practical applications of logic programming.

*Strong answer:*
- Datomic: Clojure database (Rich Hickey). Uses Datalog as
  the query language. Facts are immutable (append-only log).
  Queries are Datalog over the current (or historical) database
  value. Time-travel queries: query the database "as of" a
  specific point in time.
- CodeQL: GitHub's code analysis platform. Datalog queries
  over AST/CFG of code. Finds security vulnerabilities
  (SQL injection, XSS, path traversal) by expressing the
  vulnerability as a taint flow analysis query.
- OPA (Open Policy Agent): policy-as-code. Rego language is
  Datalog-inspired. Kubernetes admission control, API gateway
  authorization, service mesh policy. Declarative policies,
  closed-world deny-by-default.
- Bloom (UC Berkeley): research language for distributed
  systems. Datalog extended with temporal operators to
  express distributed system invariants and prove confluence
  (CALM analysis: Consistency As Logical Monotonicity).
