---
layout: default
title: "Object Header"
parent: "Java Fundamentals"
nav_order: 12
permalink: /java/object-header/
---
âš¡ TL;DR â€” The hidden metadata prepended to every heap object containing identity, locking state, GC age, and type pointer â€” invisible in Java source but costs memory on every single object you create.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #012         â”‚ Category: JVM Internals              â”‚ Difficulty: â˜…â˜…â˜…          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Depends on:  â”‚ [[JVM]] [[Heap Memory]] [[Bytecode]] â”‚                          â”‚
â”‚ Used by:     â”‚ [[GC]] [[Synchronized]] [[JIT]]      â”‚                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ“˜ Textbook Definition

Every Java object on the heap is prepended with anÂ **Object Header**Â â€” a JVM-managed metadata block invisible to Java source code. It consists of two machine-word fields: theÂ **Mark Word**Â (stores identity hashcode, GC age, locking state, and GC flags) and theÂ **Klass Pointer**Â (reference to the class metadata in Metaspace). Arrays additionally carry a third field: theÂ **array length**. On a 64-bit JVM with compressed OOPs, the header is typically 12 bytes; without compression, 16 bytes.

---

#### ðŸŸ¢ Simple Definition (Easy)

Every object you create has aÂ **hidden preamble**Â attached by the JVM â€” before your fields even start â€” that stores bookkeeping information the JVM needs for locking, GC, and type checking. You never see it in Java code, but it's always there.

---

#### ðŸ”µ Simple Definition (Elaborated)

When you writeÂ `new Order()`, you think about the fields insideÂ `Order`. But the JVM prepends extra bytes to every object â€” a header containing: what class this object belongs to, how old it is for GC purposes, what its identity hashcode is, and whether any thread currently holds a lock on it. This header enablesÂ `synchronized`,Â `instanceof`, GC age tracking, and identity hashCode â€” all without you doing anything. The cost: every object pays this overhead regardless of how small it is.

---

#### ðŸ”© First Principles Explanation

**The problem:**

The JVM needs to answer four questions about ANY object at runtime, given only a heap pointer:

```
1. What type is this?     â†’ for instanceof, casting, virtual dispatch
2. Is it locked?          â†’ for synchronized blocks
3. How old is it?         â†’ for GC generational promotion
4. What is its identity?  â†’ for default hashCode(), System.identityHashCode()
```

**The constraint:**

Java source code doesn't store any of this. AÂ `Point`Â class withÂ `x`Â andÂ `y`Â has noÂ `type`Â field, noÂ `lockState`Â field, noÂ `gcAge`Â field.

**The solution:**

> Prepend a fixed-size metadata block to every object on the heap â€” managed entirely by the JVM, invisible to Java code.

```
HEAP MEMORY â€” what actually exists for 'new Point(3,4)':

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚         OBJECT HEADER               â”‚  â† JVM managed, invisible
â”‚  Mark Word      (8 bytes)           â”‚
â”‚  Klass Pointer  (4 bytes compressed)â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚         INSTANCE DATA               â”‚  â† your fields
â”‚  int x = 3     (4 bytes)            â”‚
â”‚  int y = 4     (4 bytes)            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Total: 20 bytes for a two-int object
Your fields: 8 bytes
JVM overhead: 12 bytes (60% overhead for small objects!)
```

---

#### â“ Why Does This Exist â€” Why Before What

**Without the Object Header:**

```
synchronized(obj) { ... }
â†’ Where does the JVM store the lock state?
â†’ No header = nowhere to put it
â†’ synchronized impossible without external lock table
   (external table = hash map lookup per lock = slow)

obj.hashCode()  (default implementation)
â†’ Where is the identity hash stored after first call?
â†’ No header = recompute every time OR external map
â†’ External map = memory leak + synchronization overhead

GC generational collection
â†’ How does GC know object's age?
â†’ No header = no age tracking = no generational GC
â†’ No generational GC = collect entire heap every time = slow

instanceof / virtual method dispatch
â†’ How does JVM know what type obj is at runtime?
â†’ No klass pointer = type check requires scanning
â†’ Virtual dispatch (polymorphism) becomes O(n) not O(1)
```

**What breaks without it:**

