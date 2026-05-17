---
id: RCT-039
title: React Reconciliation Algorithm
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-011, RCT-015, RCT-039
used_by: RCT-035, RCT-036, RCT-037, RCT-052, RCT-053
related: RCT-011, RCT-052, RCT-053
tags:
  - react
  - frontend
  - internals
  - performance
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /react/react-reconciliation-algorithm/
---

# RCT-039 - REACT RECONCILIATION ALGORITHM

⚡ TL;DR - React's reconciliation algorithm diffs two
virtual DOM trees to find the minimal set of DOM operations
needed after a state change; it uses two heuristics to
achieve O(n) complexity instead of O(n^3): same-type
elements are updated in place (not replaced), and the
`key` prop identifies stable list elements across renders.

| #039            | Category: React                                                                           | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual DOM and Reconciliation, List Rendering and key Prop                               |                 |
| **Used by:**    | useMemo Hook, useCallback Hook, React.memo, React Fiber Architecture, Concurrent Features |                 |
| **Related:**    | Virtual DOM, React Fiber Architecture, React.memo                                         |                 |

---

### 🔥 The Problem This Solves

**O(N^3) TREE DIFF IS TOO SLOW:**
The general algorithm for comparing two arbitrary trees
is O(n^3) where n is the number of nodes. For a React
app with 1,000 elements, that is 1,000,000,000 operations
per render. At 60fps, this is physically impossible.

React's reconciliation uses two domain-specific heuristics
that reduce this to O(n) for the vast majority of UI
patterns:

1. Two elements of different types will produce different
   trees - replacing the entire subtree is correct and
   efficient
2. `key` props identify stable list items across renders -
   elements with the same key are updated in place instead
   of being replaced

Understanding these two heuristics explains why: incorrect
keys cause visible bugs, changing an element type causes
state loss, and the `key` prop must come from the data,
not from the array index.

---

### 📘 Textbook Definition

**React Reconciliation Algorithm** - the "diffing" algorithm
React uses to compare the previous virtual DOM tree with
the new virtual DOM tree produced after a state change.
The algorithm determines which DOM nodes to create, update,
or delete. It operates on Fiber nodes (React 16+). Its
O(n) complexity relies on two heuristics: (1) element
type identity - same type → update, different type →
replace, and (2) key identity - same key → same element,
different/no key → index-based matching.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// HEURISTIC 1: Type identity
// Before: <div>content</div>
// After:  <span>content</span>
// Result: REPLACE (unmount div tree, mount span tree)
//         div's state and children are DESTROYED

// Before: <Button>text</Button>
// After:  <Button>text</Button>
// Result: UPDATE in place (same type, same component)
//         Button's state is PRESERVED

// HEURISTIC 2: Key identity
// Before: [<Item key="a"/>, <Item key="b"/>]
// After:  [<Item key="b"/>, <Item key="a"/>]
// Result: MOVE items (key "a" to position 2, "b" to 1)
//         State of each Item component is PRESERVED

// Without keys (or with index keys):
// Before: [<Item id="a"/>, <Item id="b"/>]
// After:  [<Item id="b"/>, <Item id="a"/>]
// Result: UPDATE in place (position 0 updates a→b, 1 updates b→a)
//         Component STATE persists at position 0 (now showing "b")
//         Input focus, scroll position, component state: WRONG
```

---

### 🔩 First Principles Explanation

**THE TWO HEURISTICS IN DETAIL:**

**Heuristic 1 - Element Type:**

```
React traverses both trees simultaneously (old tree, new tree).
For each position, it compares the element TYPE.

If types match: React UPDATES the existing DOM node.
  <div className="old"> → <div className="new">
  DOM node is reused. React updates attributes.
  Child components: recursively reconciled.
  Component state: PRESERVED (same component instance).

If types differ: React REPLACES the entire subtree.
  <div> → <span>
  Old div and ALL its children: UNMOUNT (componentWillUnmount)
  New span and ALL its children: MOUNT (fresh start)
  All component state in the subtree: DESTROYED.

Example bug:
  function Parent() {
    return isLoading ? <Spinner /> : <UserProfile />;
    // Spinner and UserProfile are different types
    // On isLoading=false: Spinner unmounts, UserProfile mounts fresh
    // This is CORRECT - you want a fresh UserProfile
  }

  function Parent() {
    // BAD: ternary changes the element at the same tree position
    return (
      <div>
        {isEditing ? <TextInput /> : <TextDisplay />}
        // When isEditing changes: TextInput state is DESTROYED
        // Including typed text, focus, cursor position
      </div>
    );
    // Fix: keep both in the tree, use CSS display or conditional rendering
    // that preserves the same type at the same position
  }
```

**Heuristic 2 - Key:**

```
For lists of elements, React uses the key prop to match
old elements to new elements, regardless of position.

