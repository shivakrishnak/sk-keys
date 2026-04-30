---
layout: default
title: "Binding (call, apply, bind)"
parent: "JavaScript"
nav_order: 557
permalink: /javascript/binding-call-apply-bind/
number: "557"
category: JavaScript
difficulty: ★★☆
depends_on: this keyword, Functions, Prototype Chain
used_by: Method borrowing, Partial application, Event handlers, Arrow Functions
tags: #javascript, #intermediate, #browser, #nodejs
---

# 557 — Binding (call, apply, bind)

`#javascript` `#intermediate` `#browser` `#nodejs`

⚡ TL;DR — Three Function.prototype methods that explicitly control what `this` refers to when a function is invoked: call and apply invoke immediately, bind returns a new function with this locked.

| #557 | Category: JavaScript | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | this keyword, Functions, Prototype Chain | |
| **Used by:** | Method borrowing, Partial application, Event handlers, Arrow Functions | |

---

### 📘 Textbook Definition

`Function.prototype.call(thisArg, arg1, arg2, ...)`, `Function.prototype.apply(thisArg, [args])`, and `Function.prototype.bind(thisArg, ...partialArgs)` are the three explicit `this`-binding mechanisms. `call` and `apply` invoke the function immediately with the specified `this` value, differing only in how arguments are passed (individually vs as an array). `bind` returns a **new function** with `this` permanently fixed to `thisArg`; additional arguments passed to `bind` become prepended partial arguments on every call to the returned function. A bound function's `this` cannot be overridden by a later `call`, `apply`, or `bind` — only `new` can override a bound `this`.

---

### 🟢 Simple Definition (Easy)

`call` and `apply` let you run a function "as if" it belonged to a different object. `bind` creates a copy of the function with the object permanently attached, for use later.

---

### 🔵 Simple Definition (Elaborated)

By default, `this` in a function is determined by how you call it. `call`, `apply`, and `bind` let you override that. `call` and `apply` are identical in effect — they call the function right now with a specific `this`. The difference: `call` takes arguments one by one, `apply` takes them as an array. `bind` doesn't call the function — it returns a new function that, whenever called, will always use the specified `this`. `bind` is essential for event handlers and callbacks where you need `this` to refer to a specific object even though you're not calling the function directly.

---

### 🔩 First Principles Explanation

**The problem: this is lost when you detach a method:**

```javascript
const user = {
  name: 'Alice',
  greet() { return `Hello, ${this.name}`; },
};

const fn = user.greet; // detached — this is lost
fn();                   // "Hello, undefined"

// setTimeout, event listeners, Promise callbacks —
// all receive a function reference, not a bound method
setTimeout(user.greet, 1000); // this = global/undefined
```

**Solution: explicit binding lets you specify the receiver:**

```javascript
// call — invoke now with explicit this
user.greet.call({ name: 'Bob' }); // "Hello, Bob"

// apply — invoke now, args as array
function sum(a, b) { return a + b; }
sum.apply(null, [3, 4]); // 7 — useful when args are array

// bind — create bound function for later
const boundGreet = user.greet.bind(user);
setTimeout(boundGreet, 1000); // "Hello, Alice" — this preserved
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT call/apply/bind:**

```
Without explicit binding:

  Problem 1: Method borrowing impossible
    Arrays have .forEach, .map, etc.
    NodeLists, arguments object do not
    → must convert to array first with [...args]
      before ES6, this was the only option

  Problem 2: Callbacks always lose this
    button.addEventListener('click', obj.handler);
    // obj.handler runs with this = button (DOM element)
    // not with this = obj — silent bug

  Problem 3: Partial application requires closures
    // Pre-bind: need wrapper function each time
    const logError = function(msg) {
      logger.log('ERROR', msg);
    };
    // bind: const logError = logger.log.bind(logger, 'ERROR')
