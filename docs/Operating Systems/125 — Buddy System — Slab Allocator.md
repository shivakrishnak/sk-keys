---
layout: default
title: "Buddy System — Slab Allocator"
parent: "Operating Systems"
nav_order: 125
permalink: /operating-systems/buddy-system-slab-allocator/
number: "0125"
category: Operating Systems
difficulty: ★★★
depends_on: Virtual Memory, Paging, Page Fault, Cache Line
used_by: Kernel Memory Allocation, malloc, JVM, Database Buffer Pools
related: Fragmentation, SLAB, SLUB, kmalloc, mmap
tags:
  - os
  - memory-management
  - kernel
  - internals
---

# 125 — Buddy System — Slab Allocator

⚡ TL;DR — The buddy system splits/merges RAM in power-of-2 blocks to allocate pages fast with minimal fragmentation; the slab allocator sits on top and caches fixed-size kernel objects (inodes, task_structs) to avoid per-object allocation overhead.

| #0125           | Category: Operating Systems                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, Paging, Page Fault, Cache Line               |                 |
| **Used by:**    | Kernel Memory Allocation, malloc, JVM, Database Buffer Pools |                 |
| **Related:**    | Fragmentation, SLAB, SLUB, kmalloc, mmap                     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The kernel needs to allocate memory for thousands of transient objects: a process creates a socket → kernel needs a `sock` struct (192 bytes); receives a packet → needs an `sk_buff` (240 bytes); creates a file → needs a `file` struct (256 bytes). With naive allocation (first-fit or best-fit), each allocation/deallocation leaves fragments. After millions of allocations: the kernel has plenty of free memory in total, but no contiguous blocks of the required size — **external fragmentation**. Or the kernel must always round up to power-of-2, wasting internal space — **internal fragmentation**.

**THE BREAKING POINT:**
Two levels of fragmentation problem: (1) Page-level: the kernel needs contiguous physical pages for DMA buffers, huge pages, etc. Naive allocation fragments physical memory. (2) Sub-page level: most kernel objects are 64–512 bytes. Allocating a full 4KB page for a 192-byte struct wastes 3904 bytes × thousands of concurrent objects = GBs wasted. These two levels require two different allocators.

**THE INVENTION MOMENT:**
**Buddy system** (Knowlton, 1965): page-level allocator. **Slab allocator** (Bonwick, 1994, SunOS 5.4): object-level allocator on top of buddy. Slab observation: object creation (constructor + cache warming) is expensive; if you never destroy the object (just "free to free-list"), the next allocation gets a warm, already-initialised object. The slab allocator is a per-object-type free-list that keeps objects initialised and cache-hot.

---

### 📘 Textbook Definition

The **buddy system** is the Linux kernel's page frame allocator. It manages physical memory in **free lists** indexed by order (0 to MAX_ORDER=10, representing 1 to 1024 contiguous 4KB pages = 4KB to 4MB blocks). Allocations are rounded up to the nearest power-of-2. When a block of order N is needed but only order N+1 is free, the N+1 block is split into two "buddies" of order N; one is returned, one goes to the order-N free list. On free, if a block's buddy is also free, they are merged back into an order N+1 block (coalescing).

The **slab allocator** (implemented as **SLUB** in Linux 2.6.23+) sits above the buddy system and provides efficient allocation of small, fixed-size kernel objects. For each object type (inode, task_struct, sk_buff, dentry), a **cache** (kmem_cache) is created. Each cache has one or more **slabs** (one or more physically-contiguous pages holding N pre-initialised objects). Free objects are maintained on per-CPU free-lists, enabling lock-free allocation in the common case.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Buddy = splits/merges RAM pages in power-of-2; slab = caches pre-made kernel objects so allocation is just "pop from free list."

**One analogy:**

