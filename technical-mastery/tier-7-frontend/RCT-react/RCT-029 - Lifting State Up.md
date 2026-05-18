---
id: RCT-029
title: Lifting State Up
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-009, RCT-010, RCT-020, RCT-016
used_by: RCT-030, RCT-022, RCT-034, RCT-051
related: RCT-030, RCT-022, RCT-034
tags:
  - react
  - frontend
  - state
  - composition
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/react/lifting-state-up/
---

⚡ TL;DR - Lifting State Up moves shared state from
multiple sibling components to their closest common
ancestor, then distributes it via props - the canonical
React pattern for sibling-to-sibling communication and
the prerequisite concept before Context API and Redux.

| #029            | Category: React                                              | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Props, React Components, useState Hook, One-Way Data Binding |                 |
| **Used by:**    | Prop Drilling Anti-Pattern, useContext Hook, useReducer Hook |                 |
| **Related:**    | Prop Drilling Anti-Pattern, useContext Hook, useReducer Hook |                 |

---

### 🔥 The Problem This Solves

**TWO COMPONENTS, ONE SHARED VALUE:**
Two sibling components both need to read and respond to
the same value. For example:

- A filter component that controls which products are shown
- A product list that uses the filter to decide what to render

Both need the filter state. Neither is a parent of the
other. React data flows only one way: down via props.
Siblings cannot share state directly.

The naive solution is to duplicate the state in both
components - but then they get out of sync. Lifting State
Up is the correct solution: move the state to their shared
parent, pass it down via props, pass event handlers down
for updates.

---

### 📘 Textbook Definition

**Lifting State Up** - the React pattern of moving state
to the lowest common ancestor of all components that
need it, then distributing the state via props (read) and
callback props (write). The child component becomes
"controlled" by its parent: it displays what the parent
passes in and calls the parent's handler when it wants
to change the value. The parent owns the state and is the
single source of truth for all its children.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// BEFORE: State duplicated in siblings (bad - out of sync)
function Filters() {
  const [query, setQuery] = useState(""); // own state
  return <input value={query} onChange={(e) => setQuery(
      e.target.value)} />;
}
function ProductList() {
  // Can't access Filters' query!
  return <ul>...</ul>;
}

// AFTER: State lifted to parent (correct)
function ProductPage() {
  const [query, setQuery] = useState(""); // parent owns state

  return (
    <>
      {/* pass state down + callback for changes */}
      <SearchBar query={query} onQueryChange={setQuery} />
      {/* pass state down for filtering */}
      <ProductList query={query} />
    </>
  );
}
// Both children see the same query. Parent is single source.
```

---

### 🔩 First Principles Explanation

**THE INFORMATION FLOW PROBLEM:**

```
ONE-WAY DATA FLOW:
  Parent → Child: via props (always available)
  Child → Parent: via callback props (lifting state up)
  Sibling → Sibling: NOT directly possible
    → Must go: ChildA → Parent → ChildB
    → Achieved by: lifting state to Parent

DATA FLOW WITH LIFTED STATE:
  Parent owns state
    ↓ passes value via prop
    ChildA (displays/reads value)
    ↓ user interaction in ChildA
    ChildA calls onValueChange callback (passed from
      Parent)
    ↓
    Parent.setState(newValue)
    ↓
    React re-renders Parent
    ↓ passes new value via props to both children
    ChildA + ChildB receive new value
