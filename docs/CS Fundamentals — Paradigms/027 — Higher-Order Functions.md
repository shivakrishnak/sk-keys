---
layout: default
title: "Higher-Order Functions"
parent: "CS Fundamentals — Paradigms"
nav_order: 27
permalink: /cs-fundamentals/higher-order-functions/
number: "027"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: First-Class Functions, Functional Programming, Lambda Calculus
used_by: Functional Programming, Stream API, Reactive Programming, JavaScript
tags: #intermediate, #functional, #pattern, #algorithm
---

# 027 — Higher-Order Functions

`#intermediate` `#functional` `#pattern` `#algorithm`

⚡ TL;DR — A higher-order function either takes one or more functions as arguments, or returns a function as its result — enabling reusable, composable abstractions over behaviour.

| #027            | Category: CS Fundamentals — Paradigms                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | First-Class Functions, Functional Programming, Lambda Calculus       |                 |
| **Used by:**    | Functional Programming, Stream API, Reactive Programming, JavaScript |                 |

---

### 📘 Textbook Definition

A **higher-order function** (HOF) is a function that satisfies at least one of two conditions: it accepts one or more functions as arguments, or it returns a function as its result. The term was introduced in formal logic and adopted by computer science from lambda calculus, where applying a function to another function is the norm. Higher-order functions are the mechanism by which behaviour is abstracted and composed in functional programming: `map` applies a transformation function to every element of a collection, `filter` selects elements by a predicate function, and `reduce` (fold) aggregates elements using a combining function. In Java, HOFs are expressed via functional interfaces; in JavaScript and Python they are a natural language feature. HOFs are the primary tool for eliminating duplicated control flow by extracting the varying behaviour as a function parameter.

---

### 🟢 Simple Definition (Easy)

A higher-order function is a function that works with other functions — it either accepts a function as an input or produces a function as output.

---

### 🔵 Simple Definition (Elaborated)

When you call `list.stream().map(x -> x * 2)`, the `map` function takes your transformation function (`x -> x * 2`) as an argument and applies it to every element. That makes `map` a higher-order function — its argument is a function, not a simple value. Similarly, `filter`, `forEach`, `reduce`, `flatMap`, `sorted`, and `Comparator.comparing` are all higher-order functions. On the "returns a function" side: `Comparator.comparing(Person::getName).thenComparing(Person::getAge)` returns a new comparator function by composing two function arguments. Higher-order functions are the reason modern Java can express a complex multi-step data pipeline in a single readable chain, and why JavaScript's `Array.prototype.map`, `filter`, and `reduce` eliminate most manual loops.

---

### 🔩 First Principles Explanation

**The problem: duplicated control flow with varying logic.**

Consider: filter a list of orders by status, filter by customer, filter by amount. Without HOFs:

```java
// WITHOUT HOFs: copy-paste the loop structure for every variation
List<Order> filterByStatus(List<Order> orders, String status) {
    List<Order> result = new ArrayList<>();
    for (Order o : orders) {               // ← same structure
        if (o.getStatus().equals(status)) result.add(o); // varies
    }
    return result;
}

List<Order> filterByCustomer(List<Order> orders, String customer) {
    List<Order> result = new ArrayList<>();
    for (Order o : orders) {               // ← same structure
        if (o.getCustomer().equals(customer)) result.add(o); // varies
    }
    return result;
}
// Three filter methods = three copies of the same loop
```

**The HOF solution — parameterise the varying behaviour:**

```java
// WITH HOFs: one method, the PREDICATE is the parameter
List<Order> filter(List<Order> orders, Predicate<Order> condition) {
    List<Order> result = new ArrayList<>();
    for (Order o : orders) {
        if (condition.test(o)) result.add(o); // behaviour is injected
    }
    return result;
}

// Call sites — the varying logic is a one-liner
filter(orders, o -> o.getStatus().equals("PLACED"));
filter(orders, o -> o.getCustomer().equals("ACME"));
filter(orders, o -> o.getAmount() > 1000.0);
```

The loop runs once. The varying predicate is a first-class function argument. This is the essence of higher-order functions: extract the structure, parameterise the behaviour.

**The three canonical HOFs:**

```
map(collection, f)     → new collection where each element is f(element)
filter(collection, p)  → new collection with only elements where p(element) is true
reduce(collection, f, init) → single value from folding f over all elements
```

These three functions can express any transformation on a collection, replacing virtually all manual loops.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Higher-Order Functions:

What breaks without it:

1. Algorithm reuse requires copying loop structures — any variation in logic forces code duplication.
2. Collections pipelines (`map → filter → reduce`) require intermediate variables and manual iteration.
3. Callbacks, event handlers, and middleware require dedicated interface types for every use case.
4. Composing behaviours (logging + timing + retry) requires inheritance hierarchies or manual wiring.

WITH Higher-Order Functions:
→ `map`, `filter`, `reduce` express any collection transformation without manual loops.
→ Retry logic, circuit breakers, and decorators are functions that wrap other functions.
→ Middleware chains compose by passing each handler function to the next wrapper.
→ Test doubles (mocks) are functions injected as arguments — no framework needed for simple cases.

