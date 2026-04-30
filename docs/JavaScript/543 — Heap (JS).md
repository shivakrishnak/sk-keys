---
layout: default
title: "Heap (JS)"
parent: "JavaScript"
nav_order: 543
permalink: /javascript/heap-js/
number: "543"
category: JavaScript
difficulty: ★☆☆
depends_on: JavaScript Engine (V8)
used_by: Garbage Collection (JS), Memory Leaks (JS), WeakMap, WeakSet, Closure
tags: #javascript, #memory, #internals, #browser, #nodejs, #foundational
---

# 543 — Heap (JS)

`#javascript` `#memory` `#internals` `#browser` `#nodejs` `#foundational`

⚡ TL;DR — The unstructured memory region where JavaScript allocates all objects, arrays, closures, and strings at runtime.

| #543 | Category: JavaScript | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | JavaScript Engine (V8) | |
| **Used by:** | Garbage Collection (JS), Memory Leaks (JS), WeakMap, WeakSet, Closure | |

---

### 📘 Textbook Definition

The **Heap** in a JavaScript runtime is a large, dynamically-sized region of memory used for the allocation of all reference types — objects, arrays, functions, closures, and strings. Unlike the call stack, which allocates and deallocates memory in strict LIFO order, the heap has no inherent order; memory can be allocated and freed at arbitrary addresses. The JavaScript engine's garbage collector is responsible for identifying and reclaiming heap memory that is no longer reachable from any GC root. In V8, the heap is divided into several spaces: New Space (Young Generation), Old Space (Old Generation), Large Object Space, Code Space, and Map Space.

---

### 🟢 Simple Definition (Easy)

The heap is JavaScript's storage warehouse. Every object, array, and function you create gets stored there. Unlike the call stack (which is neat and orderly), the heap is a big, flexible space that can grow as needed.

---

### 🔵 Simple Definition (Elaborated)

When you write `const user = { name: 'Alice' }`, the `user` object isn't stored in the call stack — it's allocated in the heap. The stack only holds a small reference (pointer) to where that object lives in the heap. The heap is unstructured: objects can be allocated and freed at any location. Because the heap can grow very large and its contents aren't automatically cleaned up when functions return, the engine needs a garbage collector to periodically scan the heap and free memory for objects that nothing references anymore.

---

### 🔩 First Principles Explanation

**Problem — stack can't hold everything:**

The call stack is fast but limited. Its size is fixed (~1–8 MB). It only holds data for the currently active function, and all data is destroyed when the function returns.

```
// Stack can hold primitives and references:
function fn() {
  const x = 42;       // ← stored on stack (number)
  const s = "hello";  // ← reference on stack,
                       //   string data on heap
  const obj = {};     // ← reference on stack,
                       //   object on heap
}
// When fn() returns, x is gone instantly.
// But obj may still be referenced elsewhere —
// it must outlive this function call.
```

**Constraint — objects have unknown, dynamic lifetimes:**

Objects might need to live longer than the function that created them — closures capture them, arrays are passed around, DOM event listeners hold references. Static stack allocation can't handle this.

**Insight — separate lifetimes from execution frames:**

```
┌─────────────────────────────────────────────┐
│  MEMORY DIVISION                            │
│                                             │
│  STACK           HEAP                       │
│  ─────────       ──────────────────────     │
│  fast, small     large, flexible            │
│  auto-freed      GC-managed                 │
│  primitives      objects, arrays,           │
│  + references    functions, strings         │
│                                             │
│  stack var ──pointer──→ heap object         │
└─────────────────────────────────────────────┘
```

**Solution — heap allocation with GC:**

Allocate all objects on the heap. Track which heap objects are reachable. When an object has no more references pointing to it, the garbage collector reclaims that memory.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT a heap:**