```

**THE CONTROLLED COMPONENT PARALLEL:**
Lifting state up for sibling communication is the same
conceptual move as controlled inputs (RCT-025). In
controlled inputs, the DOM form element's state is lifted
to React component state. In lifting state up, a child
component's local state is lifted to the parent. Same
pattern, different scope.

**LOWEST COMMON ANCESTOR RULE:**
Lift to the LOWEST ancestor that is a parent of all
components needing the state. Lifting too high (e.g.,
to `<App>`) causes unnecessary re-renders across the
entire tree and is the seed of Prop Drilling (RCT-030).

---

### 🧪 Thought Experiment

**THE TEMPERATURE CONVERTER:**
The canonical React documentation example: two inputs,
one in Celsius, one in Fahrenheit. Changing one updates
the other. They must always be in sync.

If each input has its own state, they cannot sync.
Solution: lift the temperature state to their parent
`Calculator`. Both inputs receive the temperature and
an `onTemperatureChange` callback. When the user types
in Celsius input, it calls `onTemperatureChange('c', value)`.
The parent converts to the canonical unit (Celsius), stores
it, and passes the derived Fahrenheit value to the other
input. Both stay in sync because they share one source
of truth.

---

### 🧠 Mental Model / Analogy

> Two assistants (child components) are working on a
> project and need to share a document. They cannot
> directly exchange files (siblings cannot share state).
> The solution: give the document to the manager (parent
> component). Each assistant reads the document from
> the manager's desk (props). When an assistant needs
> to update the document, they hand a revision note to
> the manager (callback prop). The manager updates the
> document on their desk (setState). Both assistants
> immediately see the updated document when they next
> look (re-render with new props).

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
When two components need the same state, move the state
to their parent. Pass the value down as a prop. Pass a
function (callback) down to update it. Parent is the
single source of truth.

**Level 2 (usage):**
Remove `useState` from both children. Add `useState` to
parent. Pass `value={state}` down to the display child.
Pass `onChange={setState}` down to the input child. Parent
re-renders both when value changes.

**Level 3 (identification):**
Recognise when to lift: "Two components need the same
value." Recognise when you have lifted too high: you are
passing state through 3+ intermediate components that
do not use it (that is Prop Drilling - RCT-030). The
lifting point should be the lowest common ancestor.

**Level 4 (scale):**
When many components across the tree share state, lifting
to the closest common ancestor may still result in prop
drilling (passing through many intermediate layers). The
solutions are Context API (for cross-tree state) and
state management libraries (Redux, Zustand) for global
state. Lifting state up is the manual, no-library solution
that works well for 1-2 levels of sharing.

**Level 5 (mastery):**
Lifting state up is a deliberate trade-off: co-location
of state (keeping state near where it is used) vs sharing.
Co-located state re-renders only the component that owns
it. Lifted state re-renders the parent and all its children
on every change. For performance-sensitive code, this
means lifted state that changes frequently (e.g., text
input value) can cause expensive re-renders of unrelated
siblings. Solutions: `React.memo` on siblings, `useReducer`
with `dispatch` passed as a stable reference, or Context
splitting to isolate re-render boundaries.

---

### ⚙️ How It Works (Mechanism)

**Complete example: tabs and content panels:**

```jsx
// Before lifting - each tab manages its own "active" flag
// (broken: multiple tabs can be active simultaneously)
function Tab({ label }) {
  const [isActive, setIsActive] = useState(false);
  return (
    <button
      onClick={() => setIsActive((prev) => !prev)}
      className={isActive ? "active" : ""}
    >
      {label}
    </button>
  );
}

// After lifting - parent owns which tab is active
function TabContainer() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div>
      {/* Tab buttons: read activeTab, call setActiveTab */}
      <TabBar
        tabs={["overview", "details", "reviews"]}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      {/* Content: reads activeTab to decide what to render */}
      <TabPanel activeTab={activeTab} />
    </div>
  );
}

function TabBar({ tabs, activeTab, onTabChange }) {
  return (
    <nav>
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onTabChange(tab)}
          className={activeTab === tab ? "active" : ""}
        >
          {tab}
        </button>
      ))}
    </nav>
  );
}

function TabPanel({ activeTab }) {
  return (
    <div>
      {activeTab === "overview" && <Overview />}
      {activeTab === "details" && <Details />}
      {activeTab === "reviews" && <Reviews />}
    </div>
  );
}
```

---

### 💻 Code Example

**BAD: Sibling state duplication (out of sync):**

```jsx
// BAD: each sibling owns its own copy of the filter
function FilterBar() {
  const [category, setCategory] = useState("all");
  // ... renders category buttons
  // Products has no access to this 'category' value
}