Without key (or index key):
  Old: [A, B, C]  position 0=A, 1=B, 2=C
  New: [D, A, B, C]  (prepend D)
  React matches by position: 0→0, 1→1, 2→2, 3 is new
  Updates: A gets D's data, B gets A's data, C gets B's data, new C
  WRONG: all items updated, state of A preserved on position 0 (now D)

With stable key:
  Old: [A(key=a), B(key=b), C(key=c)]
  New: [D(key=d), A(key=a), B(key=b), C(key=c)]
  React matches by key: a=a, b=b, c=c, d is new
  Result: A, B, C are MOVED, D is created
  CORRECT: each component keeps its state
```

---

### 🧪 Thought Experiment

**THE FORM STATE BUG:**
An app shows either a shipping form or a billing form
based on a toggle. Both are `<AddressForm>` components.
The user fills in the shipping form. They accidentally
toggle to billing. They toggle back.

Without keys (both forms at the same position in the tree,
same type): React reconciles them as the same component,
preserving the shipping form's state in the billing form
position. When the user toggles back, the shipping form
shows the billing form's data - or the user's shipping
entry was silently preserved in the billing form.

With distinct keys:

```jsx
{
  showShipping ? (
    <AddressForm key="shipping" formType="shipping" />
  ) : (
    <AddressForm key="billing" formType="billing" />
  );
}
```

Different keys force React to unmount shipping form and
mount a fresh billing form. State is correctly isolated.

This is a production bug that is subtle and hard to
reproduce - the root cause is always reconciliation and
keys.

---

### 🧠 Mental Model / Analogy

> Reconciliation is like a spot-the-difference game.
> React holds two photographs (old VDOM, new VDOM).
> Instead of comparing pixel-by-pixel (O(n^2)), React
> uses shortcuts: (1) If the frame of a picture changed
> (element type changed), tear out the entire picture
> and replace it - there is no point comparing what is
> inside. (2) Each picture in a gallery has a label (key).
> If a picture moves to a different hook, its label moves
> with it - React tracks it by label, not by hook position.
>
> Without labels: moving pictures in a gallery means
> updating the content of each hook in place. With labels:
> React moves the physical picture to the new hook.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
React compares old and new virtual DOM trees. Same type
= update. Different type = replace (and lose state).
`key` prop identifies list items - same key = same
component (state preserved), even if position changes.

**Level 2 (usage):**
Always use stable data IDs as keys (not array index).
Avoid changing element types conditionally at the same
position (use CSS or conditional rendering that preserves
type). Understand that type change = unmount/mount = state
loss.

**Level 3 (heuristics):**
The algorithm is O(n) because it is not comparing all
possible subtree matchings (that would be O(n^3)). It
makes two assumptions about React UIs that are almost
always true: (1) you rarely move an element to a completely
different level of the tree, (2) keys uniquely identify
list elements.

**Level 4 (Fiber):**
React 16 replaced the "Stack reconciler" with the "Fiber
reconciler." Fiber represents each element as a linked-
list node (Fiber node). This enables time-slicing: the
reconciliation can be interrupted between Fiber nodes
and resumed later (React 18 Concurrent Mode). The algorithm
is the same, but the execution model changed from recursive
(blocking) to iterative (interruptible).

**Level 5 (mastery):**
Reconciliation has two phases: (1) Render phase - creates
the new Fiber tree, diffs with old tree, marks nodes as
insert/update/delete (this phase is pure/interruptible
in Concurrent Mode). (2) Commit phase - applies the marked
changes to the actual DOM (this phase is always synchronous
and cannot be interrupted). Understanding this split
explains: why React.memo works (skips render phase for
the component), why Error Boundaries work (intercept
render phase errors), and why `useLayoutEffect` runs
after the commit phase (DOM is already updated).

---

### ⚙️ How It Works (Mechanism)

**The commit phase operations:**

```
After diffing, each Fiber node is tagged:

Placement  → appendChild to DOM
Update     → update DOM node attributes/properties
Deletion   → removeChild from DOM

Commit phase processes these in three passes:
  Pass 1 (before mutation): componentWillUnmount for deletions
  Pass 2 (mutation):        actual DOM operations
  Pass 3 (after mutation):  componentDidMount/Update, useLayoutEffect

useEffect fires asynchronously AFTER the commit phase
  (scheduled in a microtask / next tick)
useLayoutEffect fires synchronously in pass 3
  (fires before browser can paint)
```

**Key-based list reconciliation walkthrough:**

```jsx
// Before render (old tree):
// pos 0: <Task key="task-1" title="Buy groceries" />
// pos 1: <Task key="task-2" title="Call dentist" />
// pos 2: <Task key="task-3" title="Write report" />

