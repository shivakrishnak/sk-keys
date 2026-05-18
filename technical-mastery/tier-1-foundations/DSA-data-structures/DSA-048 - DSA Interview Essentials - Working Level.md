---
id: DSA-048
title: "DSA Interview Essentials - Working Level"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-025, DSA-047
used_by: DSA-092
related: DSA-025, DSA-047, DSA-092
tags:
  - interview
  - working-level
  - essentials
  - patterns
  - java
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/dsa/dsa-interview-essentials-working-level/
---

## TL;DR

The 12 must-know DSA patterns for working-level engineering
interviews - beyond basics, focusing on the patterns that
appear in 80% of LeetCode medium problems.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-048 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | interview, working-level, patterns |
| **Prerequisites** | DSA-025, DSA-047 |

---

### The 12 Core Patterns

---

**Pattern 1: HashMap for O(1) Lookup**

Any problem asking "find two elements with property X"
→ HashMap complement.

```java
// Two Sum: complement = target - nums[i]
Map<Integer, Integer> map = new HashMap<>();
for (int i = 0; i < nums.length; i++) {
    if (map.containsKey(target - nums[i]))
        return new int[]{map.get(target - nums[i]), i};
    map.put(nums[i], i);
}
```

---

**Pattern 2: Two Pointers for Sorted Arrays**

Any problem on sorted array needing pairs/triplets.

```java
// Template: converge from both ends
int left = 0, right = arr.length - 1;
while (left < right) {
    if (condition) { /* process */ left++; right--; }
    else if (tooSmall) left++;
    else right--;
}
```

---

**Pattern 3: Sliding Window for Subarrays**

Any "longest/shortest subarray with constraint" problem.

```java
// Variable window template
int left = 0, result = 0;
Map<Character, Integer> window = new HashMap<>();
for (int right = 0; right < s.length(); right++) {
    // Expand: add s[right] to window
    while (/* window invalid */) {
        // Shrink: remove s[left] from window; left++
    }
    result = Math.max(result, right - left + 1);
}
```

---

**Pattern 4: BFS for Shortest Path**

Any "minimum steps/hops" or tree level-order problem.

```java
Queue<Node> queue = new LinkedList<>();
Set<Node> visited = new HashSet<>();
queue.offer(start); visited.add(start);
int steps = 0;
while (!queue.isEmpty()) {
    int size = queue.size();
    for (int i = 0; i < size; i++) {
        Node curr = queue.poll();
        if (curr.equals(target)) return steps;
        for (Node neighbor : curr.neighbors())
            if (visited.add(neighbor)) queue.offer(neighbor);
    }
    steps++;
}
```

---

**Pattern 5: DFS for Graph/Tree Exploration**

Any "path exists", "count paths", or tree structure problem.

```java
void dfs(Node node, Set<Node> visited) {
    if (node == null || visited.contains(node)) return;
    visited.add(node);
    // Process node
    for (Node neighbor : node.neighbors())
        dfs(neighbor, visited);
}
```

---

**Pattern 6: Top K with Min-Heap**

"k largest" = maintain min-heap of size k.
"k smallest" = maintain max-heap of size k.

```java
PriorityQueue<Integer> heap = new PriorityQueue<>(); // min
for (int n : nums) {
    heap.offer(n);
    if (heap.size() > k) heap.poll(); // remove min
}
// heap contains k largest
```

---

**Pattern 7: Monotonic Stack for Next Greater/Smaller**

Any "next greater element" or "largest rectangle" problem.

```java
Deque<Integer> stack = new ArrayDeque<>(); // stores indices
for (int i = 0; i < nums.length; i++) {
    // Pop while current element is greater than stack top
    while (!stack.isEmpty() && nums[i] > nums[stack.peek()])
        result[stack.pop()] = nums[i];
    stack.push(i);
}
```

---

**Pattern 8: Binary Search on Answer**

Any "minimum/maximum satisfying constraint" problem with
monotonic feasibility function.

```java
int lo = minPossible, hi = maxPossible;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (feasible(mid)) hi = mid;
    else lo = mid + 1;
}
return lo; // smallest feasible answer
```

---

**Pattern 9: DP - Memoized Recursion**

Any overlapping subproblems (Fibonacci, coin change, etc.)

```java
Map<String, Integer> memo = new HashMap<>();
int dp(int... state) {
    String key = Arrays.toString(state);
    if (memo.containsKey(key)) return memo.get(key);
    // base case check
    int result = /* combine subproblems */;
    memo.put(key, result);
    return result;
}
```

---

**Pattern 10: Union-Find for Connected Components**

Any "group elements", "count components", or "is connected"
problem.

```java
int[] parent = new int[n];
Arrays.fill(parent, -1);  // each node is its own root
int find(int x) {
    if (parent[x] < 0) return x;
    return parent[x] = find(parent[x]); // path compression
}
void union(int a, int b) {
    a = find(a); b = find(b);
    if (a == b) return;
    parent[a] = b; // union by rank omitted for brevity
}
```

---

**Pattern 11: Trie for Prefix Queries**

Any "starts with", "autocomplete", or word search problem.

```java
class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    boolean isEnd = false;
}
// Insert: create nodes for each char
// Search: traverse nodes for each char
// startsWith: traverse without requiring isEnd
```

---

**Pattern 12: In-Order BST = Sorted**

Any problem on BST needing sorted output: in-order traversal.

```java
// k-th smallest: in-order traversal, count nodes
int count = 0, result = -1;
void inOrder(TreeNode node, int k) {
    if (node == null) return;
    inOrder(node.left, k);
    if (++count == k) result = node.val;
    inOrder(node.right, k);
}
```

---

### Interview Execution Checklist

Before coding:
- [ ] Clarify input size (n), constraints, edge cases
- [ ] State brute force and its complexity
- [ ] Identify the pattern (which of the 12?)
- [ ] State time and space complexity before coding

While coding:
- [ ] Write clean code with meaningful variable names
- [ ] Handle null/empty input
- [ ] Trace through a small example

After coding:
- [ ] Dry-run with the interviewer's test case
- [ ] State complexity again
- [ ] Mention possible optimizations

---

### Mastery Checklist

- [ ] Can identify the correct pattern for any LeetCode
      medium problem within 2 minutes
- [ ] Can code each of the 12 patterns from memory
- [ ] Follows the interview execution checklist consistently
