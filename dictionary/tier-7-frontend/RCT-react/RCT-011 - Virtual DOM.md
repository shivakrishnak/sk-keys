---
id: RCT-011
title: Virtual DOM
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-003, RCT-007, RCT-008
used_by: RCT-012, RCT-015, RCT-039, RCT-052, RCT-053
related: RCT-039, RCT-052, RCT-073
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
nav_order: 11
permalink: /react/virtual-dom/
---

# RCT-011 - VIRTUAL DOM

⚡ TL;DR - The virtual DOM is a lightweight JavaScript
object tree that React maintains as a representation of
the real DOM; diffing the virtual tree before touching
the real DOM makes updates efficient and the declarative
model practical.

| #011            | Category: React                                                                                               | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Declarative UI vs Imperative DOM, Component, JSX                                                              |                 |
| **Used by:**    | ReactDOM Rendering, List Rendering and the key Prop, React Reconciliation Algorithm, React Fiber Architecture |                 |
| **Related:**    | React Reconciliation Algorithm, React Fiber Architecture, Virtual DOM Comparison Survey                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The real DOM is slow to modify directly. Accessing a DOM
property (`element.offsetWidth`) triggers a layout
calculation - this can cause "layout thrashing" when reads
and writes are interleaved. Every `appendChild`, `removeChild`,
or `setAttribute` call is expensive compared to plain
JavaScript operations on objects.

More critically: if React re-rendered the entire UI on every
state change by clearing the DOM and rebuilding from scratch,
form inputs would lose focus, animations would reset, scroll
positions would jump, and iframes would reload. This is
practically unusable.

**THE CORE PROBLEM:**
Declarative rendering means React must recompute the entire
component tree on every state change. Directly applying this
to the real DOM would be catastrophic for performance and
user experience. A strategy is needed to: (1) compute the new
desired UI cheaply, (2) determine what has actually changed,
(3) make only the minimum necessary DOM mutations.

**THE SOLUTION:**
The virtual DOM is that strategy. React maintains a lightweight
JavaScript object representation of the DOM tree. On state
change, it computes a new virtual tree (cheap - just JS
objects), diffs the new tree against the previous tree,
and applies only the necessary changes to the real DOM.

---

### 📘 Textbook Definition

The **virtual DOM** (vDOM) is an in-memory representation of
the UI maintained by React as a tree of plain JavaScript
objects. Each node in the virtual DOM corresponds to a DOM
element or text node and contains the element's type, its
props, and its children. When a React component re-renders,
React creates a new virtual DOM tree and runs a **diffing
algorithm** (reconciliation) to compare it with the previous
tree. Only the differences (patches) are applied to the real
DOM. This minimises direct DOM manipulation and keeps the
declarative rendering model performant.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The virtual DOM is a JavaScript copy of the real DOM that
React diffs before touching actual DOM nodes - like preparing
edits on a draft before publishing.

**One analogy:**

> The virtual DOM is like a recipe draft. When you want to
> change a recipe, you write out the full new version on a
> blank piece of paper, compare it to the current printed
> recipe, mark only the changed lines, and update only those
> lines in the printed version. You do not reprint the entire
> recipe every time you fix a typo. React does the same:
> it writes the full new UI as a virtual tree, diffs it
> against the current tree, and only updates the real DOM
> for what changed.

**One insight:**
The virtual DOM is a performance optimisation, not a
correctness requirement. React could work without it - it
just would not be practical for most applications. The
virtual DOM is what makes "re-render on every state change"
efficient enough to be the default model.

---

### 🔩 First Principles Explanation

**WHAT A VIRTUAL DOM NODE LOOKS LIKE:**

```javascript
// This JSX:
<div className="card">
  <h2>{user.name}</h2>
</div>

// Becomes this React element (virtual DOM node):
{
  type: 'div',
  props: {
    className: 'card',
    children: {
      type: 'h2',
      props: {
        children: user.name  // e.g., "Alice"
      }
    }
  }
}
```

This is just a plain JavaScript object. Creating it is
thousands of times cheaper than creating a real DOM element.
Reading it involves no layout calculations. Comparing two
of them is a simple property comparison.

**WHY DIFFING WORKS:**
The virtual DOM diff algorithm uses heuristics to achieve
O(n) complexity (rather than the theoretical O(n³) for
general tree diffing):

1. Elements of different types are always different trees
   (no subtree comparison needed)
2. Keys identify stable elements across list re-orderings
3. Same type, same position = update (not recreate)