```

**WITH call/apply/bind:**

```
→ Method borrowing: Array.prototype.slice.call(args)
→ Constructors composing: Parent.call(this, ...)
→ Bound callbacks: fn.bind(this) preserves receiver
→ Partial application: bind prepends fixed args
→ Polyfill patterns: safely borrow native methods
```

---

### 🧠 Mental Model / Analogy

> `call` and `apply` are like **borrowing a specialist** from another team for one meeting — they do the work right now as if they belong to your team. `bind` is like **hiring a contractor** permanently assigned to your team — they always work under your management badge, no matter who requests them.

"Borrowing for one meeting" = call/apply — immediate, one-time this override
"Permanently assigned contractor" = bind — returns new function with fixed this
"Management badge" = the this binding
"Who requests them" = later call()/apply() attempts (ignored by bind)

---

### ⚙️ How It Works (Mechanism)

**call vs apply — argument passing:**

```javascript
function greet(greeting, punctuation) {
  return `${greeting}, ${this.name}${punctuation}`;
}

const user = { name: 'Alice' };

// call: args listed individually
greet.call(user, 'Hello', '!');  // "Hello, Alice!"

// apply: args as array — useful when args are dynamic
const args = ['Hello', '!'];
greet.apply(user, args);         // "Hello, Alice!"

// ES6+: spread replaces most apply use cases
greet.call(user, ...args);       // "Hello, Alice!"
```

**bind — partial application:**

```javascript
function multiply(factor, value) {
  return factor * value;
}

// Bind null (no this needed), pre-fill factor = 2
const double = multiply.bind(null, 2);
const triple = multiply.bind(null, 3);

double(5);  // 10
triple(5);  // 15
double(8);  // 16

// This is partial application — a form of currying
```

**Implementing bind from scratch (simplified):**

```javascript
Function.prototype.myBind = function(thisArg, ...preArgs) {
  const fn = this;
  return function(...callArgs) {
    return fn.apply(thisArg, [...preArgs, ...callArgs]);
  };
};
```

**Bound function vs new:**

```javascript
function Point(x, y) {
  this.x = x;
  this.y = y;
}
const BoundPoint = Point.bind({ notUsed: true }, 10);
// new overrides bind's this:
const p = new BoundPoint(20); // this = new object, NOT { notUsed: true }
p.x; // 10  (pre-filled arg)
p.y; // 20  (call arg)
```

---

### 🔄 How It Connects (Mini-Map)

```
this keyword (rule 2: explicit binding)
        ↓
  call(thisArg, ...args)   → invoke immediately
  apply(thisArg, [args])   → invoke immediately
  bind(thisArg, ...partial)→ return new bound fn
        ↓
  Used for:
  ├── Method borrowing (Array.prototype on NodeList)
  ├── Super constructor call (Parent.call(this,...))
  ├── Callback binding (setTimeout, DOM events)
  └── Partial application (factory of specialised fns)
        ↓
  Arrow Functions (ES6 alternative)
  (lexical this — makes bind less necessary for callbacks)
```

---

### 💻 Code Example

**Example 1 — Method borrowing:**

```javascript
// NodeList doesn't have array methods
const divs = document.querySelectorAll('div');
// divs.forEach works (ES6) but historically:
const arr = Array.prototype.slice.call(divs);
arr.map(div => div.classList.add('processed'));

// arguments object (not an array):
function sum() {
  return Array.prototype.reduce.call(
    arguments,
    (acc, n) => acc + n,
    0
  );
}
sum(1, 2, 3); // 6
```

**Example 2 — Constructor composition:**

```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() {
  return `${this.name} makes noise`;
};

function Dog(name, breed) {
  Animal.call(this, name); // inherit own properties via call
  this.breed = breed;
}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

