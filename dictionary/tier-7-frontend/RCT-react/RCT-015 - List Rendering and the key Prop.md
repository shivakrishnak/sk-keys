---
id: RCT-015
title: List Rendering and the key Prop
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-008, RCT-009, RCT-011
used_by: RCT-030, RCT-037, RCT-041
related: RCT-014, RCT-011, RCT-038
tags:
  - react
  - frontend
  - lists
  - reconciliation
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /react/list-rendering-and-the-key-prop/
---

# RCT-015 - LIST RENDERING AND THE KEY PROP

⚡ TL;DR - React renders lists by mapping arrays to JSX
elements; every list item needs a unique, stable `key`
prop so React can identify which items changed, were added,
or removed - using index as key causes subtle bugs when
items reorder or the list changes.

| #015 | Category: React | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Component, JSX, Props, Virtual DOM | |
| **Used by:** | Form Handling, useReducer, Render Props Pattern | |
| **Related:** | Conditional Rendering, Virtual DOM, React Reconciliation | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT KEYS:**
React's Virtual DOM diffing compares previous and current
output trees to determine minimal DOM updates. For a list,
React needs to know: "This item moved to a new position"
vs "This item was deleted and a different item was added."
Without a way to identify items, React falls back to
positional comparison: item 0 maps to item 0, item 1 to
item 1. If you add an item to the beginning of the list,
React sees every position as "changed" and re-renders the
entire list - inefficient. Worse: if list items have local
state (a focused input, a partially filled form field),
React cannot know item identity has changed, so state
persists at the wrong position.

The `key` prop gives React a stable identity for each item,
enabling efficient reconciliation and correct state
association.

---

### 📘 Textbook Definition

**List rendering** in React converts an array of data to
an array of JSX elements using `.map()`. Each element in
the output array must have a `key` prop - a string or
number that is unique among siblings and stable (does not
change between renders unless the item itself changes).

The `key` prop is not passed to the component as a prop
(it is consumed by React internally). React uses keys
during reconciliation to match elements from the previous
tree to elements in the new tree, enabling it to reuse
DOM nodes for unchanged items, update DOM nodes for
changed items, and add/remove DOM nodes for added/removed
items.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Use `.map()` to render arrays, and give every element a
`key` prop set to a unique, stable identifier from your
data (database ID, not array index).

**One trap:**
> Using array index as `key` (the "it works" shortcut)
> causes incorrect behaviour when items reorder or are
> inserted/deleted. Index 0 always refers to "first item
> in DOM position", not "the specific item with this
> identity." If the item at index 0 changes, React
> UPDATES the existing DOM node rather than SWAPPING it.
> This causes input focus bugs, animation glitches, and
> wrong state.

---

### 🔩 First Principles Explanation

**HOW REACT USES KEYS:**

```
Without keys (positional comparison):
Previous: [A, B, C]
Current:  [X, A, B, C]  (X prepended)

React compares by position:
  pos 0: A → X (different, UPDATE A's DOM node to X)
  pos 1: B → A (different, UPDATE B's DOM node to A)
  pos 2: C → B (different, UPDATE C's DOM node to B)
  pos 3: (nothing) → C (ADD new DOM node for C)
Result: 3 updates + 1 insert (all DOM nodes touched)
```

```
With stable keys:
Previous: [{key:"a",val:A}, {key:"b",val:B}, {key:"c",val:C}]
Current:  [{key:"x",val:X}, {key:"a",val:A}, ... ]

React matches by key:
  key "a": same (exists in both), KEEP DOM node
  key "b": same (exists in both), KEEP DOM node
  key "c": same (exists in both), KEEP DOM node
  key "x": new (not in previous), ADD DOM node
Result: 0 updates + 1 insert (only new node added)
```

**WHY INDEX KEYS FAIL:**

```
Items: [{id:1, text:"Buy milk"}, {id:2, text:"Call Alice"}]
User deletes item 1 (id:1).
New list: [{id:2, text:"Call Alice"}]

With index keys:
  pos 0 = id:2, "Call Alice"
  But React still sees key=0 at position 0
  It maps "Call Alice" onto the DOM node that
  previously had "Buy milk" and UPDATES it
  The DOM node for index 0 keeps its state
  (input focus, checked state, etc.) but with
  different content - incorrect behaviour.

With id keys:
  key "2" is still present, React keeps its DOM node
  key "1" is gone, React removes its DOM node
  Correct: the "Call Alice" node is untouched
```

