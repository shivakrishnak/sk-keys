---
id: RCT-025
title: Controlled vs Uncontrolled Components
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-010, RCT-013, RCT-020, RCT-023
used_by: RCT-026, RCT-039
related: RCT-020, RCT-026, RCT-023
tags:
  - react
  - frontend
  - forms
  - controlled
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /react/controlled-vs-uncontrolled-components/
---

# RCT-025 - CONTROLLED VS UNCONTROLLED COMPONENTS

⚡ TL;DR - A controlled input's value is driven by React
state (`value={state}` + `onChange`); an uncontrolled
input manages its own DOM value read via `useRef`; controlled
is the React standard because state is the single source
of truth, but uncontrolled avoids re-renders and is simpler
for large forms with no real-time validation.

| #025 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | State, Event Handling, useState Hook, useRef Hook | |
| **Used by:** | Form Handling in React, Redux Toolkit Architecture | |
| **Related:** | useState Hook, Form Handling in React, useRef Hook | |

---

### 🔥 The Problem This Solves

**FORM INPUT OWNERSHIP AMBIGUITY:**
HTML inputs manage their own value state in the DOM.
When you type "Hello" in an input, the DOM input's value
is "Hello" - stored in the DOM, not in JavaScript. This
is "uncontrolled" from React's perspective.

React's declarative model says: state is the source of
truth; the DOM is the output. But for form inputs, the
DOM is managing state (what the user typed). This creates
a tension: should the input value be owned by React state
or the DOM?

React offers both options with different trade-offs.
Understanding which to use - and when each is correct -
is essential for building forms correctly.

---

### 📘 Textbook Definition

**Controlled component:** A form element whose value is
controlled by React state. The `value` prop is set from
state (`value={state}`), and an `onChange` handler updates
state as the user types. React drives the input's displayed
value on every render. The component cannot display a value
that is not in React state.

**Uncontrolled component:** A form element that manages
its own value in the DOM. React does not drive the input's
value. The current value is read on demand via `useRef`
(typically on form submit). React's `defaultValue` sets
the initial value only.

---

### ⏱️ Understand It in 30 Seconds

**Controlled:**

```jsx
const [email, setEmail] = useState('');
<input
  value={email}           // React drives the value
  onChange={e => setEmail(e.target.value)}  // state update
/>
// email state IS the input value at all times
```

**Uncontrolled:**

```jsx
const emailRef = useRef(null);
<input
  ref={emailRef}          // DOM drives the value
  defaultValue=""         // initial value only
/>
// Read on submit: emailRef.current.value
// React does not know the current value during typing
```

---

### 🔩 First Principles Explanation

**THE OWNERSHIP MODEL:**

```
CONTROLLED:
  User types → onChange fires → setEmail(value)
  → state updates → React re-renders → input.value = state
  React state ↔ DOM value (always in sync, React owns it)

UNCONTROLLED:
  User types → DOM updates input.value
  React state is NOT updated
  On submit: read emailRef.current.value from DOM
  DOM owns the value; React reads it when needed
```

**TRADEOFFS IN DETAIL:**

```
CONTROLLED:
  + State is always current (real-time validation)
  + Programmatic value change (clear button, format on blur)
  + React state is always in sync with UI
  - Re-render on every keystroke
  - More boilerplate per field

UNCONTROLLED:
  + No re-render while typing
  + Less boilerplate for simple forms
  + Works with some third-party DOM-based libraries
  - No real-time validation (can't check "as you type")
  - Cannot programmatically set value after mount (mostly)
  - DOM is the source of truth (less React-idiomatic)
```

---

### 🧪 Thought Experiment

**REAL-TIME PASSWORD STRENGTH:**
A registration form needs to show password strength as the
user types (weak/medium/strong indicator).

With **uncontrolled**: the strength cannot be computed
because React does not know the current input value until
submit. You would need to add an `onChange` listener
manually - at which point you have partially controlled
the input anyway.

With **controlled**: `onChange` updates state on every
keystroke. Strength is computed from state on every render.
The indicator updates in real-time with no extra code.

This is the definitive signal: **if you need real-time
feedback on the input value, use controlled.** If you
only need the value at submit time with no real-time
interaction, uncontrolled is simpler.

