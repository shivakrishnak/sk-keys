---
layout: default
title: "011 — Local Variable Table"
parent: "Java Fundamentals"
nav_order: 11
permalink: /java/011-local-variable-table/
---
# â˜• Local Variable Table

ðŸ·ï¸ Tags â€” #java #jvm #internals #memory #bytecode #deep-dive

âš¡ TL;DR â€” The indexed slot array inside every stack frame that stores a method's parameters and local variables â€” fixed at compile time, zero GC overhead, lives and dies with its frame. 

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #011  â”‚ Category: JVM Internals  â”‚ Difficulty: â˜…â˜…â˜…   â”‚
â”‚ Depends on: Stack Frame,         â”‚ Used by: Every    â”‚
â”‚ Bytecode, Operand Stack          â”‚ method execution, â”‚
â”‚                                  â”‚ Debugger, JIT     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ“˜ Textbook Definition

The Local Variable Table (LVT) is a **fixed-size, indexed array of variable slots within a stack frame** that stores a method's parameters and locally declared variables. Slot 0 holds `this` for instance methods. Each slot holds a primitive value or object reference. `long` and `double` occupy two consecutive slots. The table's size is determined at compile time by `javac` and stored in the `.class` file's `Code` attribute.

---

#### ðŸŸ¢ Simple Definition (Easy)

The Local Variable Table is the method's **named storage cabinet** â€” every parameter and local variable gets a numbered drawer, and bytecode reads and writes to those drawers by number.

---

#### ðŸ”µ Simple Definition (Elaborated)

When `javac` compiles a method, it assigns every parameter and local variable a slot number â€” like locker numbers. The JVM uses these numbers, not names, at runtime. `iload_2` means "push the integer from slot 2 onto the operand stack" â€” it doesn't know or care that slot 2 is called `total`. Names are debug metadata, not runtime reality. The table is pre-sized exactly right at compile time â€” no dynamic resizing, no GC, instant allocation when the frame is pushed.

---

#### ðŸ”© First Principles Explanation

**The problem:**

A method needs to store:

- Its incoming parameters
- Variables it declares during execution
- The `this` reference (for instance methods)

These need to be:

- Instantly accessible by bytecode instructions
- Completely isolated from other methods' variables
- Automatically cleaned up when the method exits

**The naive solution â€” heap allocation:**

```
Store local vars as objects on heap â†’ GC cleans up
Problem:
  â€¢ GC overhead for every method call
  â€¢ Slow allocation
  â€¢ Cache-unfriendly (heap pointers everywhere)
```

**The right solution â€” pre-allocated indexed array:**

```
javac analyses the method at compile time:
  â€¢ Counts all parameters
  â€¢ Counts all local variables
  â€¢ Determines maximum slots needed
  â€¢ Writes that number into .class file

JVM at runtime:
  â€¢ Reads slot count from .class
  â€¢ Allocates exactly that many slots on stack
  â€¢ No counting, no resizing, no GC
  â€¢ Just: frame_base_ptr + (slot_index * slot_size)
```

> Access to any slot = single pointer arithmetic operation. O(1), cache-hot, zero overhead.

---

#### â“ Why Does This Exist â€” Why Before What

**Without the Local Variable Table:**

**Option A â€” Use Operand Stack for everything:**

```
Every intermediate AND named variable goes on operand stack
Problem:
  â€¢ Stack is LIFO â€” can't randomly access variable 'a'
    while 'b', 'c', 'd' are on top of it
  â€¢ Reading 'a' mid-computation = impossible without
    destroying the stack
  â€¢ Code generation becomes nightmarish
```

**Option B â€” Use heap for local variables:**

```
Allocate local vars as heap objects
Problem:
  â€¢ GC pressure on every method call
  â€¢ Cache misses â€” heap is not as cache-hot as stack
  â€¢ Pointer chasing for every variable access
  â€¢ OOP overhead for primitive integers
```

**Option C â€” Use CPU registers directly:**