---

### 🧠 Mental Model / Analogy

> Think of a factory assembly line that has variable stations. A fixed HOF is the conveyor belt — it moves every item through the line. The function argument is the robot arm at each station. You don't rebuild the belt to change what the robot does — you swap out the robot arm. `map` is the belt; the transformation function is the arm. The belt never changes; the arm is injected.

"The assembly line conveyor belt" = the HOF structure (`map`, `filter`, `reduce`)
"The robot arm at a station" = the function argument (the varying behaviour)
"Swapping the robot arm" = passing a different function to the same HOF
"Building a new factory for each product" = copying the loop for each variation

---

### ⚙️ How It Works (Mechanism)

**The three canonical HOFs visualised:**

```
┌──────────────────────────────────────────────┐
│  map(f): transform every element             │
│                                              │
│  [1, 2, 3, 4]  →map(x→x²)→  [1, 4, 9, 16]  │
│                                              │
│  filter(p): keep matching elements           │
│                                              │
│  [1,2,3,4] →filter(x>2)→ [3, 4]             │
│                                              │
│  reduce(f, init): fold to single value       │
│                                              │
│  [1,2,3,4] →reduce(+, 0)→ 10               │
│   init=0: 0+1=1, 1+2=3, 3+3=6, 6+4=10      │
└──────────────────────────────────────────────┘
```

**Function returning a function — currying and partial application:**

```java
// Currying: transform f(a, b) into a -> b -> f(a, b)
// The outer function RETURNS a function

// Method returning a Comparator (a function)
Comparator<Person> byName = Comparator.comparing(Person::getName);
// Comparator.comparing IS a HOF: takes a key-extractor function,
// RETURNS a Comparator function.

// Explicit: function returning function
Function<String, Predicate<String>> startsWith =
    prefix -> s -> s.startsWith(prefix); // returns a Predicate

Predicate<String> startsWithHttp  = startsWith.apply("http");
Predicate<String> startsWithHttps = startsWith.apply("https");
```

**Function composition:**

```java
// compose: g(f(x)) — apply f first, then g
Function<Integer, Integer> doubleIt   = x -> x * 2;
Function<Integer, Integer> addTen     = x -> x + 10;

Function<Integer, Integer> doubleThenAdd = doubleIt.andThen(addTen);
doubleThenAdd.apply(5); // (5*2)+10 = 20

Function<Integer, Integer> addThenDouble = doubleIt.compose(addTen);
addThenDouble.apply(5); // (5+10)*2 = 30
```

---

### 🔄 How It Connects (Mini-Map)

```
First-Class Functions
(prerequisite: functions must be values)
        │
        ▼
Higher-Order Functions  ◄──── (you are here)
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
Java Stream API                         Function Composition
(map, filter, reduce, flatMap)          (andThen, compose, chain)
        │                                          │
        ▼                                          ▼
Reactive Programming                    Middleware / Decorator
(Rx operators are all HOFs)             (wrap a fn with another fn)
```

---

### 💻 Code Example

**Example 1 — map / filter / reduce pipeline:**

```java
List<Order> orders = getOrders();

// Without HOFs: 15 lines of loops
// With HOFs: one pipeline
double totalRevenue = orders.stream()
    .filter(o -> o.getStatus() == Status.COMPLETED)  // HOF: filter
    .map(Order::getAmount)                            // HOF: map
    .reduce(0.0, Double::sum);                        // HOF: reduce
// Reads as English: "sum amounts of completed orders"
```

**Example 2 — Decorator HOF (wrapping a function with retry logic):**

```java
// A HOF that wraps any Supplier<T> with retry logic
<T> Supplier<T> withRetry(Supplier<T> action, int maxAttempts) {
    return () -> {                                   // returns a function
        for (int i = 0; i < maxAttempts; i++) {
            try {
                return action.get();                 // call the wrapped fn
            } catch (Exception e) {
                if (i == maxAttempts - 1) throw e;
            }
        }
        throw new IllegalStateException("unreachable");
    };
}

// Apply the HOF — wrap any operation with retry:
Supplier<String> fetchConfig = withRetry(
    () -> remoteConfig.fetch("db.url"), 3
);
String url = fetchConfig.get(); // retries up to 3 times on failure
```

**Example 3 — Comparator composition (HOF returning HOF):**

```java
List<Employee> employees = getEmployees();

// Comparator.comparing is a HOF: takes a key-extractor function,
// returns a Comparator function.
// thenComparing chains HOFs.
employees.sort(
    Comparator.comparing(Employee::getDepartment)  // HOF call 1
              .thenComparing(Employee::getSalary,  // HOF call 2
                             Comparator.reverseOrder())
);
// Sort by department, then by salary descending — no custom class needed
```

**Example 4 — flatMap (HOF for nested collections):**