> Buddy: a parking garage that only sells parking spots in powers of 2 (1, 2, 4, 8 spots). Need 3 spots? Get 4. Return them: the adjacent 4 might merge back to 8. This makes merging trivial (you always know your buddy's location).
> Slab: a kitchen with pre-made pancake batter. Need a pancake? Take one from the warm stack (O(1), cache-hot). Return a pancake? Put it back (no cooking needed). Way faster than mixing batter from scratch each time.

**One insight:**
The slab allocator's key insight is not just reuse — it's **NUMA and cache locality**. Per-CPU slabs mean that on a 64-core machine, allocating an inode on CPU 3 always comes from CPU 3's local cache (no cross-CPU locking, L1/L2 cache warm).

---

### 🔩 First Principles Explanation

BUDDY SYSTEM OPERATION:

```
Free lists: order 0 (4KB), 1 (8KB), 2 (16KB), ... 10 (4MB)
Initial state: one large block at order 10

Request: 12KB → round up to 16KB (order 2)
  Order 2 free list: empty
  → Split order 3 (32KB) → two order-2 buddies (16KB each)
  → Return one to caller; add one to order-2 free list

Request: another 16KB (order 2)
  → Order-2 free list has one → return it

Free: first 16KB block
  → Check buddy: the second 16KB was also freed?
  → Yes → merge → one order-3 (32KB) block → coalesce

Buddy address calculation:
  buddy_address = block_address XOR (1 << (order × PAGE_SHIFT))
  This is why "buddy": the address differs by exactly one bit
```

SLUB ALLOCATOR:

```
kmem_cache for task_struct (size=9216 bytes):
  slab = 3 pages (12KB) holding 1 task_struct + metadata

  Free list per CPU (e.g., CPU 0):
    [task_struct*] → [task_struct*] → [task_struct*] → NULL

kmalloc(sizeof(task_struct)):
  → Check CPU 0's free list (no lock, atomic ptr swap)
  → Pop head → return pre-zeroed, pre-constructed object
  → If free list empty: get new slab from buddy system

kfree(task_struct*):
  → Push back onto CPU 0's free list
  → If slab fully free AND global free list has excess: return to buddy
```

**THE TRADE-OFFS:**
**Gain:** O(1) allocation and deallocation for both page-level (buddy) and object-level (slab); minimal fragmentation; CPU-local allocation avoids NUMA penalties.
**Cost:** Buddy wastes up to 50% of allocation (rounding to power-of-2); slab wastes memory holding objects that will be reused (memory "committed" to each cache can be large); SLUB debugging (`CONFIG_SLUB_DEBUG`) has significant overhead.

---

### 🧪 Thought Experiment

SLAB OBJECT REUSE PERFORMANCE:
Test: allocate 1M inodes, free all, allocate 1M inodes again.

Without slab (raw kmalloc each time):

```
1M alloc × (buddy split + zeroing + inode init + VFS init) = 1.2 seconds
1M free  × (inode destroy + VFS cleanup + buddy merge) = 0.8 seconds
2nd 1M alloc = 1.2 seconds again (cold cache, re-init)
Total: 3.2 seconds
```

With slab allocator:

```
1M alloc × (pop from free list, already initialised) = 0.05 seconds
1M free  × (push to free list, keep initialised) = 0.04 seconds
2nd 1M alloc × (pop from warm free list) = 0.03 seconds
Total: 0.12 seconds
```

27× faster. The slab allocator's win is: objects are never destroyed — their initialisation cost is paid once.

---

### 🧠 Mental Model / Analogy

> **Buddy system** = library book stacks, arranged in sections of 1, 2, 4, 8 shelves. Need a 3-shelf section? Get a 4-shelf section, leave 1 shelf on the "1-shelf" list. Return your 4 shelves? Check if the adjacent 4-shelf section is also free → merge to 8. Fast because address arithmetic immediately locates the buddy.

> **Slab allocator** = cafeteria tray return. Trays go back to a warm stack (not to a dishwasher). When you need a tray, you grab from the warm stack — it's already clean and room temperature. The "clean and room temperature" corresponds to the object's initialised state and cache hotness.

> Where this breaks down: in userspace, tcmalloc (Google) and jemalloc (Meta/FreeBSD) use similar slab-like per-thread caches — the same insight applied to userspace malloc.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The OS has two memory allocation systems: one for large chunks (buddy), one for small objects (slab). The buddy system divides memory in halves recursively until it has the right size. The slab system keeps a pool of pre-made objects ready to hand out instantly, avoiding the overhead of creating them from scratch each time.

**Level 2 — How to use it (junior developer):**
As a developer you indirectly use these every time you: create a Java object (JVM uses slab-like arenas), open a file (kernel allocates inode+dentry from slab), create a socket (sk_buff from slab). You can see slab usage: `cat /proc/slabinfo` or `slabtop`. Useful for: diagnosing kernel memory leaks (growing slab caches), understanding why `kmalloc` is O(1), and understanding why Java's `-XX:+UseTLAB` is the JVM's equivalent of per-CPU slab caches.

**Level 3 — How it works (mid-level engineer):**
SLUB (Linux 2.6.23+, superseded SLAB): Each `kmem_cache` has per-CPU slabs. Allocation: check `kmem_cache_cpu->freelist` (lock-free pointer to next free object within slab). If empty: try `kmem_cache->node[node_id]->partial` (partially-full slabs for this NUMA node). If empty: allocate new slab from buddy system. The slab tracks: which page it lives on (via page->slab_cache pointer), allocation bitmap, and free-list pointer embedded in the object (SLUB stores the free-list pointer in the free object's memory, avoiding extra metadata). SLUB debugging: poison free objects (detect use-after-free), redzone (detect overflow), stack traces on alloc/free.

**Level 4 — Why it was designed this way (senior/staff):**
Bonwick's original slab paper (1994) identified three costs: (1) object construction/destruction (solved by object reuse), (2) data structure allocation for the slab book-keeping (solved by storing metadata in the slab pages themselves), and (3) cache coloring — different slabs for the same size object are placed at different offsets to ensure objects land on different cache lines across slabs, preventing cache-line contention. SLUB (Christoph Lameter, 2007) simplified by removing coloring (it helped on older CPUs; modern CPUs with larger L1 caches benefit less) and focusing on per-CPU locality. The result: SLUB has fewer code paths, is more debuggable, and has better worst-case behavior under NUMA-heavy workloads. Google's `tcmalloc` (2005) and jemalloc (2006) independently arrived at the same design for userspace: per-thread size-class caches of free objects.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           BUDDY + SLAB ARCHITECTURE                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PHYSICAL MEMORY:                                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Free lists: order 0 (4K) | 1 (8K) | ... | 10    │   │
│  │ BUDDY SYSTEM manages at page granularity         │   │
│  └──────────────────────────────────────────────────┘   │
│                     │                                   │
│  SLAB LAYER:         │                                   │
│  kmem_cache: inode_cache (inode = 592 bytes)            │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │  CPU 0 slab      │  │  CPU 1 slab      │             │
│  │  freelist:       │  │  freelist:       │             │
│  │  [obj1→obj2→...] │  │  [obj7→obj8→...] │             │
│  │  (no lock!)      │  │  (no lock!)      │             │
│  └──────────────────┘  └──────────────────┘             │
│         │                                               │
│  Partial slabs (NUMA node 0): [slab A, slab B]          │
│         │                                               │
│  Full slabs: tracked for debugging/accounting           │
│                                                         │
│  kmalloc(inode):                                        │
│    CPU 0's freelist not empty → pop obj1 (L1 cache hit) │
│    → Return obj1 (pre-initialised, warm cache)          │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

NETWORK PACKET RECEIVE PATH (sk_buff allocation):

```
NIC receives Ethernet frame:
1. NIC DMA: writes packet data to pre-allocated DMA ring buffer
   (buddy system: allocated order-0 pages at NIC init)

2. Interrupt: softirq → netif_receive_skb()

3. Allocate sk_buff: alloc_skb()
   → kmem_cache_alloc(skbuff_head_cache)   # from slab: O(1)
   → pop from CPU's sk_buff freelist        # no lock
   → return pre-zeroed sk_buff (240 bytes)

4. Copy/reference packet data into sk_buff

5. Deliver to protocol stack (IP → TCP → socket recv buffer)

6. Application: recv() → data copied to userspace → sk_buff freed
   kfree_skb() → push onto CPU's sk_buff freelist (O(1), no lock)
   → slab: object ready for next packet (still warm, still zeroed-ish)

Performance: 10Gbps NIC = 14.8M packets/sec
sk_buff allocation: <100ns each (from slab)
Without slab (raw kmalloc): ~1000ns each → can't keep up
```

---

### 💻 Code Example

Example 1 — View slab usage (Linux):

```bash
# Top slab caches by memory usage
slabtop -o | head -30

# Specific cache info
cat /proc/slabinfo | grep -E "^(inode_cache|dentry|task_struct|kmalloc)"
# Fields: name, active, num, objsize, objperslab, pagesperslab, limit, batch, shared

# Memory breakdown by slab
cat /proc/meminfo | grep -i slab
# Slab:             1048576 kB  (total slab memory)
# SReclaimable:      786432 kB  (reclaimable: page cache metadata, dentry)
# SUnreclaim:        262144 kB  (non-reclaimable: task_struct, sock, etc.)
```

Example 2 — Kernel module: creating a custom slab cache:

```c
#include <linux/slab.h>

struct my_object {
    int id;
    char name[64];
    spinlock_t lock;
};

static struct kmem_cache *my_cache;

// Module init: create cache
my_cache = kmem_cache_create(
    "my_object_cache",        // name (shown in /proc/slabinfo)
    sizeof(struct my_object), // object size
    0,                        // alignment (0 = natural)
    SLAB_HWCACHE_ALIGN,       // flags: align to cache line
    NULL                      // constructor (NULL: zero-fill)
);

// Allocation: O(1), from CPU-local cache
struct my_object *obj = kmem_cache_alloc(my_cache, GFP_KERNEL);

// Free: O(1), returns to CPU-local cache
kmem_cache_free(my_cache, obj);

// Module exit: destroy cache (all objects must be freed first)
kmem_cache_destroy(my_cache);
```

Example 3 — Buddy system: get/free pages:

```c
#include <linux/gfp.h>

// Allocate 2^order contiguous pages
// order=0: 4KB, order=1: 8KB, order=2: 16KB
struct page *page = alloc_pages(GFP_KERNEL, 2);  // order=2: 16KB (4 pages)
void *vaddr = page_address(page);                  // virtual address

// Use the pages (DMA buffer, huge pages, etc.)
memset(vaddr, 0, 4 * PAGE_SIZE);

// Free back to buddy system
free_pages((unsigned long)vaddr, 2);
// buddy system: checks buddy block → merge if free → coalesce upward
```

---

### ⚖️ Comparison Table

| Allocator        | Level     | Granularity           | Algorithm                         | Best For                   |
| ---------------- | --------- | --------------------- | --------------------------------- | -------------------------- |
| **Buddy system** | Kernel    | Pages (4KB–4MB)       | Power-of-2 split/merge            | Contiguous page allocation |
| **SLUB**         | Kernel    | Objects (8B–8KB)      | Per-CPU free lists                | Fixed-size kernel objects  |
| **kmalloc**      | Kernel    | Arbitrary (uses SLUB) | Size classes                      | General kernel allocations |
| **tcmalloc**     | Userspace | Objects (8B–256KB)    | Per-thread size classes           | C++ server allocations     |
| **jemalloc**     | Userspace | Objects               | Per-thread arenas                 | Firefox, Redis, FreeBSD    |
| **JVM TLAB**     | JVM       | Java objects          | Bump pointer in thread-local area | Java object allocation     |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                         |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| "Buddy system wastes memory"           | Worst-case 50% waste for power-of-2 rounding, but in practice most allocations are exact powers of 2; slab caches further reduce waste          |
| "Slab allocator is just a free list"   | It also provides CPU locality (per-CPU caches), NUMA awareness (per-node partial lists), and keeps objects initialised between uses             |
| "kmalloc(N) allocates exactly N bytes" | Rounds up to the nearest size class; `kmalloc(200)` gets a 256-byte slab object                                                                 |
| "SLAB and SLUB are the same"           | SLAB (older): complex with coloring and per-CPU/per-node caches separately. SLUB (modern): simplified, per-CPU active slab pointer, no coloring |

---

### 🚨 Failure Modes & Diagnosis

**1. Slab Memory Leak (kernel)**

**Symptom:** Memory usage grows continuously; `free -h` shows decreasing `available`; `cat /proc/meminfo` shows `Slab` growing; application and page cache sizes unchanged.

Diagnosis:

```bash
# Check growing slab caches
watch -n 5 'slabtop -o | head -20'
# If a specific cache (e.g., dentry, inode_cache) grows unboundedly → leak

# More detailed
cat /proc/slabinfo | sort -k3 -rn | head -20  # Sort by total objects
```

Root Cause Examples: dentry cache growth from filesystem with millions of short-lived files; inode cache leak from missing `iput()` in a kernel module.

---

**2. Buddy System Fragmentation (unable to allocate huge pages)**

**Symptom:** `grep HugePages_Free /proc/meminfo` shows 0 despite `MemFree` being large; `cat /proc/buddyinfo` shows many order-0 to order-3 blocks but none at order-9 (2MB).

Diagnosis:

```bash
cat /proc/buddyinfo
# Node 0, zone Normal: 512 256 128 64 32 8 0 0 0 0 0
# Many small free blocks; nothing at high orders → fragmented

# Attempt defrag (transparent huge page compaction)
echo 1 > /proc/sys/vm/compact_memory
# Re-check buddyinfo after compaction
```

**Fix:** `vm.min_free_kbytes` increase forces more aggressive reclaim before fragmentation; `khugepaged` (THP daemon) performs compaction; for critical workloads use `hugetlbfs` with pre-reserved huge pages at boot.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — buddy system allocates physical page frames; virtual memory maps them
- `Paging` — buddy allocates contiguous physical pages; paging maps virtual to physical
- `Cache Line` — slab coloring and per-CPU caches optimize for cache line locality

**Builds On This (learn these next):**

- `NUMA` — SLUB's per-node partial lists exist specifically for NUMA topology
- `Huge Pages` — require contiguous physical pages; depend on buddy system order-9 blocks
- `Fragmentation` — the specific problem both buddy and slab are designed to prevent

**Alternatives / Comparisons:**

- `tcmalloc / jemalloc` — userspace equivalents of slab (per-thread caches, size classes)
- `JVM TLAB` — thread-local allocation buffers: same insight as per-CPU slab caches applied to JVM heap

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Buddy: page allocator (power-of-2 blocks)│
│              │ Slab: object allocator (pre-made objects) │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Fragmentation at page level (buddy);     │
│ SOLVES       │ allocation overhead at object level (slab)│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Slab: objects stay initialised between   │
│              │ uses; allocation = pop from CPU freelist  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Understanding kernel OOM, huge page      │
│              │ failures, or GC design decisions         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ "Avoid" = avoid kernel memory leaks by   │
│              │ always pairing kmem_cache_alloc + _free  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Speed/locality (slab) vs memory overhead │
│              │ (keeps objects and slabs warm in memory) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Buddy splits pages; slab caches objects"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ NUMA → Huge Pages → tcmalloc/jemalloc    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The JVM's Thread-Local Allocation Buffer (TLAB) is conceptually identical to SLUB's per-CPU active slab: each thread has a small region of the Eden heap (~1% of Eden by default) where it allocates Java objects using bump-pointer allocation (just increment a pointer — no lock, no CAS). TLAB exhaustion triggers TLAB refill from the shared Eden (which requires a CAS or lock). In G1GC, each region (1–32MB) is independently managed. Explain: (1) why bump-pointer allocation in TLAB is O(1) with no synchronization, (2) what happens when an object is larger than the TLAB, (3) how TLAB size is dynamically adjusted by the JVM (hint: based on allocation rate and GC frequency), and (4) why a system with 1000 threads each with 1MB TLABs might waste more Eden space than it saves in synchronization overhead.

**Q2.** Linux's `kcompactd` kernel thread performs memory compaction: it walks physical memory, migrating moveable pages (most non-slab pages) to create contiguous free areas for buddy system high-order allocations. During compaction, migrated pages' PTEs in all processes must be updated. On a 64-core NUMA machine with 512GB RAM, compaction of a 1GB contiguous region requires scanning and potentially migrating thousands of pages. Explain: (1) which pages cannot be migrated (pinned by DMA, slab objects, kernel stack pages) and why, (2) how the page migration mechanism works (alloc new page, copy content, atomic PTE swap), (3) why compaction is triggered by THP (Transparent Huge Pages) allocation failures but not by normal 4KB allocations, and (4) the production trade-off between `khugepaged` aggressiveness and application latency spikes from compaction pauses.