```
Map local vars to actual CPU registers
Problem:
  â€¢ CPU-specific â€” x86 has 16 general registers,
    ARM has different count/rules
  â€¢ Methods with 20 local vars â†’ register spilling
  â€¢ Bytecode becomes platform-specific
  â€¢ Destroys "write once, run anywhere"
```

**What breaks without LVT:**

```
1. Random access to named variables â†’ impossible on pure stack
2. Platform independence â†’ broken if using CPU registers
3. Performance â†’ destroyed if using heap
4. GC pressure â†’ explodes with heap-allocated locals
5. Debugger support â†’ can't inspect named variables
```

**With LVT:**

```
â†’ Platform-independent indexed access (JIT maps to registers later)
â†’ O(1) random access to any variable by slot number
â†’ Zero GC overhead â€” lives on stack
â†’ Exact size pre-calculated â€” no waste, no resize
â†’ Debugger reads names from .class metadata â†’ human-readable
```

---

#### ðŸ§  Mental Model / Analogy

> Think of a method call as renting a **safety deposit box room** at a bank.
> 
> When you enter (method called), the bank assigns you a room with exactly N numbered boxes (slots) â€” pre-determined by the vault architect (javac) who designed this room type.
> 
> - Box 0: always holds your ID (this reference)
> - Box 1, 2...: your parameters, handed to you at the door
> - Remaining boxes: empty, ready for things you'll store during your visit
> 
> You can open any box instantly by number â€” O(1). When you leave (method returns), the entire room is released instantly â€” no cleanup crew needed.
> 
> The box **numbers** are what matter at runtime. The **names** on the labels (variable names) are just for your convenience â€” the bank doesn't care.

---

#### âš™ï¸ How It Works â€” Slot Assignment Rules

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚            SLOT ASSIGNMENT BY JAVAC                     â”‚
â”‚                                                         â”‚
â”‚  INSTANCE METHOD:                                       â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ Slot â”‚ Content                                  â”‚   â”‚
â”‚  â”œâ”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”‚
â”‚  â”‚  0   â”‚ this  (always â€” implicit first param)    â”‚   â”‚
â”‚  â”‚  1   â”‚ first declared parameter                 â”‚   â”‚
â”‚  â”‚  2   â”‚ second declared parameter                â”‚   â”‚
â”‚  â”‚  3   â”‚ third declared parameter (or 3+4 if long)â”‚   â”‚
â”‚  â”‚  N   â”‚ first local variable declared in method  â”‚   â”‚
â”‚  â”‚ N+1  â”‚ second local variable                    â”‚   â”‚
â”‚  â”‚ ...  â”‚ ...                                      â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                         â”‚
â”‚  STATIC METHOD:                                         â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ Slot â”‚ Content                                  â”‚   â”‚
â”‚  â”œâ”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”‚
â”‚  â”‚  0   â”‚ first declared parameter (no 'this')     â”‚   â”‚
â”‚  â”‚  1   â”‚ second declared parameter                â”‚   â”‚
â”‚  â”‚  2   â”‚ first local variable                     â”‚   â”‚
â”‚  â”‚ ...  â”‚ ...                                      â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                         â”‚
â”‚  TYPE RULES:                                            â”‚
â”‚  â€¢ int, float, reference â†’ 1 slot                      â”‚
â”‚  â€¢ long, double           â†’ 2 consecutive slots        â”‚
â”‚  â€¢ boolean, byte, char, short â†’ stored as int (1 slot) â”‚
â”‚                                                         â”‚
â”‚  SCOPE REUSE:                                           â”‚
â”‚  â€¢ If variable goes out of scope, its slot can be      â”‚
â”‚    reused by a later variable in the same method       â”‚
â”‚  â€¢ javac optimises slot count by reusing slots         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ”„ How It Connects