---

### 🧪 Thought Experiment

**THE FOCUSED INPUT BUG:**

A todo list renders inputs. Each input has a `key` set to
index. The user focuses the second input (index 1) and
starts typing. Another user or automatic update deletes
the first todo. Now the list is:

- Index 0: what was the second todo
- Index 1: what was the third todo

React sees key=1 still at index 1 and keeps that DOM node.
The user's focused, partially-typed input is now associated
with a different todo item. Their text is in the wrong
field. This is the exact bug that index keys cause.

---

### 🧠 Mental Model / Analogy

> `key` is a name tag at a conference. Without name tags,
> if you rearrange the seats, the person sitting in seat 5
> IS seat 5 - identity is positional. With name tags, each
> person has identity regardless of seat. When React needs
> to find "Alice", it looks for the name tag "Alice", not
> "whoever is in seat 3."

```
Array data:
[{id: 101, name: "Alice"}, {id: 102, name: "Bob"}]
         │                         │
         key="101"                 key="102"
         │                         │
         v                         v
<li key="101">Alice</li>  <li key="102">Bob</li>

If Bob moves to position 0:
React finds key="102" (Bob) - SAME DOM NODE, repositioned
React finds key="101" (Alice) - SAME DOM NODE, repositioned
No updates needed - React reuses both nodes.
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
When showing a list of items in React, use `.map()` to
convert each item to JSX. React requires a `key` prop
on each item. Use the item's unique ID as the key.

**Level 2 (usage):**
`key` must be unique among siblings, not globally unique.
It must be a string or number. Do not use index except
for static, never-reordered lists. The `key` prop is not
accessible in the component (it does not appear in
`props.key`). If you need to pass the key value to the
component, pass it separately as another prop.

**Level 3 (mechanism):**
React's reconciler uses keys in the diffing algorithm.
During reconciliation, React creates a map of keys to
elements in the previous render. For the next render, it
looks up each element's key in the map. If found: update
that existing DOM node. If not found: create a new DOM
node. If a previous key is absent in the new render:
remove that DOM node. This is O(n) matching instead of
O(n^2) naive comparison.

**Level 4 (architecture):**
Keys affect component lifecycle. Changing a key unmounts
the old component and mounts a fresh one. This is a
pattern: `<Form key={selectedItemId} />` resets the form
completely when `selectedItemId` changes. Without the key
change, the form component is the same instance and keeps
its state even when the selected item changes.

**Level 5 (mastery):**
Key stability interacts with animation libraries.
Framer Motion and react-spring use keys to identify
entering/exiting elements for transitions. A key change
signals "this element is exiting" and triggers the exit
animation before unmounting. Using `AnimatePresence`
requires correct keys to distinguish "item is being
replaced" from "item is being updated." At this level, the
key is not just a performance hint - it is the semantic
identity of the element in the animation graph.

---

### ⚙️ How It Works (Mechanism)

**Basic list render:**

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

**List with components as items:**

```jsx
function TodoList({ todos, onDelete }) {
  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}      // React identity
          id={todo.id}       // pass as separate prop if needed
          text={todo.text}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