// State change: insert new task at top
// New tree:
// pos 0: <Task key="task-4" title="New urgent task" />  ← new
// pos 1: <Task key="task-1" title="Buy groceries" />    ← moved
// pos 2: <Task key="task-2" title="Call dentist" />     ← moved
// pos 3: <Task key="task-3" title="Write report" />     ← moved

// Reconciliation (with keys):
// key "task-4": not in old tree → CREATE (Placement)
// key "task-1": was pos 0, now pos 1 → MOVE (no state loss)
// key "task-2": was pos 1, now pos 2 → MOVE (no state loss)
// key "task-3": was pos 2, now pos 3 → MOVE (no state loss)

// Without keys (index matching):
// pos 0: Update task-1 with task-4 data (task-1 state preserved, wrong data)
// pos 1: Update task-2 with task-1 data
// pos 2: Update task-3 with task-2 data
// pos 3: Create new element with task-3 data
// Each Task component is "updated" - all 4 are marked for Update
// State (checkboxes, expanded state) is NOT matched to the correct item
```

---

### 💻 Code Example

**BAD: Index as key causes state bugs:**

```jsx
// BAD: index as key causes reconciliation bugs
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        // Using index as key: React matches elements by position
        // Insert at top → all elements "update", state mismatches
        <TodoItem key={index} todo={todo} />
      ))}
    </ul>
  );
}