```
Without dynamic heap allocation:

  Problem 1: Objects can't outlive their creator
    function makeUser() {
      return { name: 'Alice' };  // ← where does this go?
      // if stack-only: destroyed when makeUser() returns
      // caller receives garbage
    }

  Problem 2: Variable-size data impossible
    const arr = new Array(userInput);
    // can't put variable-size data on fixed stack

  Problem 3: Sharing data between call sites
    callbacks, closures, event handlers
    all need to reference the SAME object instance
    → impossible without a shared memory region
```

**WITH the Heap:**

```
→ Objects persist beyond their creating function
→ Closures work — lexical vars stay alive
  as long as any closure references them
→ Arrays and strings can be any size
→ Multiple references to the same object work
  (pass-by-reference semantics)
```

---

### 🧠 Mental Model / Analogy

> Think of the heap as a **city's storage facilities** — warehouses of varying sizes scattered around. The call stack is like your desk — small, orderly, fast to use. When you need something big or long-term, you rent warehouse space (allocate on heap) and keep a tag (reference/pointer) on your desk. When you no longer need the warehouse, you should return it. The garbage collector is the city inspector who periodically walks around and reclaims any warehouse that nobody holds a tag to anymore.

"Warehouse" = heap-allocated object
"Tag on your desk" = stack variable (reference/pointer)
"City inspector" = garbage collector
"Warehouse nobody holds a tag to" = unreachable object, eligible for collection

---

### ⚙️ How It Works (Mechanism)

**V8 heap layout:**

```
┌──────────────────────────────────────────────┐
│  V8 HEAP SPACES                              │
├──────────────────────────────────────────────┤
│  New Space (Young Generation)                │
│  ├── From-Space  (active allocations)        │
│  └── To-Space    (used during minor GC)      │
│  Small, recently-created objects live here   │
│  Minor GC (Scavenge) runs frequently         │
├──────────────────────────────────────────────┤
│  Old Space (Old Generation)                  │
│  Objects surviving 2 minor GCs promoted here │
│  Major GC (Mark-Sweep-Compact) runs here     │
├──────────────────────────────────────────────┤
│  Large Object Space                          │
│  Objects > 512KB — never moved by GC         │
├──────────────────────────────────────────────┤
│  Code Space                                  │
│  JIT-compiled machine code                   │
├──────────────────────────────────────────────┤
│  Map Space                                   │
│  Hidden classes (V8 object shape descriptors)│
└──────────────────────────────────────────────┘
```

**Allocating on the heap:**

Every `new Object()`, `{}`, `[]`, function expression, and string literal triggers a heap allocation. V8 uses a bump-pointer allocator in New Space (extremely fast — just increment a pointer). When New Space fills up, a minor GC runs.

**Inspecting heap usage:**

```javascript
// Node.js — snapshot heap usage
const v8 = require('v8');
const stats = v8.getHeapStatistics();
console.log(stats);
// {
//   heap_size_limit: 2197815296,    // ~2GB
//   total_heap_size: 8200192,
//   used_heap_size: 5850144,
//   ...
// }
```

---

### 🔄 How It Connects (Mini-Map)

```
JavaScript Engine (V8)
        ↓
  ┌─────────────┐    ┌───────────────────────┐
  │ Call Stack  │    │   HEAP  ← you are here│
  │ (references)│───→│   (actual objects)    │
  └─────────────┘    └───────────┬───────────┘
                                 │
               ┌─────────────────┼──────────────┐
               ↓                 ↓              ↓
         GC Roots          Garbage           Closures
         (reachable)       Collector         (capture
                           (reclaims         heap refs)
                           unreachable)
               ↓
         Memory Leaks
         (unintentional
          heap retention)
```

---

### 💻 Code Example

**Example 1 — Primitives on stack vs objects on heap:**

```javascript
// Primitives — value copied (conceptually on stack)
let a = 42;
let b = a;
b = 99;
console.log(a); // 42 — a unchanged

// Objects — reference copied (both point to heap object)
const obj1 = { x: 1 };
const obj2 = obj1;    // both point to SAME heap object
obj2.x = 99;
console.log(obj1.x);  // 99 — same object modified
```

**Example 2 — Monitoring heap in production (Node.js):**