```
javac compiles method
      â†“
Calculates max slots needed
Writes into .class Code attribute: locals=N
      â†“
Class Loader loads .class
      â†“
Method called â†’ Stack Frame created
      â†“
[Local Variable Table] allocated: N slots
  â† parameters copied in from caller's Operand Stack
      â†“
Bytecode executes:
  iload_N  â†’ LVT slot N â†’ Operand Stack
  istore_N â† Operand Stack â†’ LVT slot N
      â†“
Method returns â†’ Frame popped
  â†’ LVT instantly gone (no GC)
  â†’ Return value was on Operand Stack, passed to caller
```

---

#### ðŸ’» Code Example â€” Slot Assignment in Detail

**Instance method â€” full slot trace:**

java

```java
public class Order {

    public double calculateTotal(int quantity, double price) {
        double subtotal = quantity * price;
        double tax = subtotal * 0.1;
        return subtotal + tax;
    }
}
```

bash

```bash
javap -c -verbose Order
```

```
public double calculateTotal(int, double);
  descriptor: (ID)D
  flags: ACC_PUBLIC
  Code:
    stack=4       â† max operand stack depth
    locals=6      â† total LVT slots needed
    args_size=3   â† this + quantity + price (double=2)
```

**LVT slot assignment:**

```
Slot 0 â†’ this          (reference, 1 slot)
Slot 1 â†’ quantity      (int,       1 slot)
Slot 2 â†’ price         (double,    2 slots â†’ occupies 2,3)
Slot 4 â†’ subtotal      (double,    2 slots â†’ occupies 4,5)
         â†‘ slot 3 is second half of 'price'
         tax would be slot 6,7 BUT javac reuses slots...

Actually with optimisation:
Slot 4,5 â†’ subtotal
Slot 6,7 â†’ tax
locals = 8
```

**Bytecode trace:**

```
 0: iload_1           // push quantity (slot 1) â†’ OS: [qty]
 1: i2d               // convert intâ†’double     â†’ OS: [qty_d]
 2: dload_2           // push price (slots 2,3) â†’ OS: [qty_d, price]
 3: dmul              // pop two doubles, multiply â†’ OS: [subtotal]
 4: dstore 4          // pop â†’ store in slots 4,5 (subtotal)
 6: dload 4           // push subtotal          â†’ OS: [subtotal]
 8: ldc2_w 0.1        // push constant 0.1      â†’ OS: [subtotal, 0.1]
11: dmul              // multiply               â†’ OS: [tax]
12: dstore 6          // store tax in slots 6,7
14: dload 4           // push subtotal          â†’ OS: [subtotal]
16: dload 6           // push tax               â†’ OS: [subtotal, tax]
18: dadd              // add                    â†’ OS: [total]
19: dreturn           // return double to caller
```

---

**Slot reuse â€” javac optimisation:**

java

```java
public static void slotReuse(boolean flag) {
    if (flag) {
        int x = 10;         // x gets slot 1
        System.out.println(x);
    }   // x goes out of scope here â€” slot 1 now FREE

    if (!flag) {
        int y = 20;         // y REUSES slot 1 (x is gone)
        System.out.println(y);
    }
    // max locals = 2 (slot 0: flag, slot 1: x OR y)
    // NOT 3 â€” javac is smarter than that
}
```

bash

```bash
javap -verbose SlotReuse | grep locals
# locals=2   â† confirmed: slot reuse happened
# NOT locals=3
```

---

**Debugger metadata â€” variable names are NOT in bytecode:**

bash

```bash
# Without debug info (default javac):
javac SlotReuse.java
javap -l SlotReuse
# LocalVariableTable: NOT SHOWN
# Debugger sees: slot 0, slot 1 â€” no names

# With debug info:
javac -g SlotReuse.java
javap -l SlotReuse
```

```
LocalVariableTable:
  Start  Length  Slot  Name        Signature
      0      20     0  flag        Z          â† boolean
      3       8     1  x           I          â† int
     12       8     1  y           I          â† int, SAME slot 1!
```

> The debugger uses this metadata to show you `x` and `y` as names â€” but the JVM only ever sees slot 1. Names are purely for human consumption, compiled in only with `-g` flag or by default in most build tools.

---

**The `this` reference â€” just slot 0:**

