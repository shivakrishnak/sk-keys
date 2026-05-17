---
id: RCT-044
title: Compound Components Pattern
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★★
depends_on: RCT-022, RCT-024, RCT-043
used_by: RCT-069
related: RCT-042, RCT-043, RCT-022
tags:
  - react
  - frontend
  - patterns
  - composition
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /react/compound-components-pattern/
---

# RCT-044 - COMPOUND COMPONENTS PATTERN

⚡ TL;DR - Compound Components is a pattern where a
parent component manages shared state and exposes child
components as named sub-components (e.g. `<Select.Option>`),
using React Context to implicitly share state between
parent and children without prop drilling; it gives
consumers full control over the composition and order
of sub-components while encapsulating all coordination
logic in the parent.

| #044            | Category: React                                        | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | useContext Hook, Custom Hooks, Render Props Pattern    |                 |
| **Used by:**    | Design System Architecture with React                  |                 |
| **Related:**    | Higher-Order Components, Render Props, useContext Hook |                 |

---

### 🔥 The Problem This Solves

**THE RIGID COMPONENT API PROBLEM:**
A `<Select>` component needs to render a list of options.
The obvious implementation: pass all options as a prop.

```jsx
// NAIVE: monolithic API
<Select
  options={[
    { label: "Apple", value: "apple", disabled: false },
    { label: "Banana", value: "banana", disabled: true },
    { label: "Cherry", value: "cherry", disabled: false },
  ]}
  onSelect={handleSelect}
/>
```

The problem surfaces when consumers need customisation:

- Add an icon to one option
- Group options by category
- Add a "create new" option at the bottom
- Custom rendering for some items

Each customisation requires adding props: `renderOption`,
`groupBy`, `footer`, `renderHeader`. The component API
grows without bounds. Consumers are at the mercy of what
the component author anticipated.

Compound Components solve this: the parent provides the
coordination (state, context), and consumers compose
the children in any order with any structure.

---

### 📘 Textbook Definition

**Compound Components Pattern** - a React component API
design pattern where a "parent" component manages shared
state via Context and exposes "sub-components" (child
components attached as properties on the parent, e.g.
`Select.Option`, `Tabs.Tab`, `Accordion.Panel`) that
implicitly consume the parent's context. Consumers compose
the sub-components in any order and structure, with
full control over the rendered layout and content of
each piece, while the parent handles all state
coordination between the sub-components.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// Compound Components usage:
<Select value={selected} onChange={setSelected}>
  <Select.Option value="apple">🍎 Apple</Select.Option>
  <Select.Option value="banana" disabled>
    🍌 Banana (out of stock)
  </Select.Option>
  <Select.Separator /> {/* Custom content between options */}
  <Select.Option value="cherry">🍒 Cherry</Select.Option>
</Select>

// Benefits:
// - Consumer controls the structure and order of options
// - Each option can have custom content (icons, badges)
// - Can insert arbitrary elements (Separator)
// - Parent Select handles selection state - consumer does not
// - No prop explosion (no renderOption callback needed)
```

---

### 🔩 First Principles Explanation

**THE CONTEXT COMMUNICATION MECHANISM:**

```
Compound Components work via React Context:

1. Parent component creates a Context:
   const SelectContext = createContext(null);

2. Parent provides state to all children via Context:
   <SelectContext.Provider value={{ selected, onSelect }}>
     {children}
   </SelectContext.Provider>

3. Sub-components (Select.Option) consume the context:
   function Option({ value, children, disabled }) {
     const { selected, onSelect } = useContext(SelectContext);
     const isSelected = selected === value;
     return (
       <li
         aria-selected={isSelected}
         onClick={() => !disabled && onSelect(value)}
       >
         {children}
       </li>
     );
   }

4. Sub-components are attached to the parent as properties:
   Select.Option = Option;
   Select.Separator = Separator;

5. Consumer composes using the parent + sub-components:
   <Select><Select.Option value="x">X</Select.Option></Select>
```

---

### 🧪 Thought Experiment

**THE TABS COMPONENT FLEXIBILITY TEST:**
A design system's `<Tabs>` component needs to support:

- Regular tabs (tabs above content)
- Vertical tabs (tabs on the left)
- Tabs with icons
- Tabs with notification badges
- Programmatically controlled active tab
- Lazy loading of tab content
- Custom tab styles per tab (active/inactive/disabled)
- Keyboard navigation
- ARIA accessibility attributes

With a monolithic API: you would need props for each of
these. The component author must anticipate every use case.
Users who need combinations of these features may be stuck.

With Compound Components:

```jsx
<Tabs defaultTab="tab1">
  <Tabs.List>
    <Tabs.Tab value="tab1">
      <BellIcon /> Notifications
      <Badge count={5} />
    </Tabs.Tab>
    <Tabs.Tab value="tab2" disabled>
      Settings
    </Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="tab1">
    <NotificationList />
  </Tabs.Panel>
  <Tabs.Panel value="tab2">
    <SettingsPanel />
  </Tabs.Panel>