```
1. synchronized         â†’ needs external lock table (slow)
2. Default hashCode()   â†’ recomputed or external map (slow/leaky)
3. Generational GC      â†’ impossible (no age tracking)
4. instanceof           â†’ O(n) scan instead of O(1) pointer check
5. Virtual dispatch     â†’ method lookup becomes linear
6. GC forwarding        â†’ can't store forwarding pointer during GC
```

**With Object Header:**

```
â†’ O(1) lock acquisition â€” state in Mark Word
â†’ O(1) type check â€” follow Klass Pointer
â†’ O(1) age check â€” 4 bits in Mark Word
â†’ Identity hash stored once in Mark Word
â†’ GC forwarding pointer stored in Mark Word during collection
â†’ All of this with zero Java code, zero developer overhead
```

---

#### ðŸ§  Mental Model / Analogy

> Think of every Java object as aÂ **filed document in a government office**.
> 
> Your document (object fields) contains the actual content â€” name, address, data.
> 
> But stapled to the front is aÂ **government cover sheet**Â (object header) containing:
> 
> - Document type/classification (Klass Pointer â†’ what class)
> - Security clearance / lock status (Mark Word â†’ locking)
> - Filing date / age (Mark Word â†’ GC age)
> - Document ID number (Mark Word â†’ identity hashCode)
> 
> You never write the cover sheet â€” the office (JVM) stamps it automatically. But every document pays the cost of those extra pages, even a one-line memo.

---

#### âš™ï¸ How It Works â€” Mark Word Deep Dive

The Mark Word is the most complex part â€” it'sÂ **multipurpose**, meaning the same 64 bits mean different things depending on object state:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    MARK WORD (64-bit JVM)                        â”‚
â”‚                    8 bytes â€” always present                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ State           â”‚ Bit layout (simplified)                        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
â”‚ Unlocked        â”‚ [identity hashcode: 31b][unused:25b][age:4b]   â”‚
â”‚                 â”‚ [biased:1b=0][lock:2b=01]                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚ Biased Locked   â”‚ [thread_id:54b][epoch:2b][age:4b]              â”‚
â”‚                 â”‚ [biased:1b=1][lock:2b=01]                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚ Lightweight     â”‚ [ptr_to_lock_record:62b][lock:2b=00]           â”‚
â”‚ Locked          â”‚ (points to stack-allocated lock record)        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚ Heavyweight     â”‚ [ptr_to_monitor:62b][lock:2b=10]               â”‚
â”‚ Locked          â”‚ (points to OS mutex â€” ObjectMonitor)           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚ GC Marked       â”‚ [forwarding_ptr:62b][lock:2b=11]               â”‚
â”‚ (during GC)     â”‚ (points to new location during copying GC)     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Last 2 bits = lock state indicator:
  00 â†’ lightweight locked
  01 â†’ unlocked or biased
  10 â†’ heavyweight locked (inflated)
  11 â†’ GC mark (forwarding pointer)
```

**Klass Pointer:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   KLASS POINTER                                  â”‚
â”‚                                                                  â”‚
â”‚  Points to class metadata in Metaspace                          â”‚
â”‚                                                                  â”‚
â”‚  64-bit JVM, no compression: 8 bytes                            â”‚
â”‚  64-bit JVM, compressed OOPs (-XX:+UseCompressedOops):          â”‚
â”‚    4 bytes (default on heaps â‰¤ 32GB)                            â”‚
â”‚                                                                  â”‚
â”‚  Used by:                                                        â”‚
â”‚  â€¢ instanceof checks â†’ follow klass ptr â†’ check type hierarchy  â”‚
â”‚  â€¢ Virtual method dispatch â†’ klass has vtable                   â”‚
â”‚  â€¢ GC â†’ klass knows object size for correct copying             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Array Header â€” extra field:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    ARRAY OBJECT HEADER                           â”‚
â”‚                                                                  â”‚
â”‚  Mark Word      8 bytes                                          â”‚
â”‚  Klass Pointer  4 bytes (compressed)                            â”‚
â”‚  Array Length   4 bytes  â† EXTRA field for arrays only          â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                           â”‚
â”‚  Total:        16 bytes                                          â”‚
â”‚                                                                  â”‚
â”‚  Why needed: GC must know array size to copy it correctly        â”‚
â”‚  int[] arr = new int[100]                                        â”‚
â”‚  â†’ header stores length=100                                      â”‚
â”‚  â†’ GC knows: copy 16 + (100 Ã— 4) = 416 bytes                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ”„ How It Connects

```
new Order()
      â†“
