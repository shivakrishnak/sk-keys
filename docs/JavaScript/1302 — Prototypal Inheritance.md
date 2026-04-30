---
layout: default
title: "Prototypal Inheritance"
parent: "JavaScript"
nav_order: 1302
permalink: /javascript/prototypal-inheritance/
number: "1302"
category: JavaScript
difficulty: ★★☆
depends_on: Prototype Chain, Object.create, Functions, var / let / const
used_by: Class (ES6+), Mixins, Object.assign, instanceof, Factory Functions
tags: #javascript, #intermediate, #browser, #nodejs, #pattern
---

# 1302 — Prototypal Inheritance

`#javascript` `#intermediate` `#browser` `#nodejs` `#pattern`

⚡ TL;DR — JavaScript's native inheritance model where objects inherit directly from other objects via the prototype chain, without requiring class hierarchies.

| #1302 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | Prototype Chain, Object.create, Functions, var / let / const | |
| **Used by:** | Class (ES6+), Mixins, Object.assign, instanceof, Factory Functions | |

---

### 📘 Textbook Definition

**Prototypal inheritance** is the object composition model native to JavaScript in which objects inherit properties and methods directly from other objects through the `[[Prototype]]` chain, rather than from class definitions at instantiation time. There are two primary forms: **prototype delegation** (an object's `[[Prototype]]` points to a prototype object, and property lookups delegate up the chain) and **concatenative inheritance** (properties are copied from source objects using `Object.assign` or spread). Both forms can be combined. ES6 `class` syntax provides a classical-looking façade but compiles directly to prototypal mechanics.

---

### 🟢 Simple Definition (Easy)

In prototypal inheritance, objects inherit from other objects — not from blueprints. You can take an existing object and create new ones that share its behaviour, then customise them further.

---

### 🔵 Simple Definition (Elaborated)

Classical inheritance (Java, C++) says: "Write a class, create instances from it." Prototypal inheritance says: "Take an existing object, delegate to it, add what you need." JavaScript uses the prototype chain to implement this — when you look up a property on an object, JavaScript walks up to the prototype object if necessary. This means you can set up inheritance between any two objects without defining a class first. The ES6 `class` keyword is popular and useful, but it's just cleaner syntax over the same prototype delegation that has always existed in JavaScript.

---

### 🔩 First Principles Explanation

**The fundamental design choice:**

Class-based languages instantiate objects from static blueprints. Prototypal languages link objects to other objects. JavaScript chose prototypal:

```
┌──────────────────────────────────────────────┐
│  CLASS-BASED (Java)                          │
│                                              │
│  Class definition (blueprint)                │
│      ↓ instantiation                         │
│  Object instance                             │
│  (copy of structure, not linked to class)    │
│                                              │
│  PROTOTYPAL (JavaScript)                     │
│                                              │
│  Prototype object (live object)              │
│      ↑ [[Prototype]] link                    │
│  New object (delegates up to prototype)      │
└──────────────────────────────────────────────┘
```

**Three patterns for prototypal inheritance:**

**Pattern 1 — Delegation via Object.create:**

```javascript
const animalProto = {
  breathe() { return 'breathing'; },
};
const dog = Object.create(animalProto);
dog.bark = function() { return 'woof'; };
// dog delegates unknowns to animalProto
```

**Pattern 2 — Constructor + prototype (classic):**

```javascript
function Animal(name) { this.name = name; }
Animal.prototype.breathe = function() { return 'breathing'; };
const dog = new Animal('Rex');
// dog.[[Prototype]] === Animal.prototype
```

**Pattern 3 — Concatenative (mixin / stamp):**

```javascript
// Copy properties — no chain link
const swimmer = { swim() { return 'swimming'; } };
const flyer   = { fly()  { return 'flying'; } };
const duck = Object.assign({}, swimmer, flyer, {
  name: 'Donald'
});
// duck has own copies of swim and fly
```

---

### ❓ Why Does This Exist (Why Before What)

**Without a shared-behaviour mechanism:**

```
Without prototypal inheritance:

  Option A: Copy methods to each object
    → Memory waste — 1M users × 5 methods
    → Updating a method requires patching all

  Option B: Use global functions
    → No encapsulation — function namespace collision
    → `updateUser(user, ...)` vs `user.update(...)`
    → Hard to compose related behaviour

  Option C: Classical class hierarchy (forced)
    → Fragile base class problem
    → Deep hierarchies resist change
    → "Gorilla-banana-jungle" problem:
      you wanted a banana but got the
      gorilla holding it and the jungle
```

**WITH prototypal inheritance (delegation):**

```
→ Share methods via prototype — one copy, many users
→ Object.create for any-to-any inheritance
→ Mix multiple behaviours via concatenative
→ No class taxonomy needed — just compose
→ Runtime extensibility: add to prototype,
  all instances immediately get it
```

---

### 🧠 Mental Model / Analogy

> Prototypal inheritance is like a **franchise model**. The franchise HQ (prototype) has the standard operating procedures (methods). Each location (object instance) personalises it with their own staff and address (own properties). When a customer asks "do you have WiFi?" the staff member doesn't know, but escalates to the franchise handbook (prototype lookup). The handbook has the answer once — all 500 locations benefit.

"Franchise HQ handbook" = prototype object
"Each location" = object instance
"Local staff and address" = object's own properties
"Escalating to the handbook" = prototype chain delegation
"All locations get update instantly" = modifying prototype affects all instances

---

### ⚙️ How It Works (Mechanism)

**Object.create — the cleanest form:**

```javascript
// Proto object — shared behaviour
const vehicleProto = {
  start() { return `${this.brand} starts`; },
  stop()  { return `${this.brand} stops`; },
};

// Child objects — own data, delegated behaviour
const car = Object.create(vehicleProto);
car.brand = 'Toyota';
car.doors = 4;

const bike = Object.create(vehicleProto);
bike.brand = 'Honda';
bike.wheels = 2;

car.start();  // "Toyota starts" — found on vehicleProto
bike.start(); // "Honda starts"  — same shared method
```

**Class as prototypal inheritance sugar:**

```javascript
class Shape {
  constructor(color) { this.color = color; }
  describe() { return `A ${this.color} shape`; }
}

class Circle extends Shape {
  constructor(color, r) {
    super(color);
    this.radius = r;
  }
  area() { return Math.PI * this.radius ** 2; }
}

// Under the hood:
// Circle.prototype.__proto__ === Shape.prototype
// new Circle(...).__proto__ === Circle.prototype
```

**Mixin pattern — concatenative inheritance:**

```javascript
// Compose behaviours without a class hierarchy
const Serializable = {
  serialize: () => JSON.stringify(this),
};
const Validatable = {
  validate: () => Object.keys(this).every(k => this[k]),
};

function createUser(name, email) {
  return Object.assign(
    Object.create(null), // no Object.prototype baggage
    Serializable,
    Validatable,
    { name, email }
  );
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Prototype Chain (mechanism)
        ↓
PROTOTYPAL INHERITANCE  ← you are here
(three flavours: delegation, constructor, mixin)
        ↓
  ┌──────────────────────────────────────────┐
  │  Class (ES6+) — declarative sugar        │
  │  Object.create — explicit delegation     │
  │  Object.assign — concatenative mixin     │
  │  Factory Functions — closure + proto     │
  └──────────────────────────────────────────┘
        ↓
  instanceof (chain membership)
  hasOwnProperty (own vs inherited)
  super (walk up one level in chain)
```

---

### 💻 Code Example

**Example 1 — Delegation vs concatenative, side by side:**

```javascript
// Delegation — changes to proto affect all instances
const proto = { greet: () => 'hello' };
const a = Object.create(proto);
const b = Object.create(proto);
proto.greet = () => 'hi'; // changes for BOTH a and b

// Concatenative — independent copies
const mixin = { greet: () => 'hello' };
const c = Object.assign({}, mixin);
const d = Object.assign({}, mixin);
mixin.greet = () => 'hi'; // c and d UNAFFECTED
```

**Example 2 — Factory function with shared prototype:**

```javascript
const personProto = {
  fullName() { return `${this.first} ${this.last}`; },
  greet()    { return `Hi, I'm ${this.fullName()}`; },
};