</Tabs>
```

The consumer adds icons, badges, and disabled state without
any new props. The Tabs parent handles selection state
and ARIA. Each piece is independently customisable.

---

### 🧠 Mental Model / Analogy

> Compound Components are like a restaurant menu system.
> The restaurant (parent) manages the bill, the table,
> and the kitchen coordination (state). The menu items
> (sub-components) each do their own thing but implicitly
> connect to the restaurant's system (context) when
> ordered. The diner (consumer) can choose any combination
> of menu items in any order - the restaurant coordinates
> the kitchen regardless.
>
> A monolithic API would be like a set menu: the restaurant
> decides the courses. Compound components are a la carte:
> the diner composes the meal.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Parent component manages state via Context. Sub-components
consume that context implicitly. Consumer composes them
in any order. No prop drilling, full layout control.

**Level 2 (implementation):**
`createContext` in the parent. `useContext` in each sub-
component. Attach sub-components as static properties
(`Select.Option = Option`). Parent renders `{children}`.

**Level 3 (controlled vs uncontrolled):**
Compound components can be uncontrolled (internal state
in the parent, e.g. `defaultValue`) or controlled (state
managed by the consumer, e.g. `value` + `onChange`). Use
the pattern from HTML's `<input>`: support both, with
`defaultValue` for uncontrolled and `value`+`onChange`
for controlled.

**Level 4 (validation):**
Sub-components should validate that they are used inside
the correct parent. If `useContext(SelectContext)` returns
`null` (no parent Select), the sub-component is being
used incorrectly. Throw a useful error:

```jsx
const context = useContext(SelectContext);
if (context === null) {
  throw new Error("Select.Option must be used inside <Select>");
}
```

**Level 5 (mastery):**
The Compound Components pattern is the foundation of
headless UI libraries: Radix UI, Headless UI, react-aria.
These libraries provide all the accessibility and
interaction logic (keyboard nav, ARIA, focus management)
as a Compound Components API, and let consumers provide
all the markup and styles. The pattern separates
"behaviour" from "appearance" at the library level.
For design systems, Compound Components enable component
flexibility without prop explosion - a critical capability
for maintaining a component library that serves diverse
consumer needs without constant new API additions.

---

### ⚙️ How It Works (Mechanism)

**Full Compound Component implementation:**

```jsx
import { createContext, useContext, useState } from "react";

// 1. Create the context (null default triggers validation error)
const SelectContext = createContext(null);

// 2. Custom hook for consuming context with validation
function useSelectContext() {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error("Select sub-components must be used inside <Select>");
  }
  return context;
}

// 3. Sub-components
function Option({ value, children, disabled = false }) {
  const { selected, onSelect } = useSelectContext();
  const isSelected = selected === value;

  return (
    <li
      role="option"
      aria-selected={isSelected}
      aria-disabled={disabled}
      onClick={() => !disabled && onSelect(value)}
      style={{
        fontWeight: isSelected ? "bold" : "normal",
        opacity: disabled ? 0.5 : 1,
        cursor: disabled ? "not-allowed" : "pointer",
      }}
    >
      {children}
    </li>
  );
}

function Separator() {
  return <li role="separator" aria-hidden="true" />;
}

// 4. Parent component
function Select({ value, onChange, defaultValue, children }) {
  // Support both controlled and uncontrolled
  const isControlled = value !== undefined;
  const [internalValue, setInternalValue] = useState(defaultValue);
  const selected = isControlled ? value : internalValue;

  function onSelect(newValue) {
    if (!isControlled) setInternalValue(newValue);
    onChange?.(newValue);
  }

  return (
    <SelectContext.Provider value={{ selected, onSelect }}>
      <ul role="listbox">{children}</ul>
    </SelectContext.Provider>
  );
}

// 5. Attach sub-components as static properties
Select.Option = Option;
Select.Separator = Separator;