java

```java
public class Counter {
    private int count = 0;

    public void increment() {
        // 'this' is slot 0 â€” invisible in source, present in bytecode
        this.count++;
    }
}
```

```
Bytecode for increment():
  0: aload_0          // push 'this' (slot 0) â†’ OS: [this_ref]
  1: aload_0          // push 'this' again    â†’ OS: [this_ref, this_ref]
  2: getfield count   // pop ref, get field   â†’ OS: [this_ref, count_val]
  5: iconst_1         // push 1               â†’ OS: [this_ref, count_val, 1]
  6: iadd             // add                  â†’ OS: [this_ref, count_val+1]
  7: putfield count   // pop ref+val, store field â†’ OS: []
 10: return
```

> Every `this.field` access = `aload_0` + `getfield`. `this` is not magic â€” it's slot 0, an ordinary reference.

---

**long/double two-slot behaviour:**

java

```java
public static void twoSlots(int a, long b, double c, int d) {
    // Slot assignment:
    // slot 0 â†’ a     (int,    1 slot)
    // slot 1 â†’ b     (long,   2 slots â†’ 1,2)
    // slot 3 â†’ c     (double, 2 slots â†’ 3,4)
    // slot 5 â†’ d     (int,    1 slot)
    // total: 6 slots for 4 parameters
}
```

bash

```bash
javap -verbose TwoSlots | grep locals
# locals=6
# args_size=6  â† JVM counts slot consumption, not param count
```

---

#### âš™ï¸ LVT Size Calculation â€” How javac Does It

```
javac performs LIVENESS ANALYSIS:

1. Build control flow graph of method
2. Track which variables are "live" at each point
3. Assign slots â€” dead variable's slot can be reused
4. Calculate maximum simultaneous live slots = locals=N

Example:
  void method() {
      int a = 1;     // slot 1 live
      int b = 2;     // slot 2 live  â†’ max so far: 3 (this+a+b)
      use(a, b);
      // a, b dead here
      int c = 3;     // slot 1 reused (a was here)
      int d = 4;     // slot 2 reused (b was here)
      use(c, d);
  }
  locals = 3   (not 5)
  â† javac reused slots 1,2
```

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Variable names exist at runtime"|Names are **debug metadata** â€” JVM only uses slot numbers|
|"`this` is special/magic"|`this` is **slot 0** â€” an ordinary reference in LVT|
|"Each variable always gets its own slot"|javac **reuses slots** when variables go out of scope|
|"long/double = 1 slot"|They consume **2 consecutive slots** â€” category 2 types|
|"LVT can grow during execution"|Size is **fixed at compile time** â€” zero dynamic resizing|
|"boolean/byte/char have their own slot type"|All stored as **int** in LVT â€” JVM has no sub-int slot types|
|"Static and instance methods work the same"|Static methods have **no slot 0** â€” no `this` reference|

---

#### ðŸ”¥ Pitfalls in Production

**1. Missing debug info â€” blind debugging**

bash

```bash
# Production builds often strip debug info for size:
javac -g:none MyClass.java  # no debug info at all
# or Maven with:
<compilerArg>-g:none</compilerArg>

# Result: debugger shows slot numbers, not names
# Stack traces show line numbers as -1 or "Unknown Source"
# Profilers can't show variable names

# Recommendation: always compile with -g (default in Maven/Gradle)
# Size overhead is minimal (~5-10%) vs massive debug value
# Especially critical for production heap dumps
```

**2. Slot reuse surprises in bytecode manipulation**

java

```java
// You generate bytecode with ASM expecting:
// slot 1 = variable 'x' throughout method
// But javac (or your own generator) reused slot 1 for 'y'
// after 'x' went out of scope

// Symptom: wrong variable value read from slot
// Diagnosis: javap -l MyClass  â†’ check LocalVariableTable
// shows slot start/length ranges

// Fix: in ASM, use LocalVariableNode to track slot lifetimes
//      or use COMPUTE_FRAMES flag to let ASM handle it
```

