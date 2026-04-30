---
layout: default
title: "Prototype Chain"
parent: "JavaScript"
nav_order: 1301
permalink: /javascript/prototype-chain/
number: "1301"
category: JavaScript
difficulty: ★★★
depends_on: JavaScript Engine (V8), Object, Heap (JS), Functions
used_by: Prototypal Inheritance, Class (ES6+), Object.create, instanceof, hasOwnProperty
tags: #javascript, #internals, #advanced, #deep-dive, #browser, #nodejs
---

# 1301 — Prototype Chain

`#javascript` `#internals` `#advanced` `#deep-dive` `#browser` `#nodejs`

⚡ TL;DR — The linked chain of objects through which JavaScript resolves property lookups, walking from an object up through its prototype references until found or reaching null.

| #1301 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | JavaScript Engine (V8), Object, Heap (JS), Functions | |
| **Used by:** | Prototypal Inheritance, Class (ES6+), Object.create, instanceof, hasOwnProperty | |

---

### 📘 Textbook Definition

The **Prototype Chain** is the mechanism by which JavaScript resolves property and method access on objects. Every object has an internal `[[Prototype]]` slot (accessible via `Object.getPrototypeOf()` or the deprecated `__proto__`) that references another object — its prototype. When a property is accessed on an object and not found on the object itself, the engine walks up the prototype chain — checking each prototype in sequence — until the property is found or the chain ends at `null`. All ordinary objects ultimately inherit from `Object.prototype`. Functions have both a `prototype` property (used when the function is called as a constructor) and `[[Prototype]]` (their own inheritance chain).

---

### 🟢 Simple Definition (Easy)

Every JavaScript object has a "parent." When you access a property that isn't on the object itself, JavaScript asks the parent. If the parent doesn't have it either, it asks the grandparent — all the way up until there's nothing left to ask.

---

### 🔵 Simple Definition (Elaborated)

JavaScript doesn't use classical inheritance like Java or C++. Instead, objects are linked together through a chain of prototypes. When you look up `obj.method`, JavaScript first checks `obj` itself, then follows the `[[Prototype]]` link to the next object, checks that, and continues up the chain. This makes it possible to share methods across many objects without copying them — all instances share the same method via the prototype chain. The ES6 `class` syntax is built entirely on top of this mechanism — it doesn't replace prototypal inheritance, it provides a cleaner way to set it up.

---

### 🔩 First Principles Explanation

**Problem — sharing behaviour without copying:**

If every object needs its own copy of every method, memory scales with the number of instances:

```javascript
// Naive: each object gets its own copy of greet
const user1 = { name: 'Alice', greet: function() { ... } };
const user2 = { name: 'Bob',   greet: function() { ... } };
// 1000 users → 1000 copies of greet in memory
```

**Constraint — objects need identity (own properties) and shared behaviour:**

Name is per-instance. `greet` is shared. You need a way to separate these two concerns.

**Insight — property lookup via a linked chain:**

```
┌─────────────────────────────────────────────┐
│  PROTOTYPE CHAIN LOOKUP                     │
│                                             │
│  user1 object                               │
│  { name: 'Alice' }                          │
│       │ [[Prototype]]                       │
│       ↓                                     │
│  UserPrototype object                       │
│  { greet: function() {...} }    ← shared    │
│       │ [[Prototype]]                       │
│       ↓                                     │
│  Object.prototype                           │
│  { toString, hasOwnProperty, ... }          │
│       │ [[Prototype]]                       │
│       ↓                                     │
│       null  ← end of chain                  │
└─────────────────────────────────────────────┘

user1.greet → not on user1 → check UserPrototype
           → found → execute it
1000 users → one shared greet on UserPrototype
```

**The two distinct "prototype" concepts:**

```
[[Prototype]]  — every object's INTERNAL slot
                  points to its prototype object

.prototype     — property on FUNCTION OBJECTS
                  used when function is called with `new`
                  assigned as [[Prototype]] of new instance
```

This distinction trips up every JavaScript developer.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT the prototype chain:**

```
Without delegation-based inheritance:

  Problem 1: Method duplication per instance
    new User() → copies greet/save/validate
    1M users → 1M method copies on heap

  Problem 2: No structural type sharing
    Can't ask: "does this object behave like X?"
    → instanceof impossible
    → Duck typing requires manual checks

  Problem 3: No runtime extensibility
    Adding a method to all users requires
    iterating and adding to each object
    → Array.prototype.flatMap added in ES2019
      → available on ALL existing arrays instantly
```

**WITH the prototype chain:**

```
→ One method on prototype, shared by all instances
→ instanceof walks prototype chain to check lineage
→ Runtime extensibility: patch prototype once →
  affects all instances (with great power...)
→ Monkey-patching enables polyfills and shims
→ Object.create(proto) creates objects that inherit
  from any arbitrary object, not just classes
```