export { Select };
```

---

### 💻 Code Example

**BAD: Prop-based API (rigid, hard to customise):**

```jsx
// BAD: every customisation requires new props
function Select({ options, renderOption, header, footer, onSelect }) {
  return (
    <ul>
      {header && <li>{header}</li>}
      {options.map((o) =>
        renderOption ? (
          renderOption(o)
        ) : (
          <li key={o.value} onClick={() => onSelect(o.value)}>
            {o.label}
          </li>
        ),
      )}
      {footer && <li>{footer}</li>}
    </ul>
  );
}
// Adding a badge to one option? Add badgeMap prop.
// Adding a separator? Add separatorAfterIndex prop.
// The props grow without bound.
```

**GOOD: Compound Components (composable, extensible):**

```jsx
// GOOD: consumer has full structural control
<Select onChange={setSelected} defaultValue="apple">
  <Select.Option value="apple">
    🍎 Apple <NewBadge /> {/* badge just works */}
  </Select.Option>
  <Select.Separator /> {/* insert anywhere */}
  <Select.Option value="cherry">🍒 Cherry</Select.Option>
</Select>
// No new props needed for badge, separator, or icons
// Consumer composes the structure they need
```

---

### 📊 Comparison Table

|                          | Compound Components                 | Render Props                   | Config Props               |
| ------------------------ | ----------------------------------- | ------------------------------ | -------------------------- |
| Consumer control         | Full layout control                 | Partial (inside render fn)     | Limited (via config props) |
| Customisation surface    | Unlimited (compose children freely) | What the render fn exposes     | What props expose          |
| API surface (on parent)  | Small (context + children)          | Medium (render prop signature) | Large (many props)         |
| Learning curve           | Higher (must know sub-components)   | Medium                         | Low (just pass props)      |
| Sub-component validation | Yes (useContext null check)         | N/A                            | N/A                        |
| ARIA/a11y management     | Centralised in parent               | Split between parent/render    | Centralised                |
| Used by                  | Radix UI, Headless UI, Ant Design   | react-window, older Formik     | MUI (many props)           |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                             |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Compound Components require Context"                 | Not strictly - the original pattern used `React.Children` + `cloneElement` to pass state to children directly. Context is the modern, cleaner implementation. `cloneElement` has limitations: only works with direct children (not wrapped/nested children), and is considered legacy. Context works regardless of nesting depth.   |
| "Sub-components can be used independently anywhere"   | Sub-components are designed to be used inside their parent and read from its context. Using `<Select.Option>` outside `<Select>` should throw an error (if context validation is implemented). This is a feature - it makes misuse obvious.                                                                                         |
| "Compound Components are only for complex components" | The pattern is valuable whenever a component has multiple related pieces that share state. A simple `<Accordion>` with `<Accordion.Item>` and `<Accordion.Panel>` is a legitimate compound component. The threshold is: if you need more than 2-3 config props and consumers want layout flexibility, consider compound components. |
| "Compound Components prevent TypeScript typing"       | TypeScript can fully type compound components. The sub-components are typed individually, and the parent's static property types are inferred automatically when you attach them with `Parent.Child = Child`. The context type from `createContext<ContextType>` provides full type safety inside sub-components.                   |

---

### 🚨 Failure Modes & Diagnosis

**Sub-component Used Outside Parent - Silent Null Bug**

**Symptom:** A sub-component renders but does nothing -
clicks are ignored, state does not update.

**Root Cause:** Context value is `null` (no parent
provider). Without validation, `useContext` returns null
and the onClick handler silently does nothing.

**Fix:** Add the null check:

```jsx
const context = useContext(SelectContext);
if (!context) {
  throw new Error(
    "Select.Option must be used within <Select>. " +
      "Check that you are not using Select.Option " +
      "outside the Select component tree.",
  );
}
```

---

**Context Not Updated for Deeply Nested Sub-components**

**Symptom:** Sub-components three levels deep inside the
compound component do not react to parent state changes.

**Root Cause:** The Context Provider is not wrapping the
full subtree, or a memoised intermediate component is
not re-rendering.

**Diagnosis:** React DevTools → inspect the component
tree for the Context Provider. Check that the Provider
wraps ALL rendered children. Check for `React.memo` on
intermediate components that might block context updates.

Note: Context bypasses `React.memo` - components that
call `useContext` always re-render when context changes,
regardless of `React.memo` on ancestors. If a memoised
component READS from context, it will update. If it does
NOT read from context, memo works correctly.

---

### 🔗 Related Keywords

**Prerequisites:**

- `useContext Hook` - the mechanism for sharing state
  between parent and sub-components
- `Custom Hooks` - often used to encapsulate the context
  consumption with validation
- `Render Props Pattern` - the predecessor pattern that
  Compound Components extend

**Builds On:**

- `Design System Architecture with React` - Compound
  Components are the foundation of flexible design system
  component APIs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRUCTURE │ Parent creates context → children consume    │
│           │ Sub-components attached: Parent.Child = Child│
├──────────────────────────────────────────────────────────┤
│ USAGE     │ <Select><Select.Option>..</Select.Option>    │
│ VALIDATE  │ useContext null check → throw useful error   │
│ BOTH      │ Support controlled (value+onChange) and      │
│           │ uncontrolled (defaultValue) modes            │
├──────────────────────────────────────────────────────────┤
│ WHEN      │ 2+ related pieces, layout flexibility needed │
│ HEADLESS  │ Radix UI, Headless UI use this pattern       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Parent provides state via Context. Sub-components
   (`Parent.Child`) consume context implicitly. Consumers
   compose sub-components in any order.
2. Validate context in sub-components: if `useContext`
   returns null, throw a helpful error (sub-component
   used outside parent).
3. Compound Components are the foundation of headless UI:
   provide behaviour + accessibility in the parent; let
   consumers provide markup + styling in the children.

**Interview one-liner:**
"Compound Components is a React composition pattern where
a parent component manages shared state via Context and
exposes child sub-components (e.g. `<Select.Option>`)
that implicitly consume that state. Consumers have full
control over the structure and order of sub-components,
enabling flexible layouts without prop explosion. It is
the pattern used by Radix UI, Headless UI, and most
design system libraries - the parent provides behaviour
and accessibility, consumers provide markup and styling.
Key rules: validate context usage in sub-components, and
support both controlled and uncontrolled modes."

---

### 💎 Transferable Wisdom

Compound Components implement the "Inversion of Control"
principle at the component level: instead of the parent
controlling exactly what renders (by accepting a large
config), it delegates control to the consumer by exposing
sub-components. This is a universal pattern in software
architecture: plugin systems (the host provides hooks,
plugins control their own behaviour), event-driven
architectures (the event bus provides routing, subscribers
control their own handling), and the Hollywood Principle
("don't call us, we'll call you" - the framework calls
your code, not the other way around). The common benefit
is extensibility without modification: new capabilities
can be added by new sub-components without changing the
parent API.

---

### 💡 The Surprising Truth

The Compound Components pattern was coined by Kent C.
Dodds in 2017 as a "secret advanced React component
pattern" - secret because it was not widely documented
despite being used in prominent libraries (Reach UI,
which Dodds co-created). The original implementation
used `React.Children.map` + `cloneElement` to inject
props into direct children (before Context was common).
This approach broke when consumers wrapped children in
`<div>`s (cloneElement only works on direct children).
Context fixed this limitation entirely - context works
regardless of how deeply children are nested. Dodds
updated his teaching to use Context. Today, every major
headless UI library uses Compound Components + Context
as their fundamental API design, making it one of the
most impactful patterns in modern React library design.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a fully functional `<Accordion>` using
   Compound Components: `<Accordion>`, `<Accordion.Item>`,
   `<Accordion.Header>`, `<Accordion.Panel>`. Include
   context validation (throw error if used outside
   parent) and support both single-open and multi-open
   modes.
2. **IMPLEMENT** both controlled and uncontrolled modes
   for the Accordion: `defaultOpenItem` for uncontrolled,
   `openItem` + `onOpenChange` for controlled.
3. **ADD** TypeScript types to the Accordion compound
   component: context type, sub-component props, and
   the static property attachment on the parent.
4. **DEMONSTRATE** the cloneElement vs Context approach:
   show that cloneElement fails when `<Accordion.Item>`
   is wrapped in a `<div>`, and that Context works
   regardless of wrapping depth.
5. **COMPARE** the Accordion compound component API to
   the Radix UI Accordion API (from radix-ui.com docs).
   Identify which principles are the same and what Radix
   adds (accessibility, animation, keyboard navigation).

---

### 🧠 Think About This Before We Continue

**Q1.** Compound Components rely on Context for implicit
communication between parent and sub-components. Context
causes ALL consumers to re-render when the context value
changes. In a complex Compound Component (like a large
`<DataGrid>` with hundreds of `<Cell>` sub-components),
every state change (hover, selection) could cause hundreds
of re-renders. How do you design the Context to minimise
re-renders? Consider splitting context, using selectors,
or using Zustand as the state mechanism instead of React
Context.

**Q2.** The `<select>` and `<option>` HTML elements are
a native implementation of Compound Components. The
browser coordinates state between them implicitly.
Implement a custom accessible `<Select>` that mimics
the native API but allows custom styling and icons in
options. What ARIA attributes are required? How do you
handle keyboard navigation (arrow keys, Enter, Escape)?
How does your implementation differ from just styling
the native `<select>`?

**Q3.** A design system team is deciding whether to
build their components with Compound Components or a
configuration object (a `config` prop with slots). The
config approach is simpler to implement but less flexible.
The Compound Components approach is more flexible but
requires consumers to compose sub-components. For a
component library with 30 components and 100 consumer
teams, what are the long-term maintenance implications
of each approach?