**3. Large LVT in hot methods â€” JIT pressure**

java

```java
// Method with many local variables:
public void process(Order order) {
    int id          = order.getId();
    String name     = order.getName();
    double price    = order.getPrice();
    int quantity    = order.getQuantity();
    double subtotal = price * quantity;
    double discount = calculateDiscount(subtotal);
    double tax      = calculateTax(subtotal - discount);
    double total    = subtotal - discount + tax;
    String status   = determineStatus(total);
    // ... 20 more variables
}
// Large LVT â†’ more slots to map to CPU registers
// JIT register allocator has to spill excess to stack
// â†’ More memory traffic â†’ slower JIT output

// Fix: extract sub-methods â†’ smaller frames â†’ better JIT
```

**4. Thread-safety illusion with reference slots**

java

```java
public void process() {
    // 'list' reference is in LVT â†’ thread-local â†’ safe âœ…
    List<Order> list = new ArrayList<>();

    // BUT: if list was passed in as parameter:
    // the REFERENCE is in LVT â†’ thread-local
    // the OBJECT it points to is on HEAP â†’ shared âŒ
    list.add(new Order());  // safe if list created here

    // Passed-in list:
    public void process(List<Order> list) {
        list.add(new Order()); // â† NOT thread-safe
        // list reference in slot 1 is thread-local
        // but the ArrayList object is shared on heap
    }
}
```

---

#### ðŸ”— Related Keywords

- `Stack Frame` â€” the container holding the LVT
- `Operand Stack` â€” the working counterpart to LVT
- `Bytecode` â€” uses slot indices (`iload_N`, `istore_N`) to access LVT
- `javac` â€” performs liveness analysis and assigns slots
- `javap -l` â€” reveals LVT slot assignments and name metadata
- `this` â€” always slot 0 in instance method LVT
- `long / double` â€” category 2 types; consume 2 LVT slots
- `Escape Analysis` â€” JVM may eliminate LVT entries entirely
- `JIT Compiler` â€” maps LVT slots to CPU registers
- `Debugger (JDWP)` â€” reads LVT metadata to show variable names
- `ASM / ByteBuddy` â€” must correctly declare LVT when generating bytecode

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Fixed-size indexed slot array in each     â”‚
â”‚              â”‚ frame â€” stores params + locals by number  â”‚
â”‚              â”‚ not by name; names are debug-only         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Always present â€” understanding LVT        â”‚
â”‚              â”‚ unlocks bytecode reading, debugger        â”‚
â”‚              â”‚ behaviour, and JIT optimisation           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Don't assume variable names survive to    â”‚
â”‚              â”‚ runtime â€” strip-debug builds break        â”‚
â”‚              â”‚ name-based reflection assumptions         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "LVT = method's numbered locker room â€”    â”‚
â”‚              â”‚  slot 0 is always 'this', names are       â”‚
â”‚              â”‚  labels for humans, numbers for JVM"      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Operand Stack â†’ JIT Register Allocation â†’ â”‚
â”‚              â”‚ Escape Analysis â†’ javap -l â†’              â”‚
â”‚              â”‚ JDWP Debugger Protocol                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

**Entry 011 complete.**

#### ðŸ§  Think About This Before We Continue

**Q1.** `javac` reuses LVT slots when variables go out of scope. Now consider this scenario: you're writing a security-sensitive method that stores a password in a local `char[]` variable, zeroes it out, then the variable goes out of scope. The slot gets reused by another variable. What are the implications â€” and does zeroing actually guarantee the sensitive data is gone?

**Q2.** The JIT compiler's register allocator maps LVT slots to CPU registers. A method has 20 local variables but x86-64 only has 16 general-purpose registers. What has to happen â€” and what performance implications does that have for methods with many local variables?

---

Next up: **012 â€” Object Header** â€” the hidden metadata prepended to every object on the heap: Mark Word, Klass Pointer, array length, how they enable locking, GC, and type checking â€” and why every object costs more memory than its fields suggest.