---

### 🧠 Mental Model / Analogy

> Think of the prototype chain as a **chain of managers** in a company. You (the object) have your own work items (own properties). If you can't answer a question, you escalate to your manager (`[[Prototype]]`). If they can't answer, they escalate to their manager. Eventually you reach the CEO (`Object.prototype`). If even the CEO doesn't know (`null`), the answer is `undefined`.

"You" = the object
"Your own work items" = own properties
"Escalating to manager" = `[[Prototype]]` lookup
"CEO" = `Object.prototype`
"No one answers" = `undefined` (property not found in chain)

Each manager handles the request *on behalf of* the original asker — so `this` inside a prototype method still refers to the original object that initiated the call.

---

### ⚙️ How It Works (Mechanism)

**Property lookup algorithm:**

```
GET obj.prop:

  1. Does obj have own property 'prop'?
     → Yes: return it
     → No: continue

  2. proto = Object.getPrototypeOf(obj)
     → If proto is null: return undefined
     → Else: repeat from step 1 with proto as obj
```

**Constructor function pattern:**

```javascript
function User(name) {
  this.name = name;             // own property on instance
}
User.prototype.greet = function() {
  return `Hi, I'm ${this.name}`;  // shared method
};

const u = new User('Alice');
// new does:
// 1. Create obj with [[Prototype]] = User.prototype
// 2. Call User with this = obj
// 3. Return obj

u.greet();   // found on User.prototype → "Hi, I'm Alice"
u.name;      // found on u itself → "Alice"
```

**Object.getPrototypeOf — reading the chain:**

```javascript
const arr = [1, 2, 3];
Object.getPrototypeOf(arr) === Array.prototype; // true
Object.getPrototypeOf(Array.prototype) === Object.prototype; // true
Object.getPrototypeOf(Object.prototype); // null

// Full chain for instance:
// arr → Array.prototype → Object.prototype → null
```

**Property shadowing:**

```javascript
const animal = { speak: () => 'generic sound' };
const dog = Object.create(animal);
dog.speak = () => 'woof'; // shadows animal.speak

dog.speak();    // 'woof' — own property found first
animal.speak(); // 'generic sound' — unaffected
```

---

### 🔄 How It Connects (Mini-Map)

```
Object literal {} / new Ctor() / Object.create()
        ↓
  Creates object with [[Prototype]] set
        ↓
  PROTOTYPE CHAIN  ← you are here
  (linked list of objects)
        ↓
  Property lookup walks chain
  (own → proto → proto.proto → ... → null)
        ↓
  ┌───────────────────────────────────────┐
  │  Built on top of this:                │
  │  Prototypal Inheritance               │
  │  Class (ES6+) — syntax sugar          │
  │  instanceof — chain membership check  │
  │  Object.create — explicit chain setup │
  └───────────────────────────────────────┘
        ↓
  Distinct from Scope Chain
  (scope chain → lexical environments,
   prototype chain → object properties)
```

---

### 💻 Code Example

**Example 1 — Manual prototype chain setup:**

```javascript
const vehicleProto = {
  start() { return `${this.model} started`; },
  stop()  { return `${this.model} stopped`; },
};

const car = Object.create(vehicleProto); // sets [[Proto]]
car.model = 'Toyota';
car.doors = 4;

car.start();  // "Toyota started" — found on vehicleProto
car.doors;    // 4 — found on car itself
car.toString(); // "[object Object]" — Object.prototype
```

**Example 2 — Constructor + prototype (pre-class pattern):**

```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() {
  return `${this.name} makes a noise.`;
};

function Dog(name) {
  Animal.call(this, name);  // inherit own properties
}
// Set up Dog.prototype to inherit from Animal.prototype
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;  // fix constructor ref

Dog.prototype.speak = function() {
  return `${this.name} barks.`;
};

const d = new Dog('Rex');
d.speak();  // "Rex barks." — own proto
d instanceof Dog;    // true
d instanceof Animal; // true — chain check
```

**Example 3 — Class syntax compiles to prototype chain:**

```javascript
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a noise.`; }
}

class Dog extends Animal {
  speak() { return `${this.name} barks.`; }
}

// Equivalent prototype structure:
// Dog.prototype.__proto__ === Animal.prototype
// d.__proto__ === Dog.prototype

const d = new Dog('Rex');
Object.getPrototypeOf(d) === Dog.prototype;            // true
Object.getPrototypeOf(Dog.prototype) === Animal.prototype; // true
```

**Example 4 — Performance: avoid prototype chain lookups in hot paths:**