---

### 🧠 Mental Model / Analogy

> Controlled input is like a whiteboard where a teacher
> controls what is written. Students can only see what
> the teacher writes. If a student wants to add something,
> they hand a note to the teacher, who writes it on the
> board (onChange → setState → re-render with new value).
> The whiteboard always matches the teacher's record.
>
> Uncontrolled input is like a sticky note the student
> keeps at their desk. The teacher does not see it until
> the student hands it in (form submit reads ref.current).
> The teacher has no influence on what is written while
> the student is writing.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Controlled input: React controls what the input shows.
Uncontrolled input: the DOM controls what the input shows.
Use controlled when you need to know what the user is
typing as they type it. Use uncontrolled for simple
"submit and read" forms.

**Level 2 (usage):**
Controlled: `value={state}` + `onChange={e => setState(e.target.value)}`.
Uncontrolled: `ref={inputRef}` + read `inputRef.current.value`
on submit. Never mix `value` with no `onChange` - this
produces a read-only input (React warning).

**Level 3 (mechanism):**
React intercepts form events through its synthetic event
system. For controlled inputs, React's reconciler ensures
the input's DOM value matches state after every render.
If the user types faster than the state updates (which
is visible in slow rendering), the input value temporarily
diverges, then React snaps it back to state. This is why
extremely slow controlled input renders can feel laggy.

**Level 4 (architecture):**
The choice between controlled and uncontrolled is a
spectrum. Libraries like React Hook Form and Formik
abstract this: React Hook Form defaults to uncontrolled
(using native browser validation and `ref`-based reads
for performance - fewer re-renders for large forms).
Formik defaults to controlled (full state management,
real-time validation). Understanding the underlying model
explains why React Hook Form is faster for large forms
and why Formik has richer real-time validation support.

**Level 5 (mastery):**
React 18 concurrent features interact with controlled
inputs in subtle ways. In concurrent rendering, React
may pause and restart renders. For controlled inputs,
this could theoretically cause the input value to "jump"
if a high-priority render interrupts a low-priority one.
React handles this via the "entanglement" mechanism: input
value synchronisation is always treated as high-priority
to prevent visible lag. This is part of why controlled
inputs in React 18 still feel responsive even in concurrent
mode.

---

### ⚙️ How It Works (Mechanism)

**Controlled input variants:**