**THE TRADE-OFF:**
The virtual DOM adds memory overhead (two copies of the
tree: current + previous) and CPU overhead (diffing).
For simple static pages, this overhead is worse than
direct DOM manipulation. For complex interactive UIs with
many state changes, the batched minimal-diff approach is
more efficient than naive full re-renders.

---

### 🧪 Thought Experiment

**SETUP:**
A list of 1000 items. One item's text changes.

**WITHOUT VIRTUAL DOM:**
If React re-rendered by clearing and rebuilding:

- All 1000 DOM nodes destroyed
- All 1000 DOM nodes recreated
- Browser repaints entire list area
- Any focused element loses focus
- Scroll position may jump

**WITH VIRTUAL DOM:**

- React computes new virtual DOM tree (JS objects - cheap)
- Diff against previous virtual tree
- Finds: only item 42's text content changed
- Applies one DOM mutation: `textNode.nodeValue = newText`
- Browser repaints only the affected text region
- Focused elements untouched
- Scroll position unchanged

The virtual DOM makes "redeclare the entire UI" equivalent
to "compute the minimal diff and apply it."

---

### 🧠 Mental Model / Analogy

> The virtual DOM is a double-buffer render technique.
> In graphics programming, you render to an off-screen
> buffer (cheap), then swap the buffer to the screen
> (fast). You never flicker the display with partial renders.
> React's virtual DOM is the off-screen buffer: compute the
> full next frame in JS (cheap), compare with current frame,
> swap only what changed to the real DOM (minimal).

```
React internal state:
  currentVDOM = { div: { children: "Alice" } }

State change: name = "Bob"

New render:
  nextVDOM = { div: { children: "Bob" } }

Diff:
  currentVDOM vs nextVDOM
  -> text child changed: "Alice" -> "Bob"

Commit:
  realDOM.textNode.nodeValue = "Bob"  <- only this one op

Update internal:
  currentVDOM = nextVDOM
```

Where this model breaks: with React Fiber (Concurrent mode),
the "double buffer" metaphor is more accurate than before.
React maintains two trees: current (displayed) and workInProgress
(being rendered). In concurrent mode, the workInProgress
tree can be discarded if a higher-priority update arrives.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
React keeps a lightweight copy of the page structure in
memory. When your data changes, React updates this copy
first, figures out what changed, and only makes the minimum
changes to the actual page. This makes updates fast.

**Level 2 - How to use it (junior developer):**
You do not use the virtual DOM directly - React manages it
automatically. What you need to understand: when you update
state, React re-runs your component to produce a new virtual
DOM tree. It diffs this with the previous tree. Only DOM
operations for the differences are applied. The `key` prop
on list items helps React match elements across re-renders.

**Level 3 - How it works (mid-level engineer):**
React's reconciliation algorithm compares the new virtual
DOM tree against the saved previous tree. For each node:
if same type at same position, update props in place;
if different type or missing, unmount the old, mount the new.
Keys identify stable elements in lists - same key = same
instance, update props; missing key = unmount; new key = mount.