function ProductGrid() {
  const [category, setCategory] = useState("all");
  // This is a DIFFERENT state from FilterBar's category!
  // Changing FilterBar's state does NOT update ProductGrid's
  // They will always be out of sync
  return products
    .filter((p) => category === "all" || p.category === category)
    .map((p) => <ProductCard key={p.id} product={p} />);
}

function ShopPage() {
  return (
    <>
      <FilterBar /> {/* owns its own category */}
      <ProductGrid /> {/* owns its own category */}
    </>
  );
}
```

**GOOD: State lifted to shared parent:**

```jsx
// GOOD: parent owns the category state (single source of truth)
function ShopPage() {
  const [category, setCategory] = useState("all");

  return (
    <>
      {/* FilterBar reads + updates via callback */}
      <FilterBar activeCategory={category} onCategoryChange={setCategory} />
      {/* ProductGrid reads to filter */}
      <ProductGrid category={category} />
    </>
  );
}

function FilterBar({ activeCategory, onCategoryChange }) {
  const categories = ["all", "shoes", "clothing", "accessories"];
  return (
    <nav>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onCategoryChange(cat)}
          className={activeCategory === cat ? "active" : ""}
        >
          {cat}
        </button>
      ))}
    </nav>
  );
}

function ProductGrid({ category }) {
  const filtered = products.filter(
    (p) => category === "all" || p.category === category,
  );
  return (
    <ul>
      {filtered.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                   | Reality                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Lifting state up always means lifting to `<App>`"                              | Lift to the LOWEST common ancestor. Lifting to `<App>` when only two sibling components need the state causes all of `<App>`'s children to re-render on every state change. Identify the lowest parent that contains all the components that need the state. |
| "After lifting, both children will re-render on every change"                   | Yes - and this is correct. The re-render is necessary to propagate the new state to both. Optimise with `React.memo` if sibling re-renders are expensive and the sibling's props did not change.                                                             |
| "Lifting state is only needed when two components both need to WRITE the state" | Lifting is needed when any two siblings need to READ the same state, even if only one writes. A display component and an edit component both need the same data value - lift it even if only the edit component changes it.                                  |
| "Context API replaces lifting state up"                                         | Context eliminates prop drilling (passing through intermediate components that do not use the state). But the state still needs to live somewhere - typically in a parent that provides the context. Lifting state and Context often work together.          |

---

### 🚨 Failure Modes & Diagnosis

**Unnecessary Re-renders of Sibling Components**

**Symptom:** After lifting state, typing in a filter input
causes a slow re-render of a large sibling list component,
even though the list's props did not change.

**Root Cause:** Lifting to a common parent causes the
parent to re-render on each state change. All children
of the parent re-render by default, even if their props
did not change (React does not skip re-renders automatically).

**Diagnosis:** React DevTools Profiler - record a filter
keystroke, check which components re-rendered. Expensive
re-renders will have a high render time.

**Fix:** Wrap the non-changing sibling in `React.memo`:

```jsx
const ProductGrid = React.memo(function ProductGrid({ category }) {
  // Now only re-renders when `category` prop changes
});
```

---

**State Lifted Too High - Root of Prop Drilling**

**Symptom:** State is passed as props through 4+ components
that do not use it themselves. A change to the state
type requires updating 4+ component interfaces.

**Root Cause:** State was lifted to a common ancestor
that is too high in the tree. Often caused by lifting
to `<App>` as a shortcut instead of finding the true
lowest common ancestor.

**Fix:** Identify the actual lowest common ancestor.
Restructure the component hierarchy if needed. For very
deep sharing, use Context API (RCT-022).

---

### 🔗 Related Keywords

**Prerequisites:**

- `Props and Component Communication` - props are the
  mechanism for distributing lifted state
- `React Components` - the component tree structure
  that determines what "lowest common ancestor" means
- `useState Hook` - the state mechanism moved to parent
- `One-Way Data Binding` - the constraint that requires
  lifting state (no two-way binding)

**Builds On:**

- `Prop Drilling Anti-Pattern` - what happens when lifted
  state must pass through too many intermediate layers
- `useContext Hook` - the solution when prop passing
  becomes impractical due to tree depth

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SIGNAL      │ Two siblings need the same state value    │
│ SOLUTION    │ Move state to lowest common ancestor      │
├─────────────────────────────────────────────────────────┤
│ DISTRIBUTION│ value via prop (read)                     │
│             │ onChange callback via prop (write)        │
├─────────────────────────────────────────────────────────┤
│ RULE        │ Lift to LOWEST ancestor (not App)         │
│ AVOID       │ Lifting higher than necessary = Prop Drill│
├─────────────────────────────────────────────────────────┤
│ SCALE       │ 1-2 levels: lift state                    │
│             │ 3+ levels of passing: use Context         │
│             │ Global / complex: use Redux/Zustand       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Move shared state to the lowest common ancestor of
   all components that need it.
2. Pass value down via props. Pass update handler down
   via callback props.
3. Lift to the LOWEST ancestor (not App). Too high =
   prop drilling + unnecessary re-renders.

**Interview one-liner:**
"Lifting State Up solves sibling communication: move state
to the lowest common ancestor, pass the value down via
props (read), and pass an update handler down via callback
props (write). The ancestor is the single source of truth.
Lift to the LOWEST ancestor, not the root - lifting too
high causes prop drilling and unnecessary re-renders
across unrelated components."

---

### 💎 Transferable Wisdom

Lifting state up is the React expression of a universal
principle: "single source of truth." Multiple representations
of the same data that can diverge are a bug waiting to
happen. This appears in: database normalisation (one
authoritative table for each entity), Git (one remote
as the source of truth), configuration management
(one config file, not multiple copies with manual sync),
microservices (each service owns its domain data, others
query it rather than caching copies). The React lifting
pattern teaches the same discipline at the UI component
level.

---

### 💡 The Surprising Truth

The official React documentation's Lifting State Up
example is a temperature converter (Celsius/Fahrenheit).
But the most subtle and important insight in that example
is not the lifting itself - it is the "canonical form"
principle: instead of storing both `celsius` and
`fahrenheit` as separate state, store only one (Celsius)
and derive the other (`fahrenheit = celsius * 9/5 + 32`).
Derived state is never a source of truth - it is computed.
This principle (store minimal state, derive the rest)
prevents the second class of out-of-sync bugs: two state
variables that should always be related but can diverge.
Lifting state fixes who owns it. Deriving state fixes
what should be stored at all.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a product catalog page with a search
   filter (text input) and a product grid that both need
   the search query - using lifted state. No context or
   library.
2. **IDENTIFY** the lowest common ancestor in a given
   component tree and explain why lifting to a higher
   ancestor would be incorrect.
3. **DEMONSTRATE** the re-render behaviour after lifting:
   use React DevTools Profiler to show which components
   re-render when the parent's state changes, and apply
   `React.memo` to prevent unnecessary sibling re-renders.
4. **EXPLAIN** when to graduate from lifting state up
   to Context API, and what specific symptoms indicate
   the transition point.
5. **DISTINGUISH** between lifted state and derived state:
   given a form with "password" and "password strength"
   as two `useState` values, explain which one should
   be state and which should be derived.

---

### 🧠 Think About This Before We Continue

**Q1.** A shopping cart header shows the item count.
The product list has an "Add to Cart" button on each item.
They are siblings. You lift the `cart` state to their
parent. Now every time the user types in a search filter
(also lifted to the same parent), the entire product
list re-renders. How do you restructure the component
hierarchy or state placement to prevent this?

**Q2.** Lifting state up moves state "up." But React's
performance model prefers state close to where it is
used (co-location). These are opposing forces. What is
the process for deciding when to co-locate and when to
lift? Are there measurable criteria or is it judgment?

**Q3.** Redux and Zustand are described as "global state
managers." If you can always lift state to the root App
component and pass it everywhere via props, why do these
libraries exist? What specific problem does a dedicated
state management library solve that lifting to the root
does not?