function createPerson(first, last) {
  const p = Object.create(personProto);
  p.first = first;
  p.last = last;
  return p;
}

const alice = createPerson('Alice', 'Smith');
alice.greet(); // "Hi, I'm Alice Smith"
alice instanceof Object;     // true
Object.getPrototypeOf(alice) === personProto; // true
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ES6 classes make prototypal inheritance obsolete | class is syntactic sugar — the runtime still uses prototypal inheritance. Understanding prototypes is required to debug class-based code |
| Prototypal inheritance is weaker than classical | Prototypal is more flexible — any object can inherit from any other at runtime; classical hierarchies are fixed at compile time |
| Object.assign creates prototypal inheritance | Object.assign copies properties (concatenative inheritance) — it does NOT set up [[Prototype]] links. The result inherits from Object.prototype only |
| super in class methods works differently from prototype chain | super simply walks up the prototype chain; `super.method()` is equivalent to `ParentClass.prototype.method.call(this)` |

---

### 🔥 Pitfalls in Production

**1. Mutable reference types on prototype accidentally shared**

```javascript
// BAD: array property on prototype — shared by all
function Queue() {}
Queue.prototype.items = []; // one array, all instances

const q1 = new Queue(), q2 = new Queue();
q1.items.push('A');
console.log(q2.items); // ['A'] — same array!

// GOOD: own property in constructor
function Queue() { this.items = []; }
```