**Level 4 - Why it was designed this way (senior/staff):**
The virtual DOM was a pragmatic design choice in 2013 - it
enabled the declarative "re-render everything" model without
the performance cost of actually rebuilding the DOM on every
change. Later alternatives (Svelte's compile-time reactivity,
Solid's fine-grained signals) achieve similar or better
performance without a virtual DOM. React itself is moving
toward a model (React Forget / React Compiler) that avoids
virtual DOM diffing overhead through compile-time memoisation.

**Level 5 - Mastery (distinguished engineer):**
The virtual DOM is not inherently faster than direct DOM
manipulation. Its advantage is that it enables automatic
batching and minimal-diff updates without the developer
needing to manually track what changed. At large scale,
the overhead of reconciliation becomes measurable. React's
Fiber architecture rewritten the reconciler to support
Concurrent rendering, where work is split into interruptible
units - enabling React to pause reconciliation for high-
priority updates (user input) and resume lower-priority
work (list loading) asynchronously.

---

### ⚙️ How It Works (Mechanism)

**Reconciliation process:**

```
STATE CHANGE TRIGGER:
  setName("Bob")

RENDER PHASE (creates new virtual DOM - no DOM ops):
  React calls Component({ name: "Bob" })
  -> returns new virtual DOM tree:
     { type: 'div', props: { children: "Bob" } }

DIFF PHASE:
  Compare new tree vs currentVDOM:
  currentVDOM: { type: 'div', props: { children: "Alice" } }
  newVDOM:     { type: 'div', props: { children: "Bob" } }

  node at root: same type 'div', same position -> update
  child: text "Alice" -> "Bob" -> text node mutation needed

COMMIT PHASE (applies DOM mutations):
  realDOM.textNode.nodeValue = "Bob"

UPDATE INTERNAL STATE:
  currentVDOM = newVDOM
```

**The diffing heuristics:**

```
Heuristic 1: Type change = full subtree replace
  currentVDOM: <div>...</div>
  newVDOM:     <span>...</span>
  -> Unmount div + all children, mount span + children
  -> State of children is LOST

Heuristic 2: Same type = update props in place
  currentVDOM: <div className="old" />
  newVDOM:     <div className="new" />
  -> Update className attribute only
  -> Child state PRESERVED

Heuristic 3: Lists - keys identify stable instances
  currentVDOM: [<Item key="a"/>, <Item key="b"/>]
  newVDOM:     [<Item key="b"/>, <Item key="a"/>]
  -> React matches by key: no unmount/remount
  -> Reorder DOM nodes only
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL RENDER CYCLE:**

```
┌────────────────────────────────────────────────────────┐
│ 1. USER ACTION: setState() called                     │
├────────────────────────────────────────────────────────┤
│ 2. RENDER PHASE (interruptible in Concurrent Mode)    │
│    React calls component functions                    │
│    Builds new virtual DOM tree (JS objects)           │
│    No DOM touched in this phase                       │
├────────────────────────────────────────────────────────┤
│ 3. RECONCILIATION (diffing)                           │
│    Compare new vDOM vs current vDOM                   │
│    Build "effects list" (what needs to change in DOM) │
├────────────────────────────────────────────────────────┤
│ 4. COMMIT PHASE (synchronous, not interruptible)      │
│    Apply DOM mutations from effects list              │
│    Run layout effects (useLayoutEffect)               │
│    Update refs                                        │
├────────────────────────────────────────────────────────┤
│ 5. PASSIVE EFFECTS                                    │
│    Run useEffect callbacks (async, after paint)       │
└────────────────────────────────────────────────────────┘
```

The Render and Reconciliation phases are interruptible in
Concurrent React (can be paused for higher-priority work).
The Commit phase is always synchronous (DOM must be updated
as an atomic operation to avoid visual inconsistencies).

---

### 💻 Code Example

**Example 1 - BAD: Forcing full remounts unnecessarily:**

```jsx
// BAD: creates a new component type on every parent render
// (component defined inside component body)
function Parent({ items }) {
  // New function reference every render = new type
  function ListItem({ item }) {
    return <li>{item.name}</li>;
  }

  return (
    <ul>
      {items.map((item) => (
        <ListItem key={item.id} item={item} />
      ))}
    </ul>
  );
}
// Every Parent re-render:
// React sees new type at each list position
// -> Unmount all existing ListItems
// -> Mount all new ListItems
// -> All child state lost, all DOM recreated
// This defeats the virtual DOM's minimal-diff benefit
```

**Example 2 - GOOD: Stable component identity:**

```jsx
// GOOD: component defined at module level - stable identity
function ListItem({ item }) {
  return <li>{item.name}</li>;
}

function Parent({ items }) {
  return (
    <ul>
      {items.map((item) => (
        <ListItem key={item.id} item={item} />
      ))}
    </ul>
  );
}
// Same type at each position across renders
// -> React updates props in place (minimal diff)
// -> No unmount/remount unless key changes
```

**Example 3 - PRODUCTION: Understanding key-based remounting:**

```jsx
// DELIBERATE remount using key:
// When userId changes, reset all component state
function UserProfile({ userId }) {
  return (
    <ProfileForm
      key={userId} // <- changing key forces full remount
      userId={userId}
    />
  );
}
// ProfileForm has complex internal state (form fields,
// validation, editing mode). When userId changes, we WANT
// to reset all that state. Using key={userId} tells React
// "this is a NEW instance when userId changes" -> full
// unmount + remount -> all state reset to initial.
// This is a DELIBERATE use of virtual DOM remount semantics.
```

---

### ⚖️ Comparison Table

| Approach             | Virtual DOM (React)                   | No vDOM - Compile-time (Svelte)     | Fine-grained Signals (SolidJS)           |
| -------------------- | ------------------------------------- | ----------------------------------- | ---------------------------------------- |
| **Update strategy**  | Diff JS trees, apply patch            | Compiled surgically precise DOM ops | Signals update only subscribed DOM nodes |
| **Runtime overhead** | Medium (diffing cost)                 | Minimal (no diffing)                | Very low (signal subscriptions)          |
| **Bundle size**      | Larger (reconciler included)          | Smaller (no runtime)                | Small (signals runtime)                  |
| **Mental model**     | Declarative, re-render-based          | Declarative, compiled               | Reactive signals                         |
| **Best for**         | Complex dynamic UIs (React ecosystem) | Small-to-medium apps, performance   | High-frequency updates                   |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Virtual DOM makes React the fastest framework"             | Virtual DOM is a performance strategy but not the fastest possible approach. Compile-time frameworks (Svelte) and fine-grained reactivity (SolidJS) can be significantly faster because they eliminate the diffing step entirely. React's virtual DOM is "fast enough" for most applications. |
| "React re-renders the whole DOM"                            | React re-renders components (calls functions, produces virtual DOM). The real DOM is only touched where the diff finds changes. A component re-rendering does not mean its DOM subtree is recreated.                                                                                          |
| "The virtual DOM is always in sync with the real DOM"       | The virtual DOM reflects what React last committed. If you manually mutate the real DOM via refs or imperative code, the virtual DOM becomes stale and subsequent diffs produce incorrect patches.                                                                                            |
| "Skipping re-renders (React.memo) bypasses the virtual DOM" | React.memo skips the RENDER phase (calling the function) for a component if its props have not changed. Without a new render, there is no new virtual DOM to diff. React.memo is a way to reduce reconciliation work, not to bypass the virtual DOM mechanism.                                |

---

### 🚨 Failure Modes & Diagnosis

**Missing Keys Causing Full Remounts on List Changes**

**Symptom:**
A list of form inputs loses their values when the list is
reordered or an item is prepended. Animations on list items
restart. Performance profiler shows large numbers of
unmounts and mounts on list updates.

**Root Cause:**
List items render without `key` props (or with unstable keys
like array indices). React cannot match items across
re-renders by identity, so it uses position matching.
When items move, same-position matching causes incorrect
diffs.

**Diagnostic Command:**

```bash
# React DevTools will warn in the console:
# "Warning: Each child in a list should have a unique 'key' prop."
# In the Profiler, items that should update but show
# as mount/unmount cycles have missing or unstable keys.
```

**Fix:**
Use stable, unique IDs as keys: `key={item.id}`. Never
use array indices (`key={index}`) for lists that can be
reordered, filtered, or prepended.

---

**Manual DOM Mutation Desynchronising the vDOM**

**Symptom:**
After a user interaction that involves both a ref-based
DOM mutation and a state update, the UI shows an
incorrect combination of old and new values.

**Root Cause:**
A `useRef` was used to mutate a DOM node's content or
attributes directly. React's virtual DOM still shows the
old value. On the next state-driven re-render, React diffs
against the stale virtual DOM and produces a patch that
overwrites the manual change with the old value.

**Fix:**
Drive all visible state changes through React state.
Use `useRef` only for: accessing DOM measurements
(getBoundingClientRect), managing focus, and integrating
third-party libraries that control their own DOM subtree.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Declarative UI vs Imperative DOM Manipulation` - why
  the virtual DOM exists as the implementation of the
  declarative model
- `Component` and `JSX` - what produces the virtual DOM
  nodes

**Builds On This (learn these next):**

- `React Reconciliation Algorithm` - the diffing algorithm
  in detail
- `List Rendering and the key Prop` - how keys guide the
  diffing algorithm for lists
- `React Fiber Architecture` - the work unit that makes
  Concurrent rendering possible

**Alternatives / Comparisons:**

- `Svelte (no vDOM)` - compile-time approach that generates
  targeted DOM mutations without a runtime virtual DOM
- `SolidJS (signals)` - fine-grained reactive model where
  individual DOM nodes subscribe to signals and update
  without any diffing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ JS object tree representation of the UI │
│              │ used to compute minimal DOM mutations    │
├──────────────┼───────────────────────────────────────────┤
│ HOW IT HELPS │ Enables declarative "re-render all"     │
│              │ without actually touching full DOM       │
├──────────────┼───────────────────────────────────────────┤
│ PHASES       │ Render (vDOM) -> Reconcile (diff)       │
│              │ -> Commit (real DOM mutations)           │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Keys in lists = stable element identity │
│              │ Missing keys = position-based matching  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ Direct DOM mutations via refs that React │
│              │ does not know about                     │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Unstable keys (array indices for        │
│              │ reorderable lists)                      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Convenient minimal-diff updates vs      │
│              │ diffing overhead (vs Svelte/SolidJS)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JS copy of the DOM; React diffs it     │
│              │  before touching real DOM nodes."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reconciliation Algorithm -> Fiber       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The virtual DOM is a JavaScript object tree. Creating
   and diffing JS objects is cheap; mutating the real DOM
   is expensive. The vDOM enables "compute desired UI, apply
   only what changed" instead of "rebuild everything."
2. The virtual DOM is NOT the fastest possible approach.
   Svelte (compile-time) and SolidJS (signals) are faster.
   React's vDOM is "fast enough" with good development
   ergonomics.
3. Manual DOM mutations via `useRef` desynchronise the
   virtual DOM. React's next diff will produce incorrect
   patches because it diffs against a stale vDOM snapshot.

**Interview one-liner:**
"The virtual DOM is a lightweight JavaScript object tree
that React maintains as a representation of the real DOM.
When state changes, React re-renders components to produce
a new virtual tree, diffs it against the previous snapshot
using a heuristic O(n) algorithm, and applies only the
minimum necessary DOM mutations. This makes the declarative
're-render everything' model practical and avoids full DOM
rebuilds on every state change."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When synchronising two representations of the same data
(virtual DOM and real DOM, or cache and database), maintaining
a "current snapshot" and computing diffs is more efficient
than always replacing the full current state - provided the
diff computation is cheaper than full replacement. This
pattern appears in many systems: git diff, CRDT merging,
database replication.

**Where else this pattern appears:**

- Git - computes diffs between commits; stores only deltas
  not full file copies for most operations
- React Native - virtual DOM translates to native widget
  mutations on iOS/Android instead of DOM mutations
- Database replication (CDC) - computes changes (diff) and
  applies only those to the replica

---

### 💡 The Surprising Truth

The virtual DOM was not invented by Facebook. The concept
of maintaining a lightweight in-memory DOM representation
for diffing predates React. What React's team discovered
and publicised was that the heuristic tree diffing approach
(O(n) vs naive O(n³)) made it practical for UIs. More
surprisingly: React's creator Jordan Walke initially
described the virtual DOM as a "temporary hack" and expected
it to be replaced by more direct DOM update mechanisms.
Instead, it became React's defining characteristic. And even
more surprisingly: the React team is now working to replace
it with compile-time optimisations (React Compiler/React
Forget) - coming full circle to what Walke originally
imagined.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** Draw the virtual DOM update cycle from
   `setState()` to real DOM mutation, naming the Render,
   Reconciliation, and Commit phases and what is different
   about each.
2. **DEBUG** Given a list where items lose their input
   values on sort, identify that missing or unstable keys
   are the cause and fix it with stable IDs.
3. **DECIDE** Explain to a colleague why manually updating
   a DOM node via `ref.current.textContent =` inside a
   component that also has React state will produce
   incorrect renders on the next state update.
4. **BUILD** Demonstrate deliberate remounting using
   `key` prop to reset a complex child component's state
   when a specific prop changes.
5. **COMPARE** Explain to a tech lead why you would
   consider Svelte or SolidJS over React for a new
   performance-critical project, framing the argument in
   terms of virtual DOM overhead vs ecosystem trade-offs.

---

### 🧠 Think About This Before We Continue

**Q1.** React's virtual DOM diff heuristic assumes that
elements at the same tree position are the same component
instance across renders. What happens when a conditional
like `{isAdmin ? <AdminPanel /> : <UserPanel />}` flips?
Both components are at the same tree position but are
different types. Trace through the reconciliation process:
what DOM operations happen, and what state is preserved?
_Hint: Type change = full subtree replace._

**Q2.** React Fiber changed the internals of the virtual
DOM from a recursive synchronous process to a work-loop
that can be paused and resumed. But from the outside,
the virtual DOM model looks the same: components return JSX,
React diffs it. What visible developer-facing behaviour
changed with Concurrent Mode that is attributable to this
internal change in how the virtual DOM is processed?
_Hint: Transitions, Suspense fallbacks, useTransition._

**Q3.** The virtual DOM is often described as an
"abstraction over the DOM." React Native uses the same
React programming model but renders to native iOS and
Android widgets, not HTML DOM elements. What does this
tell you about where the "virtual DOM" model ends and where
the platform-specific rendering begins? What is the correct
name for the layer that actually does platform rendering?
_Hint: react-dom vs react-native renderer; React itself
is renderer-agnostic._