```java
List<Order> orders = getOrders();

// Each order has multiple line items — flatMap flattens nested lists
List<Product> allProducts = orders.stream()
    .flatMap(order -> order.getLineItems().stream()) // HOF: fn returning Stream
    .map(LineItem::getProduct)                        // HOF: map
    .distinct()
    .collect(Collectors.toList());
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                             |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HOFs are only useful for collections                         | HOFs appear in retry decorators, middleware pipelines, event system composition, async callback chaining, and dependency injection of behaviour — not just `map`/`filter`/`reduce`                                  |
| Using HOFs always allocates more objects                     | Non-capturing lambdas in Java are cached; method references are stable. A well-written HOF pipeline often allocates less than a manual loop with intermediate `ArrayList` results                                   |
| `reduce` is the same as `forEach` with a mutable accumulator | `reduce` is a pure fold that produces a new value; `forEach` is inherently side-effectful. Using `forEach` to accumulate into a mutable list violates functional semantics and is thread-unsafe in parallel streams |
| HOFs and recursion are equivalent alternatives               | HOFs operate on collections using internal iteration; recursion operates on self-similar structures. `map` on a list and a recursive tree traversal address different problem shapes                                |

---

### 🔥 Pitfalls in Production

**Stateful lambda in parallel stream — race condition**

```java
// BAD: lambda captures and mutates a shared list in a parallel stream
List<String> results = new ArrayList<>(); // NOT thread-safe
orders.parallelStream()
      .map(Order::getId)
      .forEach(results::add); // race condition: ArrayList is not thread-safe
// Intermittent data corruption / lost entries under load

// GOOD: use a thread-safe collector
List<String> results = orders.parallelStream()
    .map(Order::getId)
    .collect(Collectors.toList()); // collect is thread-safe in parallel
```

---

**Using `reduce` with an identity value that breaks associativity**

```java
// BAD: non-associative identity in parallel reduce
// String concatenation is NOT associative for parallel reduce identity
String result = Stream.of("a", "b", "c")
    .parallel()
    .reduce("PREFIX-",                         // identity applied per thread!
            String::concat);
// May produce: "PREFIX-aPREFIX-bPREFIX-c" because identity
// is applied to each partition, not just once

// GOOD: use collect for string joining; only use identity "" for concat
String correct = Stream.of("a", "b", "c")
    .collect(Collectors.joining(", ")); // thread-safe, correct
```

---

**Infinite stream without a terminal short-circuit — hangs production**

```java
// BAD: generating an infinite stream and calling a terminal op without limit
Stream.iterate(0, n -> n + 1)
      .filter(n -> n % 2 == 0)
      .map(n -> n * n)
      .collect(Collectors.toList()); // hangs forever — no terminal limit

// GOOD: always add limit() or findFirst() on infinite streams
List<Integer> first10EvenSquares = Stream.iterate(0, n -> n + 1)
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .limit(10)        // bound the infinite stream
    .collect(Collectors.toList());
```

---

### 🔗 Related Keywords

- `First-Class Functions` — the prerequisite: functions must be values before they can be passed or returned
- `Functional Programming` — the paradigm that places HOFs at the centre of program design
- `Java Stream API` — Java's standard HOF collection pipeline (`map`, `filter`, `reduce`, `flatMap`)
- `Closures` — HOFs that capture scope produce closures; critical for understanding what state is captured
- `Side Effects` — pure HOFs avoid them; HOFs with side effects break composability
- `Referential Transparency` — functions passed to HOFs should be referentially transparent for predictable behaviour
- `Reactive Programming` — RxJava/Project Reactor operators (`map`, `flatMap`, `filter`) are HOFs on streams of events
- `Currying` — the technique of transforming multi-argument functions into chains of single-argument HOFs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Functions that take or return functions —  │
│              │ parameterise behaviour, not just data      │
├──────────────┼───────────────────────────────────────────┤
│ BIG THREE    │ map (transform), filter (select),          │
│              │ reduce (fold/aggregate)                    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Lambda captures mutable shared state;      │
│              │ parallel stream with stateful HOF body     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Extract the loop; inject the logic."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Side Effects → Referential Transparency → │
│              │ Functional Programming → Stream API        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates a pricing engine from manual loops to a Stream API pipeline: `products.stream().filter(...).map(...).reduce(0.0, Double::sum)`. In production, they observe that under heavy load the pipeline takes 3× longer than the original loop. Profiling shows excessive GC pressure. Identify at least three distinct sources of object allocation introduced by the Stream API pipeline that are absent in a manual loop, describe how each contributes to GC pressure, and explain the specific conditions under which switching to `parallelStream()` would make GC pressure worse rather than better.

**Q2.** `flatMap` is described as "mapping and then flattening." In a reactive system using Project Reactor, `flatMap` is non-sequential: it subscribes to inner publishers concurrently, interleaving results. `concatMap` is sequential: it subscribes to each inner publisher only after the previous one completes. Given a service that makes HTTP calls for each element in a stream, describe the exact scenario where `flatMap` causes a downstream service to receive out-of-order requests it cannot handle, and explain how `concatMap` fixes it — including the trade-off in throughput between the two operators.