```javascript
// BAD: repeated prototype chain lookup in loop
for (let i = 0; i < 1_000_000; i++) {
  arr.push(Math.random()); // push resolved via chain each time
}

// GOOD: cache prototype method if profiler shows it hot
const push = Array.prototype.push.bind(arr);
for (let i = 0; i < 1_000_000; i++) {
  push(Math.random()); // direct call, no chain walk
}
// V8 usually inlines this anyway — profile first
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `__proto__` and `.prototype` are the same | `__proto__` is an object's own [[Prototype]] link; `.prototype` is a property on constructor functions used to set up `[[Prototype]]` of new instances — completely different |
| ES6 classes replace the prototype chain | class is syntactic sugar; the prototype chain is still the underlying mechanism. `typeof Dog` is still `'function'` |
| Modifying `Object.prototype` only affects one object | It affects ALL objects in the runtime — every plain object inherits from it. Modifying it breaks for-in loops and other code unless very carefully guarded |
| Properties on the prototype are "inherited" as copies | They are shared references. All instances see the same prototype object. Mutating a prototype property affects all instances simultaneously |
| instanceof checks if an object is a direct instance | instanceof walks the entire prototype chain — `[] instanceof Object` is true even though Array is Array, not Object |
| Prototype chains are slow | V8 uses hidden classes (Shapes) to cache property offsets. Well-structured prototype chains are blazingly fast — as fast as compiled struct access |

---

### 🔥 Pitfalls in Production

**1. Mutating Object.prototype (prototype pollution attack)**

```javascript
// BAD: dangerous library code that mutates Object.prototype
Object.prototype.isAdmin = true;
// Every plain object now has isAdmin = true
const user = JSON.parse(userInput);
if (user.isAdmin) {
  // ALWAYS true — prototype pollution attack!
  grantAdminAccess();
}

// ATTACK vector: JSON input like:
// { "__proto__": { "isAdmin": true } }
// Older versions of lodash merge() were vulnerable

// GOOD: always use Object.create(null) for
// property-bag objects, or check hasOwnProperty
if (Object.prototype.hasOwnProperty.call(user, 'isAdmin')
    && user.isAdmin === true) {
  grantAdminAccess();
}
```

**2. Accidentally sharing mutable state on prototype**

```javascript
// BAD: array on prototype shared across ALL instances
function Team() {}
Team.prototype.members = []; // SHARED mutable array!

const t1 = new Team();
const t2 = new Team();
t1.members.push('Alice');
console.log(t2.members); // ['Alice'] — shared!

// GOOD: initialise mutable state in constructor
function Team() {
  this.members = []; // own property per instance
}
```

**3. Deep prototype chain degrading lookup performance**

```javascript
// BAD: excessive chain depth
class A {}
class B extends A {}
class C extends B {}
class D extends C {}
class E extends D {}
// 5+ levels deep — each property lookup
// walks further if not found early

// GOOD: flatten hierarchies — prefer composition
class E {
  constructor() {
    this.a = new A(); // composition, not inheritance
  }
}
// Or use mixins to share behaviour without deep chains
```

---

### 🔗 Related Keywords

- `Prototypal Inheritance` — the pattern of inheriting behaviour by setting up prototype chains
- `Object.create` — creates an object with a specified prototype, the cleanest way to set up prototype delegation
- `Class (ES6+)` — syntactic sugar over the constructor + prototype pattern
- `instanceof` — checks if an object's prototype chain includes a specific constructor's prototype
- `hasOwnProperty` — checks if a property exists on the object itself, not on the prototype chain
- `Object.prototype` — the root of all ordinary object prototype chains; source of toString, valueOf, etc.
- `Lexical Environment` — the parallel lookup chain for variables; completely separate from prototype chain

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Property lookup delegates up a linked list│
│              │ of object prototypes until found or null  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sharing methods across instances, setting │
│              │ up inheritance, understanding class sugar  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never mutate Object.prototype; avoid deep │
│              │ chains (> 4 levels) for perf-critical code│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't copy behaviour — delegate to       │
│              │  whoever already has it."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Prototypal Inheritance → Class → Object   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The prototype pollution vulnerability exploits the fact that `JSON.parse('{"__proto__":{"isAdmin":true}}')` does NOT pollute `Object.prototype` in modern engines, but `Object.assign({}, parsed)` previously did on some platforms. Trace exactly why: what does `JSON.parse` produce (hint: a plain object, not a chain manipulation), what does `Object.assign` do with a key named `__proto__`, and what V8 change closed this specific vector? Then explain why `structuredClone` is safe and why `lodash.merge` at certain versions was not.

**Q2.** V8's hidden class (Shape) mechanism caches the memory layout of objects with the same prototype chain and property insertion order. Explain what happens to V8's Shape-based optimisation when: (a) you add properties to an object in different orders across different code paths, and (b) you add a property to a prototype after instances have already been created and used in optimised code. What specific deoptimisation does V8 trigger in each case, and how would you detect it in production using `--trace-deopt`?