// Demonstrate the bug:
// todos = [A, B, C], index keys: A=0, B=1, C=2
// User checks the checkbox for A
// New todos = [D, A, B, C] (prepend D)
// React sees: key=0 (was A, now D), key=1 (was B, now A), etc.
// The checkbox state (for key=0) is now on D, not A
// WRONG: user's checkbox appears on the wrong item
```

**GOOD: Stable unique ID as key:**

```jsx
// GOOD: stable ID from data as key
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo) => (
        // key from todo.id: React matches element to ID
        // Prepend D → D is new (create), A/B/C are moved
        // Checkbox state follows the correct todo item
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </ul>
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "The key prop is just for suppressing React warnings"                  | The key prop fundamentally changes how reconciliation matches elements. Without it (or with index keys), prepending/inserting items causes the wrong component instances to receive the wrong data. This is a correctness bug, not a cosmetic warning.                                   |
| "Same type means the DOM node is exactly the same - no updates happen" | Same type means React keeps the DOM node (updates it rather than replacing it). React still diffs the attributes and children. If `className` changed, React updates the DOM node's class attribute. Reconciliation updates; it does not skip.                                           |
| "React's diff is O(n^2) because it compares every element"             | React's reconciliation is O(n) by design, using the two heuristics (type match + key match). It does NOT compare every old element with every new element. It traverses both trees simultaneously, comparing corresponding positions and key matches.                                    |
| "Using a random key (Math.random()) forces a fresh component"          | Yes, but it also re-mounts the component on every render (destroys all state, re-runs all effects). This is sometimes intentional (force reset) but usually a bug. Use a meaningful stable key, and if you need a reset, use a data-derived key that changes only when reset is desired. |

---

### 🚨 Failure Modes & Diagnosis

**Unexpected State Loss on Component Type Change**

**Symptom:** User fills in a form. A parent state change
causes the form to lose all entered data.

**Root Cause:** A conditional expression changes the
element type at the same position:

```jsx
// The input or div at position 0 changes type:
return condition ? <input value={text} /> : <div>{text}</div>;
// When condition flips: input unmounts (state lost), div mounts fresh
```

**Fix:** Keep the same type at the same position:

```jsx
return (
  <>
    {condition && <input value={text} />}
    {!condition && <div>{text}</div>}
  </>
);
// Both exist in the tree but one is hidden
// OR: use CSS visibility/display to show/hide without unmounting
```

---

**List Items Showing Wrong State After Prepend/Insert**

**Symptom:** Adding an item to the beginning of a list
causes checkboxes, expanded states, or inputs to appear
on the wrong items.

**Root Cause:** Index keys used for the list. React
matches items by position instead of identity.

**Diagnosis:** Check the `key` prop values. If they are
0, 1, 2 (or any index), that is the bug.

**Fix:** Use `item.id` or another unique stable identifier
as the key.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Virtual DOM and Reconciliation` - the VDOM model
  that reconciliation operates on
- `List Rendering and the key Prop` - the practical
  application of key-based reconciliation

**Builds On:**

- `React Fiber Architecture` - the Fiber reconciler that
  implements this algorithm with interruptibility
- `Concurrent Features` - how React 18 uses Fiber's
  interruptibility for priority-based rendering
- `React.memo` - optimisation that skips the render phase
  entirely for unchanged components

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TYPE MATCH  │ Same type: UPDATE in place (state kept)   │
│ TYPE CHANGE │ Different type: REPLACE (state LOST)      │
├──────────────────────────────────────────────────────────┤
│ KEY MATCH   │ Same key: same component (move if needed) │
│ KEY MISSING │ Match by position (wrong for dynamic list)│
│ KEY SOURCE  │ ALWAYS data ID, NEVER array index         │
├──────────────────────────────────────────────────────────┤
│ COMPLEXITY  │ O(n) via two heuristics                   │
│ PHASES      │ 1. Render (diffing, interruptible)        │
│             │ 2. Commit (DOM mutation, always sync)     │
├──────────────────────────────────────────────────────────┤
│ STATE LOSS  │ Type change at same position              │
│ WRONG STATE │ Index key with insert/delete              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Same element type = update in place (state preserved).
   Different type = unmount + remount (state LOST).
2. `key` prop tells reconciliation which item is which.
   Always use stable data IDs, never array index.
3. Two phases: render (diffing, can be interrupted) and
   commit (DOM mutation, always synchronous).

**Interview one-liner:**
"React reconciliation diffs old and new virtual DOM trees
in O(n) using two heuristics: (1) same element type =
update in place (state preserved), different type = replace
entire subtree (state lost); (2) key prop identifies list
items across renders - same key = same component instance
moved, ensuring state follows the correct item. Wrong or
index-based keys cause state to appear on the wrong items
after insert/prepend. React 16+ Fiber reconciler makes
this algorithm interruptible, enabling Concurrent Mode."

---

### 💎 Transferable Wisdom

React's O(n) diffing heuristics are an example of "domain-
specific optimisation" over "general algorithm." The
general tree diff is O(n^3). React's heuristics make it
O(n) by exploiting properties specific to UI trees: UI
elements rarely jump to completely different positions
in the tree, and lists of items have stable identities.
This pattern - "don't use the general algorithm; exploit
domain constraints" - appears throughout computer science:
specialised sorting algorithms (radix sort for integers
vs comparison sort), compilers that use SSA form for
specific optimisations, database query optimisers that
exploit index statistics. Understanding when you can
apply domain-specific heuristics is a senior engineering skill.

---

### 💡 The Surprising Truth

React's reconciliation algorithm is published in detail
in a paper Facebook researchers wrote in 2016 titled
"React's Diffing Algorithm" (in the React docs as
"Reconciliation"). The O(n^3) baseline comes from the
1979 paper by Tai and later Shasha/Zhang for exact tree
edit distance. React's O(n) is not a new algorithm - it
is a set of practical heuristics that make the O(n^3)
problem tractable for the specific case of UI trees. The
same approach was documented independently in the edit
distance literature as "restricted tree edit distance"
(only same-level matching). React's key insight was not
the algorithm but the observation: UI tree mutations
almost always respect level boundaries, so restricted
matching is correct in practice, even if not optimal in
theory.

---

### ✅ Mastery Checklist

1. **DEMONSTRATE** the state loss bug: a component with
   local state wrapped in a conditional that changes its
   type. Show state is lost on type change. Fix by keeping
   same type.
2. **DEMONSTRATE** the key prop state bug: a list with
   index keys where prepending an item causes state
   (checkbox/input) to appear on the wrong item. Fix
   with stable ID keys.
3. **EXPLAIN** to a colleague why React.memo is related
   to reconciliation: how does memoising a component's
   render skip reconciliation work for that component?
4. **TRACE** through the reconciliation for a specific
   list change (insert, delete, move) and determine which
   elements React will create, update, and delete.
5. **EXPLAIN** the difference between the render phase
   (interruptible) and commit phase (synchronous) and why
   `useLayoutEffect` runs in the commit phase while
   `useEffect` runs after it.

---

### 🧠 Think About This Before We Continue

**Q1.** React's heuristic says: "Different element types
produce different trees." But what if you have two different
components that happen to produce identical JSX output?
`ComponentA` and `ComponentB` both return `<div>Hello</div>`.
At the same position, transitioning from ComponentA to
ComponentB causes a full remount. Is this correct behaviour,
and can you think of a case where it causes a bug that
is hard to detect?

**Q2.** The reconciliation algorithm assumes list items
do not move across tree levels. In practice, drag-and-drop
UIs can move items to completely different positions.
How do UI libraries like `react-dnd` and `framer-motion`
handle dragging an item to a different level of the component
tree while preserving its state and identity?

**Q3.** Virtual DOM diffing is one approach to minimising
DOM mutations. Svelte compiles components to direct DOM
mutation code (no virtual DOM). SolidJS uses fine-grained
reactivity that updates only the specific DOM node that
changed. Angular uses a change detection mechanism.
For what class of React applications is virtual DOM
diffing a performance ADVANTAGE over fine-grained reactivity,
and for what class is it a disadvantage?