Heap allocates: [Mark Word][Klass Ptr][fields...]
                      â†“           â†“
              locking state    points to
              GC age           Order.class
              identity hash    in Metaspace
              GC forward ptr        â†“
                      â†“        vtable for
              synchronized()   virtual dispatch
              reads/writes     instanceof check
              Mark Word        GC size calc
```

---

#### ðŸ’» Code Example

**Measuring object header cost with JOL (Java Object Layout):**

xml

```xml
<!-- Add to pom.xml -->
<dependency>
    <groupId>org.openjdk.jol</groupId>
    <artifactId>jol-core</artifactId>
    <version>0.17</version>
</dependency>
```

java

```java
import org.openjdk.jol.info.ClassLayout;
import org.openjdk.jol.vm.VM;

public class HeaderDemo {

    static class Point {
        int x;
        int y;
    }

    static class EmptyObject {
        // no fields at all
    }

    static class SingleBoolean {
        boolean flag;
    }

    public static void main(String[] args) {
        System.out.println(VM.current().details());

        // Point: two ints
        System.out.println(ClassLayout.parseClass(Point.class)
            .toPrintable());

        // Empty object
        System.out.println(ClassLayout.parseClass(EmptyObject.class)
            .toPrintable());

        // Single boolean
        System.out.println(ClassLayout.parseClass(SingleBoolean.class)
            .toPrintable());
    }
}
```

```
Output (64-bit JVM, compressed OOPs enabled):

# Point layout:
OFFSET  SIZE   TYPE
     0     4        (object header - mark word part 1)
     4     4        (object header - mark word part 2)
     8     4        (object header - klass pointer)
    12     4    int x
    16     4    int y
    20     4        (alignment padding)
Instance size: 24 bytes
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Header:  12 bytes
Fields:   8 bytes (x + y)
Padding:  4 bytes (alignment to 8-byte boundary)
Total:   24 bytes
Header overhead: 50% of useful data size!

# EmptyObject layout:
OFFSET  SIZE
     0    12   (object header)
    12     4   (alignment padding)
Instance size: 16 bytes
Header overhead: 100% â€” all overhead, zero data!

# SingleBoolean layout:
OFFSET  SIZE
     0    12   (object header)
    12     1   boolean flag
    13     3   (padding)
Instance size: 16 bytes
Header overhead: 75% of total size for 1 byte of data!
```

**Observing Mark Word changes during locking:**

java

```java
import org.openjdk.jol.info.ClassLayout;

public class LockingDemo {

    public static void main(String[] args) {
        Object obj = new Object();

        // State 1: Unlocked
        System.out.println("UNLOCKED:");
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());

        synchronized (obj) {
            // State 2: Locked â€” Mark Word changes
            System.out.println("LOCKED:");
            System.out.println(ClassLayout.parseInstance(obj).toPrintable());
        }

        // State 3: Unlocked again â€” Mark Word reverts
        System.out.println("UNLOCKED AGAIN:");
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());

        // Force identity hashCode â€” occupies Mark Word bits
        int hash = System.identityHashCode(obj);
        System.out.println("AFTER hashCode() call: hash=" + hash);
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());
        // Mark Word now permanently stores the hash
        // â†’ biased locking now IMPOSSIBLE for this object
        //   (hash and thread_id can't share same bits)
    }
}
```

**Memory cost at scale â€” why header size matters:**

java

```java
public class HeaderCost {
    public static void main(String[] args) {
        int objectCount = 10_000_000; // 10 million objects

        // Each Point: 24 bytes total, 12 bytes header
        // 10M Points = 240MB total
        // Header alone = 120MB â€” HALF the memory is overhead

        // Real world: microservice with 10M cached DTOs
        // Switching from many small objects to fewer large ones
        // or using primitive arrays instead of object arrays
        // can cut memory 40-60%

        long headerOverhead = (long) objectCount * 12; // bytes
        System.out.println("Header overhead: "
            + headerOverhead / 1024 / 1024 + " MB");
        // Output: Header overhead: 114 MB
    }
}
```

**Compressed OOPs â€” why heap > 32GB breaks it:**

bash

```bash
# Default: compressed OOPs ON (heap â‰¤ 32GB)
java -Xmx31g -XX:+UseCompressedOops myapp
# Klass Pointer: 4 bytes
# Object header: 12 bytes total

