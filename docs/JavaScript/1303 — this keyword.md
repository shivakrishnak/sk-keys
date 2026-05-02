---
layout: default
title: "this keyword"
parent: "JavaScript"
nav_order: 1303
permalink: /javascript/this-keyword/
number: "1303"
category: JavaScript
difficulty: ★★★
depends_on: Execution Context, Scope, Functions, Prototype Chain
used_by: Binding (call/apply/bind), Arrow Functions, Class, Event Handlers, Methods
tags: #javascript, #advanced, #deep-dive, #browser, #nodejs, #internals
---

# 1303 — this keyword

`#javascript` `#advanced` `#deep-dive` `#browser` `#nodejs` `#internals`

⚡ TL;DR — A context-sensitive reference resolved at call time (not definition time) that points to the object a function is called upon, with four distinct binding rules.

| #1303 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | Execution Context, Scope, Functions, Prototype Chain | |
| **Used by:** | Binding (call/apply/bind), Arrow Functions, Class, Event Handlers, Methods | |

---

### 📘 Textbook Definition

In JavaScript, **`this`** is a special identifier whose value is determined by the **call site** (how a function is invoked), not by where the function is defined. There are four binding rules, evaluated in priority order: **(1) new binding** — when called with `new`, `this` is the newly created object; **(2) explicit binding** — when called via `call()`, `apply()`, or `bind()`, `this` is the specified object; **(3) implicit binding** — when called as a method on an object (`obj.fn()`), `this` is the owning object; **(4) default binding** — in all other cases, `this` is the global object in sloppy mode, or `undefined` in strict mode. Arrow functions do not have their own `this` — they inherit `this` lexically from their enclosing context.

---

### 🟢 Simple Definition (Easy)

`this` is JavaScript's way of saying "the object I'm currently working for." The same function can have a different `this` depending on how it's called — method call, standalone call, `new`, or `call()`/`apply()`.

---

### 🔵 Simple Definition (Elaborated)

Unlike most languages where `this` is fixed to the class instance, JavaScript's `this` is dynamic and determined at call time. Call the same function as a method on `user`? `this` is `user`. Call it standalone? `this` is the global object (or `undefined` in strict mode). Pass it as a callback? `this` might be lost entirely. Arrow functions solve the callback problem by not having their own `this` — they use whatever `this` was in the surrounding code when they were written. Understanding `this` means understanding the four rules and the arrow function exception.

---

### 🔩 First Principles Explanation

**Why `this` is dynamic — the design intent:**

```javascript
// The same logic should work for any user
function greet() {
  return `Hello, ${this.name}`;
}

const alice = { name: 'Alice', greet };
const bob   = { name: 'Bob',   greet };

alice.greet(); // "Hello, Alice" — this = alice
bob.greet();   // "Hello, Bob"   — this = bob
```

One function definition, different receivers — no duplication. This is method polymorphism without class hierarchies.

**The four binding rules (priority order):**

```
┌─────────────────────────────────────────────────┐
│  this BINDING RULES (highest → lowest priority) │
│                                                 │
│  1. new binding                                 │
│     new Fn() → this = brand new object          │
│                                                 │
│  2. Explicit binding                            │
│     fn.call(obj)  → this = obj                  │
│     fn.apply(obj) → this = obj                  │
│     fn.bind(obj)  → returns new fn, this = obj  │
│                                                 │
│  3. Implicit binding                            │
│     obj.fn()      → this = obj                  │
│                                                 │
│  4. Default binding                             │
│     fn()          → this = global (sloppy)      │
│                    → this = undefined (strict)  │
│                                                 │
│  SPECIAL: Arrow function                        │
│     No own this — inherits from enclosing scope │
└─────────────────────────────────────────────────┘
```

**The binding loss problem:**

The most common `this` bug in JavaScript:

```javascript
const user = {
  name: 'Alice',
  greet() { return `Hello, ${this.name}`; },
};

user.greet();              // "Hello, Alice" ✅
const fn = user.greet;
fn();                      // "Hello, undefined" ❌
// Detached from user — rule 4 applies (default)
setTimeout(user.greet, 0); // "Hello, undefined" ❌
// Callback detaches this — same problem
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT a receiver mechanism:**

```
Without dynamic this:

  Problem 1: Method must know receiver's name
    function greetAlice() { return alice.name; }
    function greetBob()   { return bob.name;   }
    → no code reuse  across objects

  Problem 2: Prototype methods can't work
    Dog.prototype.speak = function() {
      return ??? + ' barks';
      // Must reference 'this' — the specific instance
      // Without this: prototype methods useless
    }

  Problem 3: Constructors can't initialise instances
    function User(name) {
      ??? .name = name;
      // Without this: no way to write to new instance
    }
