---
layout: default
title: "Stack Frame"
parent: "Java Fundamentals"
nav_order: 9
permalink: /java/stack-frame/
---
ðŸ·ï¸ Tags â€” #java #jvm #memory #internals #deep-dive

âš¡ TL;DR â€” The per-method execution unit pushed onto the thread stack, containing everything a method needs to run: local variables, working memory, and return context. 

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #009  â”‚ Category: JVM Memory     â”‚ Difficulty: â˜…â˜…â˜…   â”‚
â”‚ Depends on: Stack Memory, JVM,   â”‚ Used by: Every    â”‚
â”‚ Bytecode, Thread                 â”‚ method invocation â”‚
â”‚                                  â”‚ JIT, Debugger     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ“˜ Textbook Definition

A Stack Frame is a **data structure created on the thread stack for each method invocation**, containing three components: the **Local Variable Table** (stores parameters and local vars), the **Operand Stack** (working memory for bytecode execution), and **Frame Data** (return address, reference to runtime constant pool, exception table). It is pushed on method entry and popped on method exit or exception propagation.

---

#### ðŸŸ¢ Simple Definition (Easy)

A stack frame is **one method's private workspace** â€” everything that method needs to execute, allocated when called, destroyed when it returns.

---

#### ðŸ”µ Simple Definition (Elaborated)

Every time a method is called, the JVM creates a stack frame and pushes it onto the thread's stack. That frame holds the method's parameters, any local variables it declares, a working scratch pad for calculations (operand stack), and the address to return to when done. The method executes entirely within this frame. When it returns â€” or throws an uncaught exception â€” the frame is popped, and the calling method's frame becomes active again with execution resuming exactly where it left off.

---

#### ðŸ”© First Principles Explanation

**The problem:**

The JVM needs to execute thousands of method calls, each with its own variables, calculations, and return points â€” all independently, without interference.

java

```java
int a() { int x = 1; return b() + x; }
int b() { int x = 2; return c() + x; }
int c() { int x = 3; return x; }
```

Three methods â€” each with their own `x`. They must not interfere. `b()` must know to return to `a()`, not somewhere else. `a()`'s `x=1` must survive while `b()` and `c()` run.

**The insight:**

> Each method invocation needs a completely isolated, self-contained execution context. Stack frames ARE that isolation.

```
a() calls b() calls c():

STACK (top = active):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ c(): x=3            â”‚ â† executing now
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ b(): x=2            â”‚ â† frozen, waiting for c()
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ a(): x=1            â”‚ â† frozen, waiting for b()
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

c() returns 3:
  â†’ c()'s frame popped
  â†’ b()'s frame active: 3 + x(=2) = 5

b() returns 5:
  â†’ b()'s frame popped
  â†’ a()'s frame active: 5 + x(=1) = 6
```

Each `x` is completely isolated. Return addresses are baked into each frame.

---

#### ðŸ§  Mental Model / Analogy

> Think of the thread stack as a **desk with stacking paper trays**.
> 
> Each method call = placing a new tray on top with a fresh worksheet inside. The worksheet has three sections:
> 
> - **Left column** (Local Variable Table): named slots â€” `x=1`, `order=<ref>`
> - **Center** (Operand Stack): scratch area for mid-calculation values
> - **Bottom** (Frame Data): "when done, return to line 42 of the caller"
> 
> You only ever work on the **top tray**. All trays below are set aside, untouched, until you return to them. Remove the top tray (method returns) â†’ the tray below is exactly as you left it.

---