# Heap > 32GB: compressed OOPs automatically disabled
java -Xmx33g myapp
# Klass Pointer: 8 bytes
# Object header: 16 bytes total
# 10M objects Ã— 4 extra bytes = 40MB MORE just from header growth

# The 32GB cliff: going from 31GB to 33GB heap
# actually INCREASES memory usage per object
# Counter-intuitive but real production gotcha
```

---

#### ðŸ” Locking State Transitions via Mark Word

```
Object created
      â†“
[UNLOCKED] mark word: hashcode | age | 01
      â†“
First synchronized(obj) â€” same thread repeatedly
      â†“
[BIASED LOCKED] mark word: thread_id | epoch | age | 01
  â†’ No CAS operation needed for same thread
  â†’ Fastest path
      â†“
Different thread tries to lock
      â†“
Bias revoked â†’ [LIGHTWEIGHT LOCKED]
  mark word: ptr_to_stack_lock_record | 00
  â†’ Uses CAS (Compare-And-Swap)
  â†’ No OS involvement yet
      â†“
Contention â€” thread must wait
      â†“
[HEAVYWEIGHT LOCKED / INFLATED]
  mark word: ptr_to_ObjectMonitor | 10
  â†’ OS mutex involved
  â†’ Thread parked by OS scheduler
  â†’ Most expensive path
      â†“
Lock released
      â†“
[UNLOCKED] again
```

> Note: Biased locking wasÂ **deprecated in Java 15**Â andÂ **removed in Java 21**Â â€” modern JVMs start at lightweight locking. The progression is now: Unlocked â†’ Lightweight â†’ Heavyweight.

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Object size = sum of field sizes"|Always addÂ **12-16 bytes**Â for header + alignment padding|
|"Empty objects have zero overhead"|Empty object =Â **16 bytes**Â â€” all header, zero data|
|"synchronized is always expensive"|Uncontended lightweight lock =Â **CAS only**, very fast|
|"hashCode() is computed every time"|ComputedÂ **once**, stored in Mark Word, cached forever|
|"Klass Pointer is always 8 bytes"|**4 bytes**Â with compressed OOPs (default on heaps â‰¤ 32GB)|
|"Header is part of your class"|Header isÂ **JVM-managed**Â â€” invisible to Java reflection|
|"Biased locking is still used"|**Removed in Java 21**Â â€” don't rely on biased lock behaviour|

#### ðŸ”¥ Pitfalls in Production

**1. The 32GB heap cliff**

bash

```bash
# Team decides to increase heap from 28GB to 36GB
# Expecting linear memory improvement
# Result: performance WORSE, memory usage UP

# Why:
# â‰¤32GB: compressed OOPs â†’ 4-byte klass ptr â†’ 12-byte header
# >32GB: no compressed OOPs â†’ 8-byte klass ptr â†’ 16-byte header
# 10M objects Ã— 4 bytes extra = 40MB more just from headers
# + all object references grow: 4 bytes â†’ 8 bytes
# â†’ cache lines hold fewer pointers â†’ more cache misses

# Fix: stay under 32GB OR jump to significantly larger heap
# (the overhead amortises at very large heap sizes)
# Sweet spot: 28-30GB for compressed OOPs benefit
java -Xmx30g -XX:+UseCompressedOops myapp   # âœ…
java -Xmx33g myapp                           # âŒ loses compression
```

**2. Identity hashCode poisoning biased locks**

java

```java
// Calling System.identityHashCode() on an object
// BEFORE synchronizing on it prevents biased locking
// (hash and thread_id can't share the same Mark Word bits)

// Bad pattern (pre Java 21):
Map<Object, Data> map = new HashMap<>();
map.put(lock, data);           // triggers hashCode computation
                               // â†’ Mark Word now stores hash
                               // â†’ biased locking impossible
synchronized(lock) { ... }    // falls back to lightweight immediately