```

**WITH dynamic this:**

```
→ One method definition works for any receiver
→ Prototype methods access instance data via this
→ Constructors initialise the new object via this
→ call/apply allow borrowing methods across objects
→ bind creates partially applied functions with
  fixed receiver for callbacks
```

---

### 🧠 Mental Model / Analogy

> Think of `this` as a **name badge** assigned right before a function runs. If you're called as a method on an object, you get that object's badge. If you're called with `new`, you get a fresh blank badge. If you call with `call(obj)`, you're handed a specific badge. If called standalone, you get whatever the default badge is (global or nothing). Arrow functions are permanent employees who always wear the badge of the department they were hired into — they never swap badges.

"Badge" = the `this` binding
- "Called as method on obj" = implicit binding → obj's badge
- "call(obj) / apply(obj)" = explicit binding → forced badge
- "new Fn()" = new binding → fresh badge for new instance
- "Standalone call" = default binding → global/undefined
"Arrow function permanent department badge" = lexical this from enclosing scope

---

### ⚙️ How It Works (Mechanism)

**Rule 1 — new binding:**

```javascript
function User(name) {
  this.name = name; // this = newly created object
}
const u = new User('Alice');
// new: 1) creates {}, 2) sets [[Prototype]], 3) calls fn,
//      4) returns object
u.name; // 'Alice'
```

**Rule 2 — explicit binding:**

```javascript
function greet(greeting) {
  return `${greeting}, ${this.name}`;
}
const user = { name: 'Alice' };

greet.call(user, 'Hello');    // "Hello, Alice"
greet.apply(user, ['Hello']); // "Hello, Alice"
const boundGreet = greet.bind(user);
boundGreet('Hi');             // "Hi, Alice"
```

**Rule 3 — implicit binding (and loss):**

```javascript
const obj = {
  name: 'test',
  fn() { return this.name; },
};
obj.fn();               // 'test'  — implicit binding

const detached = obj.fn;
detached();             // undefined (strict) / global (sloppy)
// Rule 4 applies — implicit binding LOST on detach
```

**Rule 4 — default binding:**

```javascript
function show() { return this; }
show();             // window (browser sloppy)
                    // undefined (strict mode)

'use strict';
function strictShow() { return this; }
strictShow();       // undefined
```

**Arrow function — lexical this:**

```javascript
const obj = {
  name: 'Alice',
  delayedGreet() {
    // BAD: regular function loses this in callback
    setTimeout(function() {
      console.log(this.name); // undefined
    }, 100);

    // GOOD: arrow inherits this from delayedGreet
    setTimeout(() => {
      console.log(this.name); // 'Alice'
    }, 100);
  },
};
obj.delayedGreet();
```

---

### 🔄 How It Connects (Mini-Map)

```
Function is created
(this not bound yet)
        ↓
Function is CALLED
(this determined by call site)
        ↓
  ┌─ new? ─────────────────→ new object
  ├─ .call/.apply/.bind? ──→ specified obj
  ├─ obj.fn()? ────────────→ obj
  └─ fn()? ────────────────→ global/undefined
        ↓
  Arrow function exception:
  no own this → inherits from
  enclosing lexical context
        ↓
  Used by:
  Binding (call/apply/bind) → explicit control
  Class constructors → new binding
  Event handlers → implicit (element)
  React class components → needs .bind or arrow
```

---

### 💻 Code Example

**Example 1 — The four rules in one file:**

```javascript
'use strict';
function identify() { return this?.name ?? 'no name'; }

// Rule 4: default
identify();                  // undefined (strict)

// Rule 3: implicit
const obj = { name: 'obj', identify };
obj.identify();              // 'obj'

// Rule 2: explicit
identify.call({ name: 'explicit' }); // 'explicit'

// Rule 1: new
function Named(n) { this.name = n; }
new Named('new').name;       // 'new'
```

**Example 2 — Class methods losing `this` in React (common pitfall):**

```javascript
// BAD: method loses this when passed as callback
class Component extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  handleClick() {
    this.setState({ count: this.state.count + 1 });
    // this is undefined — handler detached from instance
  }
  render() {
    return <button onClick={this.handleClick}>
      {this.state.count}
    </button>;
  }
}

// FIX 1: bind in constructor
constructor(props) {
  super(props);
  this.handleClick = this.handleClick.bind(this);
}