```javascript
// Log heap usage every 10 seconds
setInterval(() => {
  const mem = process.memoryUsage();
  console.log({
    heapUsed:  (mem.heapUsed  / 1024 / 1024).toFixed(1) + 'MB',
    heapTotal: (mem.heapTotal / 1024 / 1024).toFixed(1) + 'MB',
    rss:       (mem.rss       / 1024 / 1024).toFixed(1) + 'MB',
  });
}, 10_000);
// heapUsed steadily climbing → likely memory leak
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strings are primitives so they're on the stack | String content is allocated on the heap; the stack holds a reference. Only small integer-like values may be inlined |
| Memory is freed immediately when a variable goes out of scope | The GC runs on its own schedule; heap memory is freed when the GC determines the object is unreachable, not when the reference is dropped |
| The heap is slow compared to the stack | New Space allocation uses bump-pointer and is extremely fast; the cost is in GC pauses, not the allocation itself |
| You can control exactly when GC runs | `global.gc()` forces a GC in Node.js with `--expose-gc`, but in production you cannot force or precisely time GC |

---

### 🔥 Pitfalls in Production

**1. Closures retaining large heap objects unintentionally**

```javascript
// BAD: event listener closure captures a 10MB object
function setup() {
  const largeData = loadTenMBDataset(); // on heap
  document.addEventListener('click', () => {
    console.log(largeData.metadata); // captures all of it
    // largeData can NEVER be GC'd while listener exists
  });
}

// GOOD: extract only what you need before the closure
function setup() {
  const largeData = loadTenMBDataset();
  const metadata = largeData.metadata; // extract needed piece
  // largeData can now be GC'd
  document.addEventListener('click', () => {
    console.log(metadata);  // only 10 bytes retained
  });
}
```

**2. Heap OOM in Node.js from unbounded caches**

```javascript
// BAD: in-process cache with no eviction
const cache = {};
app.get('/item/:id', async (req, res) => {
  if (!cache[req.params.id]) {
    cache[req.params.id] = await db.query(req.params.id);
  }
  res.json(cache[req.params.id]);
});
// With 1M unique IDs → heap grows until OOM crash

// GOOD: use LRU cache with size limit
const LRU = require('lru-cache');
const cache = new LRU({ max: 10_000 }); // max 10k entries
```

---

### 🔗 Related Keywords

- `JavaScript Engine (V8)` — allocates and manages the heap during execution
- `Call Stack` — holds references that point into the heap; stack stores where the objects are
- `Garbage Collection (JS)` — reclaims unreachable heap memory on a scheduled basis
- `Memory Leaks (JS)` — occur when heap objects remain reachable but are no longer needed
- `Closure` — captures references to heap-allocated variables, extending their lifetime
- `WeakMap / WeakSet` — hold weak references to heap objects, allowing GC despite the reference
- `New Space / Young Generation` — the fast-allocation area within the V8 heap for new objects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ All objects live here; stack holds only   │
│              │ primitives + references into the heap     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing memory growth, OOM crashes,    │
│              │ GC pressure, closure memory leaks         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — automatic; but avoid holding large  │
│              │ objects longer than necessary             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The stack knows where you are;           │
│              │  the heap remembers what you made."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Garbage Collection → Memory Leaks →       │
│              │ WeakMap / WeakSet                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Node.js service processes HTTP requests and caches parsed request bodies in a `Map`. After running for 6 hours, heap memory has grown from 50MB to 1.2GB and the process is OOM-killed. Using your knowledge of the heap and garbage collection, trace exactly why this Map prevents GC from reclaiming those objects — and why switching to a `WeakMap` would or would not solve the problem in this specific case.

**Q2.** V8's New Space uses a semi-space copying collector: live objects from the active "From-Space" are copied to "To-Space" on each minor GC. This means allocating many short-lived objects per request is actually efficient. Explain why this is counterintuitive, what the cost actually is, and at what point this strategy breaks down and promotes objects into Old Space — where GC is much more expensive.