// In Java 21+ this doesn't matter â€” biased locking removed
// But understanding Mark Word bit contention still relevant
// for custom lock implementations and JVM internals
```

**3. Small object proliferation â€” hidden memory cost**

java

```java
// Anti-pattern: many tiny objects
// Common in event-driven / streaming systems

// Each event wrapper:
class EventWrapper {
    String type;     // reference: 4 bytes
    long timestamp;  // 8 bytes
    // Header: 12 bytes
    // Total: 24 bytes â€” 50% is header
}

// 1M events/sec Ã— 24 bytes = 24MB/sec allocation rate
// GC pressure explodes

// Fix 1: use primitive arrays or ByteBuffer (off-heap)
// Fix 2: object pooling (reuse wrappers)
// Fix 3: value types (Project Valhalla â€” future Java)
//        â†’ eliminates header for small value objects
//        â†’ 'int x, y' in a value type = 8 bytes, no header
```

**4. Arrays of objects vs arrays of primitives**

java

```java
// Array of objects â€” each element is a REFERENCE
// Each referenced object has its OWN header

int[] primitives = new int[1000];
// Array header: 16 bytes
// Data: 1000 Ã— 4 = 4000 bytes
// Total: 4016 bytes âœ…

Integer[] boxed = new Integer[1000];
// Array header: 16 bytes
// References: 1000 Ã— 4 = 4000 bytes
// Each Integer object: 16 bytes (header 12 + int 4)
// Total: 16 + 4000 + (1000 Ã— 16) = 20016 bytes âŒ
// 5Ã— more memory for same data!
```

---

#### ðŸ”— Related Keywords

- `Heap Memory`Â â€” where object headers live
- `Mark Word`Â â€” first field of header; locking + GC + hash
- `Klass Pointer`Â â€” second field; points to class in Metaspace
- `Metaspace`Â â€” where Klass Pointer points to
- `synchronized`Â â€” reads/writes Mark Word for lock state
- `GC`Â â€” uses Mark Word for age tracking and forwarding pointers
- `Compressed OOPs`Â â€” shrinks Klass Pointer from 8 to 4 bytes
- `System.identityHashCode()`Â â€” stored in Mark Word after first call
- `JOL (Java Object Layout)`Â â€” tool to inspect object memory layout
- `Project Valhalla`Â â€” future JVM feature to eliminate headers for value types
- `Object Padding`Â â€” alignment bytes added after fields to reach 8-byte boundary

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Hidden 12-16 byte JVM metadata block on   â”‚
â”‚              â”‚ every heap object â€” enables locking, GC,  â”‚
â”‚              â”‚ type checking, identity hash              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Always present â€” understand it to reason  â”‚
â”‚              â”‚ about memory costs, locking behaviour,    â”‚
â”‚              â”‚ and GC efficiency                         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Avoid many tiny objects in               â”‚
â”‚              â”‚ memory-sensitive paths â€” header overhead  â”‚
â”‚              â”‚ dominates small objects                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Every object pays a 12-byte JVM tax â€”   â”‚
â”‚              â”‚  the smaller the object, the heavier      â”‚
â”‚              â”‚  the tax"                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Mark Word â†’ Compressed OOPs â†’             â”‚
â”‚              â”‚ synchronized internals â†’ GC Forwarding â†’  â”‚
â”‚              â”‚ Project Valhalla â†’ JOL                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ§  Think About This Before We Continue

**Q1.**Â AÂ `Boolean`Â object (wrapping a singleÂ `true`/`false`Â bit) takesÂ **16 bytes**Â on the heap â€” 12 bytes header, 1 byte field, 3 bytes padding. Yet aÂ `boolean`Â primitive takes 1 byte. Now consider aÂ `List<Boolean>`Â with 1 million entries vs aÂ `boolean[]`Â with 1 million entries. Calculate the exact memory difference â€” and what does this tell you about the real cost of autoboxing in high-throughput systems?

**Q2.**Â During GC, the collector needs toÂ **move objects**Â to defragment the heap (copying GC). It writes the new address into the old location so any thread still holding a reference can be redirected. Where exactly does it store this forwarding pointer â€” and why does this work without corrupting the object's data?

---

Next up:Â **013 â€” Escape Analysis**Â â€” the JVM optimisation that determines whether an object can be allocated on the stack instead of the heap, how it eliminates GC pressure, and why it silently makes your code faster without you doing anything.