// FIX 2: class field arrow function (preferred)
handleClick = () => {
  this.setState({ count: this.state.count + 1 });
};
```

**Example 3 — Method borrowing via call:**

```javascript
// Borrow Array methods for array-like objects
function sum() {
  // arguments is array-like, not an array
  return Array.prototype.reduce.call(
    arguments,
    (acc, n) => acc + n,
    0
  );
}
sum(1, 2, 3, 4); // 10
```

**Example 4 — bind for partial application with fixed this:**

```javascript
const logger = {
  prefix: '[API]',
  log(level, msg) {
    console.log(`${this.prefix} [${level}] ${msg}`);
  },
};

const info  = logger.log.bind(logger, 'INFO');
const error = logger.log.bind(logger, 'ERROR');

info('Server started');  // [API] [INFO] Server started
error('DB timeout');     // [API] [ERROR] DB timeout
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| this refers to the function itself | this refers to the call site receiver; `arguments.callee` (deprecated) or a named function expression refers to the function |
| Arrow functions cannot be used as methods | They can, but they won't have their own this — this will be whatever the enclosing context was at definition time, which is often wrong for object methods |
| this is lexically bound in all functions | Only arrow functions have lexical this; all other functions use call-time dynamic binding |
| bind() changes this of the original function | bind() returns a NEW function with the binding fixed; the original is unchanged |
| In strict mode, this is always undefined | In strict mode, default binding (standalone call) gives undefined; method calls and constructor calls still bind correctly |
| class methods automatically bind this to the instance | class methods are defined on the prototype — if detached and called as a callback, this is lost exactly as with regular functions |

---

### 🔥 Pitfalls in Production

**1. this lost in timer callbacks**

```javascript
// BAD: method loses this inside setTimeout
class Poller {
  constructor(url) { this.url = url; }
  start() {
    setInterval(function() {
      fetch(this.url); // this = global/undefined
    }, 1000);
  }
}

// GOOD: arrow function inherits this from start()
class Poller {
  constructor(url) { this.url = url; }
  start() {
    setInterval(() => {
      fetch(this.url); // this = Poller instance ✅
    }, 1000);
  }
}
```

**2. Extracting prototype methods for performance — losing this**

```javascript
// BAD: destructuring methods loses this
const { save, validate } = userService;
save(data);    // this = undefined → TypeError

// GOOD: bind or use the object directly
const { save, validate } = {
  save:     userService.save.bind(userService),
  validate: userService.validate.bind(userService),
};
// OR: just call userService.save(data) directly
```

**3. this in class field arrow vs prototype method — memory cost**

```javascript
// Arrow class field: each INSTANCE gets its OWN copy
// of the function — 1000 instances = 1000 functions
class ExpensiveComponent {
  render = () => { /* ... */ }; // per-instance copy
}

// Prototype method: ONE shared function, but needs bind
class EfficientComponent {
  render() { /* ... */ }  // one shared function
  constructor() {
    this.render = this.render.bind(this); // per-instance
    // bind still creates per-instance fn, but from proto
  }
}
// Use arrow class fields for event handlers (ergonomic);
// use prototype methods when creating thousands of instances
```

---

### 🔗 Related Keywords

- `Binding (call, apply, bind)` — the explicit mechanisms to set `this` at call time or bind permanently
- `Arrow Functions` — capture `this` lexically from enclosing context; have no own `this`
- `Execution Context` — each execution context has a `this` binding determined at call time
- `Prototype Chain` — prototype methods depend on `this` to reference the specific instance
- `Class (ES6+)` — class methods use implicit binding (rule 3); constructors use new binding (rule 1)
- `Closure` — often the solution to `this` loss — capture `this` with `const self = this` or use arrow functions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ this = who called the function, not where │
│              │ it was defined. Four rules, arrow special. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Writing methods, constructors, event      │
│              │ handlers; using call/apply to borrow      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using regular fn in callbacks where this  │
│              │ must be preserved — use arrow instead     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "this is a question answered at runtime,  │
│              │  not at write time — except arrows."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Binding → Arrow Functions → Class         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Node.js Express middleware is written as a class method: `class AuthMiddleware { verify(req, res, next) { if (!this.db) ... } }`. When registered as `app.use(auth.verify)`, it throws `TypeError: Cannot read property 'db' of undefined`. Trace exactly which of the four binding rules applies, whether strict mode changes anything, and describe three distinct fixes — explaining the trade-off between per-request function allocation and prototype-method sharing for each.

**Q2.** Consider `const fn = obj.method.bind(null)` where obj.method uses `this.data`. Now `fn.call(anotherObj)` is called on the bound function. Explain which rule wins and why — and then explain what happens when `new fn()` is called on a `bind()`-bound function, given that the ECMAScript spec says `new` overrides `bind`'s this. Trace the exact steps from the spec.