```

**Conditional list items:**

```jsx
function FilteredList({ items, showCompleted }) {
  const visible = showCompleted
    ? items
    : items.filter(item => !item.completed);

  return (
    <ul>
      {visible.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
// Keys from item.id remain stable even as the filtered
// list changes - React correctly adds/removes items
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ITEM DELETION RECONCILIATION:**

```
1. State: [{id:1,text:"Buy milk"},{id:2,text:"Call Alice"}]
2. User clicks "Delete" on id:1
3. setTodos(todos.filter(t => t.id !== 1))
4. React schedules re-render
5. New output:
     <li key="2">Call Alice</li>
   Previous output:
     <li key="1">Buy milk</li>
     <li key="2">Call Alice</li>
6. Reconciler: key "1" missing → REMOVE that DOM node
7. Reconciler: key "2" present → KEEP that DOM node
8. DOM: only 1 DOM operation (remove the first li)
9. "Call Alice" li is untouched, preserves its state
```

---

### 💻 Code Example

**BAD: Index as key - causes identity bugs:**

```jsx
// BAD: using index as key
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        // Key is positional, not item-based
        <li key={index}>
          <input defaultValue={todo.text} />
        </li>
      ))}
    </ul>
  );
}
// Bug: Delete todo at position 0.
// React sees key=0 at position 0 still exists.
// The DOM node for index 0 is kept (with its input state).
// The wrong input now displays text from the next item.
// Any focused inputs shift to wrong items.
```

**GOOD: Stable ID as key:**

```jsx
// GOOD: using stable database ID as key
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          {/* Controlled input: state in component */}
          <TodoInput
            key={todo.id}
            initialText={todo.text}
            todoId={todo.id}
          />
        </li>
      ))}
    </ul>
  );
}
// Correct: When todo id:1 is deleted, React removes
// exactly that DOM node. id:2's input state is untouched.
```

**PRODUCTION: Key pattern for force-remount:**

```jsx
// Pattern: force reset by changing key
// Useful when form should fully reset on selected item change
function ItemEditor({ selectedItemId, items }) {
  const item = items.find(i => i.id === selectedItemId);

  return (
    // key change unmounts old form, mounts fresh one
    // No manual "reset form to empty" logic needed
    <EditForm key={selectedItemId} initialData={item} />
  );
}
```

**FAILURE: Generated keys break reconciliation:**

```jsx
// BAD: Math.random() as key
{todos.map(todo => (
  <TodoItem key={Math.random()} todo={todo} />
))}
// Every render generates new keys
// React sees ALL items as new every render
// Unmounts and remounts every list item on every state change
// Performance disaster + all item state is lost every render
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Index keys are fine if the list never changes" | Acceptable only for truly static lists that never reorder, add, or remove items. If there is any chance of mutation, use a stable ID. |
| "key must be unique across the entire page" | Keys must be unique among SIBLINGS only. The same key value can be used in different list renders without conflict. |
| "`key` is accessible as `props.key` in the component" | `key` is consumed by React and NOT passed to the component as a prop. If you need the ID inside the component, pass it as a separate prop: `<Item key={item.id} id={item.id} />`. |
| "Adding a key to JSX requires using data arrays" | The `key` prop is relevant anywhere you return multiple sibling elements from a loop or condition. But you only need keys when rendering arrays - individual static siblings do not need keys. |

---

### 🚨 Failure Modes & Diagnosis

**Input Focus Shifts After Deletion**

**Symptom:** Deleting one todo causes another todo's input
to gain unexpected content or state.

**Root Cause:** Index-based keys. React reuses DOM nodes
at the same position rather than matching by item identity.

**Fix:** Use item's database `id` or another stable unique
identifier as the key.

---

**All List Items Re-render on Every Update**

**Symptom:** React DevTools Profiler shows every list item
highlighted on every state change, even items that did
not change.

**Root Cause:** `key={Math.random()}` or any unstable key.
React treats every item as new every render.

**Fix:** Use stable keys. Combine with `React.memo` on the
item component to skip re-renders for unchanged items.

---

**Key Conflict Warning in Console**

**Symptom:**
`Warning: Encountered two children with the same key`

**Root Cause:** Duplicate values in the key field. Common
when IDs are not truly unique (two API sources merged, or
string/number type mismatch producing "1" and 1 as separate
items that display as duplicates).

**Fix:** Ensure key values are unique among siblings.
Prefix keys from different sources: `key={source + '-' + id}`.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Component` and `JSX` - list rendering produces JSX
- `Props` - `key` is a special prop
- `Virtual DOM` - keys enable efficient Virtual DOM diffing

**Builds On:**
- `React Reconciliation Algorithm` - the full algorithm
  that uses keys as identity hints
- `useReducer` - often used to manage complex list state
  (add/delete/update operations on arrays)
- `React.memo` - combine with stable keys to prevent
  list items from re-rendering when unchanged

**Related Concepts:**
- `Conditional Rendering` - often combined with list
  rendering (show empty state when list is empty)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RENDER LIST │ items.map(item => <El key={item.id} />)  │
├──────────────────────────────────────────────────────────┤
│ KEY RULES   │ Unique among siblings (not global)       │
│             │ Stable across renders (not random/index) │
│             │ String or number                         │
│             │ NOT accessible as props.key              │
├──────────────────────────────────────────────────────────┤
│ USE INDEX   │ Only if: static list, never reorders,    │
│ AS KEY      │ no add/remove, no item local state       │
├──────────────────────────────────────────────────────────┤
│ KEY TRAP    │ key={Math.random()} = remounts every item │
│             │ key={index} = wrong identity on mutation  │
├──────────────────────────────────────────────────────────┤
│ FORCE RESET │ key={selectedId} on component to fully  │
│ PATTERN     │ remount when selection changes           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use `.map()` for arrays; every mapped element needs a
   `key` prop set to a unique, stable ID from your data.
2. Never use `Math.random()` or array index as key (except
   truly static lists). Index keys cause wrong state on
   insertion/deletion/reorder.
3. Changing a component's `key` is how you force a full
   remount and state reset - a useful pattern when a form
   should reset to a fresh state.

**Interview one-liner:**
"React list rendering uses `.map()` to produce arrays of
JSX elements. Each element needs a `key` prop - a unique,
stable identifier (usually database ID) - so React's
reconciler can match elements between renders for efficient
DOM updates and correct state association. Index keys cause
bugs when lists mutate because index 0 always means
'first position', not 'the specific item.' The key prop
is also used intentionally to force component remounts."

---

### 💎 Transferable Wisdom

The `key` problem is fundamentally about **stable identity
in mutable sequences**. This pattern appears everywhere:
- Database rows have primary keys for stable identity
- React list items need `key` props
- HTTP caches use URL as stable key
- Redux store keys for normalised data (entities indexed by ID)
- CSS transitions need stable element identity to animate correctly

The principle: when you have a sequence that can mutate,
explicitly associate each member with a stable identifier
that survives positional changes. React's `key` is a
specific application of this universal principle.

---

### 💡 The Surprising Truth

React intentionally does NOT pass `key` to the component
as a prop - not because of an oversight, but because `key`
is a framework-level implementation detail. If you could
read `props.key`, you might write code that depends on
the key value for business logic, making the key serve
two purposes (framework identity + business data) and
creating coupling between the framework and your component.
The deliberate inaccessibility forces clean separation:
`key` is for React's reconciler only. If you need the
ID value inside the component, pass it twice:
`<Item key={item.id} id={item.id} />`.

---

### ✅ Mastery Checklist

1. **EXPLAIN** why `key={index}` is correct for a
   alphabetically-sorted static dropdown but incorrect
   for a user-reorderable todo list.
2. **DEBUG** a bug where deleting a list item causes an
   adjacent text input to lose its typed content, and
   trace it to the key strategy being used.
3. **APPLY** the force-remount pattern: use a `key` prop
   to cause a form to fully reset when the user selects
   a different item from a list, without writing any
   explicit reset logic.
4. **DIAGNOSE** "Warning: Encountered two children with
   the same key" - identify root causes (type coercion,
   duplicate IDs from merged sources) and apply fixes.
5. **OPTIMISE** a list render: combine stable `key` props
   with `React.memo` on the item component to prevent all
   items from re-rendering when only one item changes.

---

### 🧠 Think About This Before We Continue

**Q1.** React's reconciliation uses keys to match elements
between renders. What happens when you wrap a list in
`<React.Fragment key={groupId}>` and each fragment contains
multiple items? Does the key on the Fragment protect
item state inside it, or does each item inside still need
its own key?

**Q2.** A filtered list: the user has items [A, B, C, D]
with IDs 1, 2, 3, 4. A search filter shows [B, D] (IDs
2, 4). The user types in B's input field. The search is
cleared - all items [A, B, C, D] show again. With ID keys,
does B's input retain what was typed? With index keys,
what happens?

**Q3.** The force-remount pattern (`key={selectedId}`)
causes the entire subtree to unmount and remount. This
runs all cleanup effects and setup effects. For a complex
form with dozens of fields, several API calls in effects,
and expensive rendering, is the force-remount pattern
always the right choice? What is the alternative, and
when is it better?