#### âš™ï¸ Stack Frame â€” Full Anatomy

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      STACK FRAME                           â”‚
â”‚                   (one per method call)                    â”‚
â”‚                                                            â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚              LOCAL VARIABLE TABLE                    â”‚  â”‚
â”‚  â”‚                                                      â”‚  â”‚
â”‚  â”‚  Slot â”‚ Content                    â”‚ Type            â”‚  â”‚
â”‚  â”‚  â”€â”€â”€â”€ â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€     â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚  â”‚
â”‚  â”‚   0   â”‚ this (instance methods)    â”‚ reference       â”‚  â”‚
â”‚  â”‚   1   â”‚ first parameter            â”‚ int/ref/etc     â”‚  â”‚
â”‚  â”‚   2   â”‚ second parameter           â”‚ int/ref/etc     â”‚  â”‚
â”‚  â”‚   3   â”‚ first local variable       â”‚ int/ref/etc     â”‚  â”‚
â”‚  â”‚   4   â”‚ second local variable      â”‚ int/ref/etc     â”‚  â”‚
â”‚  â”‚  ...  â”‚ ...                        â”‚ ...             â”‚  â”‚
â”‚  â”‚                                    â”‚                 â”‚  â”‚
â”‚  â”‚  Notes:                                              â”‚  â”‚
â”‚  â”‚  â€¢ long/double occupy TWO slots                      â”‚  â”‚
â”‚  â”‚  â€¢ static methods: no slot 0 (no 'this')            â”‚  â”‚
â”‚  â”‚  â€¢ references store heap address, not object         â”‚  â”‚
â”‚  â”‚  â€¢ size fixed at compile time (javac calculates)     â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                            â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚                 OPERAND STACK                        â”‚  â”‚
â”‚  â”‚                                                      â”‚  â”‚
â”‚  â”‚  â€¢ LIFO stack for intermediate calculations          â”‚  â”‚
â”‚  â”‚  â€¢ Bytecode instructions push/pop values here        â”‚  â”‚
â”‚  â”‚  â€¢ Max depth fixed at compile time                   â”‚  â”‚
â”‚  â”‚  â€¢ Empty at start of method                          â”‚  â”‚
â”‚  â”‚  â€¢ Must be empty before method returns               â”‚  â”‚
â”‚  â”‚                                                      â”‚  â”‚
â”‚  â”‚  Example: computing (a + b) * c                      â”‚  â”‚
â”‚  â”‚  iload_1  â†’ [a]                                      â”‚  â”‚
â”‚  â”‚  iload_2  â†’ [a, b]                                   â”‚  â”‚
â”‚  â”‚  iadd     â†’ [a+b]                                    â”‚  â”‚
â”‚  â”‚  iload_3  â†’ [a+b, c]                                 â”‚  â”‚
â”‚  â”‚  imul     â†’ [(a+b)*c]                                â”‚  â”‚
â”‚  â”‚  ireturn  â†’ []  (value returned to caller's stack)   â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                            â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚                   FRAME DATA                         â”‚  â”‚
â”‚  â”‚                                                      â”‚  â”‚
â”‚  â”‚  â€¢ Return address: PC of next instruction in caller  â”‚  â”‚
â”‚  â”‚  â€¢ Constant Pool reference: for symbolic resolution  â”‚  â”‚
â”‚  â”‚  â€¢ Exception table: maps bytecode ranges to          â”‚  â”‚
â”‚  â”‚    catch handlers â€” used when exception thrown       â”‚  â”‚
â”‚  â”‚  â€¢ Method reference: which method this frame is for  â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### âš™ï¸ How Frames Interact â€” Method Call Protocol

```
CALLER frame active:
  operand stack: [..., arg1, arg2]
                                  â†“ invokevirtual #method
NEW FRAME created:
  local var table: [this, arg1, arg2]   â† args moved from
  operand stack:   []                      caller's op stack
  frame data:      return_addr = caller's next PC

CALLEE executes...
  computes result
  pushes result onto its operand stack: [result]
                                  â†“ ireturn / areturn
FRAME popped:
  result moved to CALLER's operand stack: [..., result]
  caller resumes from return_addr
```

---

#### ðŸ”„ How It Connects

```
Thread created â†’ Stack allocated
      â†“
main() called â†’ [Frame: main pushed]
      â†“
method call â†’ [Frame pushed on top]
      â†“
bytecode executes within frame
  reads/writes Local Variable Table
  pushes/pops Operand Stack
      â†“
method returns â†’ [Frame popped]
  return value â†’ caller's Operand Stack
      â†“
Exception thrown â†’ Frame Data's exception table checked
  handler found â†’ jump to handler in SAME frame
  no handler    â†’ frame popped, exception propagates to caller
```

---

#### ðŸ’» Code Example â€” Frame by Frame Execution Trace

**Source:**

java

```java
public class FrameDemo {

    public static void main(String[] args) {
        int result = multiply(3, 4);
        System.out.println(result);
    }

    public static int multiply(int a, int b) {
        int product = a * b;
        return product;
    }
}
```

**Bytecode â€” `multiply` method:**

bash

```bash
javap -c FrameDemo
```

```
public static int multiply(int, int);
  Code:
     0: iload_0        // load slot 0 (a=3) â†’ operand stack
     1: iload_1        // load slot 1 (b=4) â†’ operand stack
     2: imul           // pop 3,4 â†’ multiply â†’ push 12
     3: istore_2       // pop 12 â†’ store in slot 2 (product)
     4: iload_2        // load slot 2 (product=12) â†’ stack
     5: ireturn        // return top of stack (12) to caller
```

**Full frame execution trace:**

```
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
FRAME: main()
  Local Var Table: [args=<ref>]
  Operand Stack:   []

  Executes: invokestatic multiply(3, 4)
  â†’ pushes 3, 4 onto operand stack before call
  Operand Stack: [3, 4]
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
FRAME: multiply(int,int)   â† NEW FRAME PUSHED
  Local Var Table: [a=3, b=4, product=?]
  Operand Stack:   []

  PC=0: iload_0
    LVT: [a=3, b=4, product=?]
    OS:  [3]

  PC=1: iload_1
    LVT: [a=3, b=4, product=?]
    OS:  [3, 4]

  PC=2: imul
    LVT: [a=3, b=4, product=?]
    OS:  [12]

  PC=3: istore_2
    LVT: [a=3, b=4, product=12]
    OS:  []

  PC=4: iload_2
    LVT: [a=3, b=4, product=12]
    OS:  [12]

  PC=5: ireturn â†’ returns 12, frame POPPED
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
FRAME: main()   â† RESUMES
  Local Var Table: [args=<ref>, result=12]
  Operand Stack:   [12]  â† return value landed here
  â†’ istore result=12
  â†’ invokevirtual println(12)
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**Exception handling within a frame:**

java

```java
public static int safeDivide(int a, int b) {
    try {
        return a / b;          // PC 0-3
    } catch (ArithmeticException e) {
        return -1;             // PC 10-12 (handler)
    }
}
```

```
// Frame Data's Exception Table:
// From  To   Handler  Type
//  0     4     10     ArithmeticException
//
// If exception thrown between PC 0-4:
//   â†’ JVM checks exception table
//   â†’ ArithmeticException matches
//   â†’ Jump to PC 10 (catch block)
//   â†’ SAME frame â€” not popped
//
// If exception NOT caught:
//   â†’ Frame popped
//   â†’ Exception propagates to caller's frame
//   â†’ Caller's exception table checked
//   â†’ Continues up stack until caught or main() exits
```

**Observing frames via StackWalker (Java 9+):**

java

```java
public class FrameWalker {

    public static void main(String[] args) {
        a();
    }

    static void a() { b(); }
    static void b() { c(); }

    static void c() {
        // Walk the live stack frames â€” no exception needed
        StackWalker.getInstance()
            .forEach(frame -> System.out.printf(
                "  %s.%s() line %d%n",
                frame.getClassName(),
                frame.getMethodName(),
                frame.getLineNumber()
            ));
    }
}

// Output (top to bottom = most recent to oldest):
//   FrameWalker.c() line 14
//   FrameWalker.b() line 11
//   FrameWalker.a() line 10
//   FrameWalker.main() line 6
```

**long/double â€” two-slot variables:**

java

```java
public static void twoSlotDemo(long x, double y) {
    // Local Variable Table:
    // Slot 0,1 â†’ x  (long = 2 slots)
    // Slot 2,3 â†’ y  (double = 2 slots)
    // Total: 4 slots for 2 parameters
    long sum = x + (long) y;
    // Slot 4,5 â†’ sum (long = 2 slots)
}
```

---

#### âš™ï¸ Frame Size â€” Fixed at Compile Time

A key JVM optimization: javac calculates the **exact** size of each frame at compile time:

```
javap -verbose FrameDemo
```

```
public static int multiply(int, int);
  descriptor: (II)I
  Code:
    stack=2    â† max operand stack depth needed
    locals=3   â† local variable table slots needed
    args_size=2
```

> The JVM pre-allocates exactly the right amount of memory when pushing a frame â€” no dynamic resizing, no guessing. This is why stack allocation is so fast.

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Operand stack = local variable table"|Completely separate; LVT = named storage, OS = calculation scratch pad|
|"Frame stores objects"|Frames store **primitive values** and **references** â€” objects are on heap|
|"One frame per thread"|One frame **per active method call** â€” many frames per thread|
|"Frame size is dynamic"|Fixed at **compile time** by javac â€” JVM just allocates that fixed block|
|"Exception always destroys the frame"|Caught exception â†’ frame **survives**; uncaught â†’ frame popped|
|"`this` is magic"|`this` is just **slot 0** in the local variable table â€” ordinary reference|

---

#### ðŸ”¥ Pitfalls in Production

**1. Stack trace truncation â€” losing frame history**

java

```java
// JVM optimization: after same exception thrown many times
// from same location, JVM stops filling stack trace
// for performance (JIT optimization)

// Symptom: exception with empty stack trace []
// Fix: disable this optimization if diagnosis is critical
java -XX:-OmitStackTraceInFastThrow myapp

// Or in catch block:
catch (NullPointerException e) {
    if (e.getStackTrace().length == 0) {
        // JVM omitted trace â€” log context manually
        log.error("NPE at known hotspot, context: {}", context);
    }
}
```

**2. Deep framework stacks â€” hard to read**

```
// Spring MVC + AOP + Security stack trace can be 80+ frames deep
// Real error buried under framework noise

// Fix: use filtered stack traces in logging
// Logback example:
<filter class="ch.qos.logback.classic.filter.EvaluatorFilter">
  <!-- Show only YOUR packages + the actual exception -->
</filter>

// Or programmatically find root cause:
Throwable cause = e;
while (cause.getCause() != null) cause = cause.getCause();
// cause = actual root exception, not wrapper
```

**3. StackWalker vs Thread.currentThread().getStackTrace()**

java

```java
// Old way â€” expensive: captures ALL frames, creates array
StackTraceElement[] frames =
    Thread.currentThread().getStackTrace();

// New way (Java 9+) â€” lazy, only walk what you need
StackWalker walker = StackWalker.getInstance(
    StackWalker.Option.RETAIN_CLASS_REFERENCE
);

// Only fetch caller's frame â€” O(1) vs O(n)
Class<?> caller = walker.getCallerClass();

// Or walk until condition met â€” stops early
Optional<StackWalker.StackFrame> frame = walker
    .walk(frames -> frames
        .filter(f -> f.getClassName().startsWith("com.myapp"))
        .findFirst()
    );
```

---

#### ðŸ”— Related Keywords

- `Stack Memory` â€” the region that holds all stack frames
- `Operand Stack` â€” working scratch area inside each frame
- `Local Variable Table` â€” named storage slots inside each frame
- `Bytecode` â€” instructions that operate on the frame's components
- `Thread` â€” owns the stack that holds the frames
- `StackOverflowError` â€” too many frames pushed, stack exhausted
- `Exception Table` â€” part of frame data; maps bytecode to handlers
- `StackWalker` â€” Java 9+ API for efficient frame inspection
- `JIT Compiler` â€” may eliminate frames entirely via inlining
- `Virtual Threads` â€” heap-backed stacks; frames stored differently

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Per-method execution context: local vars  â”‚
â”‚              â”‚ + operand scratch pad + return context    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Always â€” every method call creates one;   â”‚
â”‚              â”‚ understanding frames = understanding       â”‚
â”‚              â”‚ bytecode, exceptions, and debuggers       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Don't manually inspect frames in prod     â”‚
â”‚              â”‚ hot paths â€” StackWalker is fast but       â”‚
â”‚              â”‚ getStackTrace() is expensive              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "A frame is a method's universe â€” born    â”‚
â”‚              â”‚  on call, destroyed on return, isolated   â”‚
â”‚              â”‚  from every other method's universe"      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Operand Stack â†’ Local Variable Table â†’    â”‚
â”‚              â”‚ JIT Inlining â†’ StackWalker â†’              â”‚
â”‚              â”‚ Virtual Thread Continuations              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

**Entry 009 complete.**

#### ðŸ§  Think About This Before We Continue

**Q1.** The JIT compiler's most powerful optimization is **method inlining** â€” replacing a method call with the method's body directly in the caller. What happens to stack frames when inlining occurs? Does a frame still get created? What does this mean for stack traces in profilers?

**Q2.** Look at this code:

java

```java
public static long compute(int n) {
    long result = 0;
    for (int i = 0; i < n; i++) {
        result += i;
    }
    return result;
}
```

Draw the local variable table slots for this method. How many slots? Which slot holds what? What happens to slot sizing for the `long result` variable specifically?

Next up: **010 â€” Operand Stack** â€” the bytecode execution engine's working memory, how every arithmetic, logical and method-call operation flows through it, and how it differs from the Local Variable Table.