```jsx
// Text input
const [name, setName] = useState('');
<input value={name} onChange={e => setName(e.target.value)} />

// Textarea
const [bio, setBio] = useState('');
<textarea value={bio} onChange={e => setBio(e.target.value)} />

// Select
const [country, setCountry] = useState('US');
<select value={country} onChange={e => setCountry(e.target.value)}>
  <option value="US">United States</option>
  <option value="UK">United Kingdom</option>
</select>

// Checkbox
const [agreed, setAgreed] = useState(false);
<input
  type="checkbox"
  checked={agreed}   // note: "checked", not "value"
  onChange={e => setAgreed(e.target.checked)}
/>

// File input: CANNOT be controlled
// (browser security: value cannot be set by JS)
// Always uncontrolled:
const fileRef = useRef(null);
<input type="file" ref={fileRef} />
// Read: fileRef.current.files[0]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CONTROLLED FORM SUBMIT:**

```
1. User types "alice@example.com" in email input
2. Each keystroke: onChange → setEmail(value)
3. React re-renders on each keystroke
4. input.value = email state (stays in sync)
5. User clicks submit
6. onSubmit: reads email from state (already available)
7. Calls API with email
```

**UNCONTROLLED FORM SUBMIT:**

```
1. User types "alice@example.com" in email input
2. No React state updates (typing updates DOM only)
3. No re-renders during typing
4. User clicks submit
5. onSubmit: reads emailRef.current.value from DOM
6. Calls API with value
```

---

### 💻 Code Example

**BAD: Read-only input (value without onChange):**

```jsx
// BAD: value without onChange = read-only, user can't type
function Profile({ user }) {
  return (
    // value prop set, no onChange → React locks the value
    // User types → React resets to user.email → can't edit
    // React Warning: "provide an onChange handler"
    <input value={user.email} />
  );
}
```

**GOOD: Correctly controlled input:**

```jsx
// GOOD: controlled with onChange
function EditProfile({ user }) {
  const [email, setEmail] = useState(user.email);

  return (
    <input
      value={email}                                  // controlled
      onChange={e => setEmail(e.target.value)}       // updater
      placeholder="Email address"
    />
  );
}
```

**PRODUCTION: Large form with uncontrolled for performance:**

```jsx
// Uncontrolled form: reads all values on submit
// No re-renders while typing (better for 20+ field forms)
function SurveyForm({ onSubmit }) {
  const formRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const values = Object.fromEntries(formData.entries());
    onSubmit(values);
  };

  return (
    <form ref={formRef} onSubmit={handleSubmit}>
      <input name="name" defaultValue="" />
      <input name="email" type="email" defaultValue="" />
      <textarea name="comments" defaultValue="" />
      <input name="newsletter" type="checkbox" />
      <button type="submit">Submit</button>
    </form>
  );
}
// No state, no onChange handlers, no re-renders while typing
// FormData API reads all named inputs at submit time
```

---

### 📊 Comparison Table

| Feature | Controlled | Uncontrolled |
|---|---|---|
| State location | React state | DOM |
| Re-render on type | Yes (every keystroke) | No |
| Real-time validation | Yes | No (only on submit) |
| Programmatic value set | Yes (setState) | Limited (defaultValue once) |
| Read current value | From state | Via ref.current.value |
| Boilerplate per field | More (value + onChange) | Less (just ref or name) |
| Best for | Validated, interactive forms | Simple submit-only forms |
| Library preference | Formik | React Hook Form |
| File inputs | Cannot be controlled | Always uncontrolled |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`value` without `onChange` is fine for display-only inputs" | React will warn: "You provided a `value` prop to a form field without an `onChange` handler." This produces a read-only input that the user cannot edit. Use `readOnly` prop for intentional read-only inputs, or `defaultValue` for uncontrolled initial values. |
| "Uncontrolled is always faster" | Uncontrolled avoids re-renders during typing but still re-renders the full component tree when any other state changes. For complex forms embedded in re-rendering parents, both approaches re-render equally for non-typing state changes. |
| "You must choose: all controlled or all uncontrolled in a form" | You can mix. A form might control some fields (for real-time validation) and leave others uncontrolled (file inputs must be uncontrolled). React Hook Form uses this mixed approach internally. |
| "defaultValue and value are interchangeable" | `defaultValue` sets the initial value for an uncontrolled input and is NOT updated by React after mount. `value` sets the current value for a controlled input and IS updated by React on every render. They serve different purposes. |

---

### 🚨 Failure Modes & Diagnosis

**Input Not Responding to Typing (Read-Only)**

**Symptom:** User types and nothing appears. Cursor moves
but characters don't show. React console warning about
`value` without `onChange`.

**Root Cause:** `value` prop set without `onChange`. React
resets the input to `value` on every render, overriding
what was typed.

**Fix:** Add `onChange={e => setState(e.target.value)}`.
Or switch to `defaultValue` for uncontrolled behaviour.

---

**Uncontrolled Input State Lost After Re-render**

**Symptom:** User types in a form. Some unrelated button
click causes a re-render. The typed text disappears.

**Root Cause:** The component unmounts and remounts on
the re-render (key change, conditional rendering). Uncontrolled
input state lives in the DOM. When the DOM element is
removed and recreated, typed text is lost.

**Fix:** Use controlled inputs (typed text survives in
React state). Or ensure the input element is not
conditionally unmounted.

---

### 🔗 Related Keywords

**Prerequisites:**
- `State` and `useState Hook` - the source of truth in
  controlled components
- `Event Handling` - `onChange` that drives controlled inputs
- `useRef Hook` - the access mechanism for uncontrolled inputs

**Builds On:**
- `Form Handling in React` - applying controlled/uncontrolled
  in complete form patterns with validation
- `React Hook Form` - library that defaults to uncontrolled
  for performance

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONTROLLED  │ value={state} + onChange={setter}         │
│ UNCONTROLLED│ ref={inputRef}, read .current.value       │
│ DEFAULT VAL │ defaultValue="x" (uncontrolled initial)   │
├──────────────────────────────────────────────────────────┤
│ CHECKBOX    │ checked={bool} + onChange={checker}       │
│ FILE INPUT  │ ALWAYS uncontrolled (browser restriction) │
├──────────────────────────────────────────────────────────┤
│ USE         │ Controlled: real-time validation, complex │
│ CONTROLLED  │ interactions, programmatic value sets     │
│ USE         │ Uncontrolled: simple submit-only forms,  │
│ UNCONTROLLED│ large forms (performance), file inputs    │
├──────────────────────────────────────────────────────────┤
│ WARNING     │ value + no onChange = read-only input     │
│             │ use readOnly prop for intentional readonly│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Controlled: `value={state} + onChange` - React owns
   the value, real-time access to what user typed.
2. Uncontrolled: `ref={inputRef}` - DOM owns the value,
   read `inputRef.current.value` on submit.
3. `value` without `onChange` = read-only input (React
   warning). File inputs cannot be controlled at all.

**Interview one-liner:**
"Controlled inputs (`value={state}` + `onChange`) make
React state the source of truth - every keystroke updates
state, enabling real-time validation. Uncontrolled inputs
(`ref={inputRef}`) let the DOM manage value and are read
on submit via `ref.current.value`. Controlled is the React
standard; uncontrolled is faster for large submit-only
forms. A `value` prop without `onChange` creates a
read-only input (React warns). File inputs cannot be
controlled."

---

### 💎 Transferable Wisdom

The controlled vs uncontrolled distinction is a specific
case of "push vs pull" state management: controlled pushes
value updates on every change (React state is always
current), uncontrolled pulls the value when needed (on
submit). This pattern appears throughout systems: push-
based notifications vs pull-based polling, reactive
databases vs query-on-demand, event streaming vs batch
processing. The right choice depends on how frequently
the downstream consumer needs the current value and the
cost of updates.

---

### 💡 The Surprising Truth

React's controlled input model (`value` + `onChange`) is
actually two one-way bindings: state → DOM value (the
`value` prop), and DOM event → state (the `onChange`).
It is NOT two-way binding - React deliberately implemented
it as two explicit one-way flows. This is why the React
docs say "This is sometimes called a 'controlled
component.'" The illusion of two-way binding comes from
the fact that both directions are wired, but each direction
is explicit and unidirectional. Vue's `v-model` and
Angular's `[(ngModel)]` are syntactic sugar for the same
pattern - they are also two one-way bindings, just with
shorter syntax.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a complete registration form with three
   controlled inputs (name, email, password), real-time
   validation that shows error messages as you type, and
   a submit handler that calls an API.
2. **EXPLAIN** why `<input value="hello" />` produces a
   read-only input and React's warning about it. What
   are the two correct alternatives?
3. **COMPARE** the implementation of the same form using
   controlled state vs React Hook Form (uncontrolled),
   and explain when each is the better choice.
4. **DIAGNOSE** a bug where user-typed text disappears
   after a button click causes a parent re-render - identify
   whether the cause is controlled or uncontrolled state,
   and the correct fix.
5. **EXPLAIN** why file inputs (`<input type="file">`)
   cannot be controlled in React, and how to read the
   selected file.

---

### 🧠 Think About This Before We Continue

**Q1.** A checkout form has 15 fields. The user must fill
all of them. Validation should show errors only when
the user submits (not while typing). Which approach -
controlled or uncontrolled - is better for this form,
and what changes if the product team later adds "show
error as you leave each field" (on blur validation)?

**Q2.** React Hook Form is often described as significantly
faster than Formik for large forms. Both produce the same
UX outcome. The performance difference comes from
controlled vs uncontrolled architecture. Formik uses
controlled state (re-renders on every keystroke). React
Hook Form uses uncontrolled refs (no re-renders while
typing). At what point does this performance difference
become visible to users, and is it worth the complexity
trade-off?

**Q3.** Some forms need to programmatically set values:
an "autofill from profile" button that populates all
fields from the user's saved data. This is easy with
controlled inputs (`setState(profileData)`). How would
you implement this with uncontrolled inputs (no state),
and what React APIs would you use?