const d = new Dog('Rex', 'Lab');
d.speak(); // 'Rex makes noise'
```

**Example 3 — Bind for event handlers:**

```javascript
class SearchBar {
  constructor() {
    this.query = '';
    this.input = document.querySelector('#search');

    // Bind preserves `this` when DOM calls the handler
    this.input.addEventListener(
      'input',
      this.handleInput.bind(this)
    );
  }
  handleInput(event) {
    this.query = event.target.value; // this = SearchBar
    this.debounceSearch();
  }
  debounceSearch() { /* ... */ }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| bind() modifies the original function | bind() returns a NEW function; the original is unchanged. The new function internally calls the original via call/apply |
| apply() is slower than call() | In modern V8 the performance difference is negligible. Use whichever matches your argument shape |
| A bind()ed function's this can be changed with call() | call() and apply() on a bound function are ignored — the bind wins. Only new can override bind's this |
| bind() with no this argument (null/undefined) means global | In strict mode: null/undefined this stays null/undefined. In sloppy mode: null/undefined defaults to global |
| Arrow functions work with call/apply/bind | Arrow functions ignore the thisArg entirely — their this is always the lexical enclosing this, regardless of call/apply/bind |

---

### 🔥 Pitfalls in Production

**1. bind() in render creating new functions on every call**

```javascript
// BAD: bind in JSX creates new fn every render
// React sees a new function reference → re-renders child
class Parent extends React.Component {
  handleClick(id) { /* ... */ }
  render() {
    return this.props.items.map(item =>
      <Child
        onClick={this.handleClick.bind(this, item.id)}
        key={item.id}
      />
    );
  }
}

// GOOD: bind in constructor or use arrow class fields
class Parent extends React.Component {
  handleClick = (id) => { /* ... */ };
  render() {
    return this.props.items.map(item =>
      <Child
        onClick={() => this.handleClick(item.id)}
        key={item.id}
      />
    );
  }
}
// For perf-critical lists: use data-attributes + delegation
```

**2. apply() with large arrays causing stack overflow**

```javascript
// BAD: apply spreads array onto call stack
const hugeArray = new Array(500_000).fill(1);
Math.max.apply(null, hugeArray);
// RangeError: Maximum call stack size exceeded
// apply puts all elements on the call stack as arguments

// GOOD: reduce or loop
const max = hugeArray.reduce(
  (m, v) => (v > m ? v : m), -Infinity
);
// Or: Math.max(...hugeArray.slice(0, 100_000))
// if you know array is bounded
```

---

### 🔗 Related Keywords

- `this keyword` — defines what call/apply/bind control; they implement rule 2 (explicit binding)
- `Arrow Functions` — ES6 alternative to bind for callback this preservation; lexical this
- `Partial Application` — a use case of bind; pre-fill arguments to create specialised functions
- `Prototype Chain` — call/apply allow borrowing methods defined on any object's prototype
- `Execution Context` — each function call has a this binding; call/apply set it explicitly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ call/apply invoke with explicit this now; │
│              │ bind returns new fn with this locked      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Method borrowing, super calls in ctor,    │
│              │ partial application, callback binding     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ In render methods (creates new fn each    │
│              │ time); apply with huge arrays (stack risk) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "call borrows for one meeting,            │
│              │  bind assigns permanently."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Arrow Functions → Currying →              │
│              │ Partial Application                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a base utility class `Emitter` with an `on(event, handler)` method. A subclass `ApiClient extends Emitter` calls `super.on('error', this.handleError)` in its constructor. After `new ApiClient()` is instantiated, an error fires but `this.handleError` runs with `this = undefined`. Trace exactly why — stepping through which binding rule applies at each call site — and explain why `this.on('error', this.handleError.bind(this))` fixes it but `this.on('error', () => this.handleError())` is subtly different in one edge case.

**Q2.** `Function.prototype.bind` is specified to produce a bound function whose `length` property is `Math.max(0, targetFn.length - partialArgs.length)`. Explain why this matters for functions that rely on `fn.length` to detect arity (e.g., Express middleware detection, which uses `fn.length === 4` to identify error-handling middleware). What specific bug arises when binding an Express error handler with `bind`, and what is the fix?