**2. Extending native prototypes in libraries**

```javascript
// BAD: polyfill that stomps over standard if exists
Array.prototype.first = function() { return this[0]; };
// If spec later adds Array.prototype.first with different
// semantics → your polyfill breaks spec behaviour
// All third-party code using Array is affected

// GOOD: feature-detect before adding
if (!Array.prototype.at) {
  Array.prototype.at = function(i) { /* ponyfill */ };
}
// Even better: use a ponyfill (standalone function)
// instead of patching the prototype
```

---

### 🔗 Related Keywords

- `Prototype Chain` — the underlying mechanism; prototypal inheritance is the pattern built on top of it
- `Object.create` — creates an object with explicit prototype; purest form of prototypal inheritance
- `Class (ES6+)` — declarative syntax for constructor + prototype setup; compiles to prototypal mechanics
- `Mixin` — concatenative inheritance pattern using Object.assign or spread
- `instanceof` — tests prototype chain membership; works because of the prototype link
- `Factory Functions` — an alternative to constructors that use closure and Object.create together
- `Prototype Chain` — implements the delegation-based property lookup that makes this work

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Objects inherit from objects, not classes;│
│              │ three flavours: delegation, ctor, mixin   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sharing behaviour efficiently; when class │
│              │ hierarchies feel over-engineered          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Deep inheritance chains (> 3 levels);     │
│              │ never put mutable data on shared proto    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Inherit from objects, not blueprints —   │
│              │  link, don't copy."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Class (ES6+) → Mixin → Object.create      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A UI component library uses class-based inheritance with a 5-level chain: `EventEmitter → Component → FormComponent → InputComponent → TextInput`. A performance audit shows that `TextInput.render()` is 3× slower than an equivalent object-literal implementation. Using your knowledge of prototype chain traversal and V8's hidden class system, identify at least two specific mechanisms that explain this slowdown — and describe the refactor (not rewriting in C++) that would bring performance on par.

**Q2.** JavaScript's `Object.create(null)` creates an object with `null` as its `[[Prototype]]` — no inherited properties at all, not even `toString` or `hasOwnProperty`. Explain two production use cases where this is specifically the right choice over a plain `{}` object, and then explain the one gotcha that bites developers who use `Object.create(null)` objects with code that expects standard object behaviour.

