---
layout: default
title: "React Accessibility (a11y)"
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /react/react-accessibility-a11y/
id: RCT-006
category: React
difficulty: ★★★
depends_on: React, HTML, ARIA
used_by: React, Testing
related: WCAG, ESLint (React), Semantic HTML
tags:
  - react
  - frontend
  - browser
  - bestpractice
  - advanced
---

# RCT-006 - React Accessibility (a11y)

⚡ **TL;DR -** Build React UIs usable by everyone - including screen reader, keyboard, and switch-control users - through semantic HTML, ARIA, and focus management.

| Relationship | Keywords |
|---|---|
| **Depends on** | React, HTML, ARIA |
| **Used by** | React, Testing |
| **Related** | WCAG, ESLint (React), Semantic HTML |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You build a feature-rich React app with custom dropdowns, modals, and icon buttons. It looks great on screen. A blind user with NVDA cannot tab to your modal, cannot hear what the icon button does, and cannot close the dialog with Escape. A motor-impaired user cannot reach the dropdown without a mouse. Your app is legally unusable for 15–20% of users.

**THE BREAKING POINT:**
React's component model lets you render any HTML element as an interactive control. A `<div onClick={...}>` looks like a button but has no role, no keyboard access, and no accessible name. At scale, teams ship dozens of these without realising the depth of the damage. Automated visual tests pass. Screen reader users cannot use the product.

**THE INVENTION MOMENT:**
The W3C published WCAG to define what "accessible" means. The HTML spec defined semantic elements. The ARIA specification filled gaps for custom widgets. The React community built `eslint-plugin-jsx-a11y` to catch violations at dev time and axe-core to test them at runtime. Accessibility is a first-class engineering discipline, not a visual polish step.

---

### 📘 Textbook Definition

**React Accessibility (a11y)** is the practice of building React components that comply with WCAG guidelines and ARIA authoring patterns so that assistive technologies - screen readers, switch controls, keyboard-only navigation, and voice control - can fully operate the UI. It requires semantic HTML, ARIA roles and attributes, focus management, keyboard event handling, and live region announcements for dynamic content.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Make every interactive element reachable, operable, and understandable without a mouse or sight.

> A screen reader is like a phone tour guide reading your city aloud. If your buildings have no street signs (labels), hidden doors (no tab order), and soundproof lobbies (no focus management), the guide cannot help visitors navigate.

**One insight:** Every `<div onClick>` you write is a silent exclusion of keyboard and screen-reader users. Semantic HTML and ARIA are structural contracts that make inclusion automatic.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every interactive element must be reachable by keyboard (`Tab`, arrow keys).
2. Every element must have an accessible name (visible text, `aria-label`, or `aria-labelledby`).
3. Dynamic content changes must be announced to screen readers via live regions.
4. Focus must be managed when UI state changes (modals open/close, route changes).
5. Color alone must not convey meaning; contrast ratio ≥ 4.5:1 for WCAG AA.

**DERIVED DESIGN:**
Use native semantic HTML first - `<button>`, `<a>`, `<input>`, `<nav>`, `<main>` - they carry role, focusability, and keyboard behaviour for free. Add ARIA only where native semantics are insufficient. Use `aria-live` regions to announce async updates (form errors, toast messages). Move focus explicitly on route change, modal open, and modal close.

**THE TRADE-OFFS:**

**Gain:** Inclusive product, legal compliance (ADA, EN 301 549), better SEO, better keyboard UX for power users, reduced legal liability.

**Cost:** Component complexity increases (focus traps, keyboard handlers, ARIA state management). Testing surface grows. Design and engineering must co-design accessible patterns from the start.

---

### 🧪 Thought Experiment

**SETUP:** You have a custom `<Dropdown>` built entirely from `<div>` elements with click handlers. It opens on click and selects items by clicking. Works perfectly with a mouse.

**WHAT HAPPENS WITHOUT React a11y:**
A keyboard user presses `Tab` - focus skips the dropdown entirely. A screen reader announces nothing when the dropdown opens. A motor-impaired user cannot operate it at all. Your QA passes visually. You ship. Your app fails WCAG 2.1 Level AA.

**WHAT HAPPENS WITH React a11y:**
The trigger is a `<button>` with `aria-haspopup="listbox"` and `aria-expanded={isOpen}`. The list has `role="listbox"` and each option has `role="option"` with `aria-selected`. Arrow keys move focus between options; `Escape` closes and returns focus to the trigger. A `useEffect` moves focus into the list when it opens. axe-core in CI catches any regression before it ships.

**THE INSIGHT:** Accessibility is not a visual test. It is a contract between your component's DOM structure and the browser's accessibility tree. You must write code for the tree, not just the screen.

---

### 🧠 Mental Model / Analogy

> Think of your React app as a building. Sighted mouse users use the front entrance and elevators. Accessible design adds ramps (keyboard navigation), braille signage (accessible names), intercoms at every door (aria-label), and automatic floor announcements (aria-live).

- **Ramps** → `tabIndex`, native focusable elements
- **Braille signage** → `aria-label`, `aria-labelledby`
- **Intercoms** → ARIA roles (`role="button"`, `role="dialog"`)
- **Floor announcements** → `aria-live` regions
- **Emergency exits** → Escape key closes modals, focus returns to trigger

Where this analogy breaks down: A building is static; React UIs are dynamic. Focus management after state changes has no physical equivalent - it requires deliberate imperative code.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Accessibility means your website works for people who cannot see it, cannot use a mouse, or have other disabilities. About 1 in 6 people has some form of disability. A11y makes sure everyone can use your app - not just people with perfect vision and a mouse.

**Level 2 - How to use it (junior developer):**
Use HTML elements that already carry meaning: `<button>` instead of `<div onClick>`, `<nav>` for navigation, `<img alt="...">` for images. Add `aria-label` when there is no visible text. Install `eslint-plugin-jsx-a11y` to catch violations while you code. Run `axe-core` to test components.

**Level 3 - How it works (mid-level engineer):**
Browsers expose an **accessibility tree** - a parallel structure derived from the DOM that assistive technologies query (not the visual DOM). ARIA roles and attributes modify accessibility tree nodes without changing visual appearance. Focus management requires `useRef` + `element.focus()`. Focus trapping in dialogs requires intercepting Tab and Shift+Tab. Test with `jest-axe` (unit), `@axe-core/react` (dev overlay), and real screen readers (NVDA, VoiceOver).

**Level 4 - Why it was designed this way (senior/staff):**
The accessibility tree is the browser's abstraction layer between DOM and assistive technology. ARIA was designed to describe widget semantics that predate HTML5 semantic elements. React's synthetic event system does not break accessibility inherently, but JSX's freedom to compose arbitrary DOM creates a pit of failure. The WAI-ARIA Authoring Practices Guide defines invariant keyboard interaction patterns per widget type (combobox, listbox, dialog, tabs). The engineering discipline is encoding these invariants into reusable hook and component abstractions - `useFocusTrap`, `useDialog`, `useFocusReturn` - so application code cannot accidentally violate them.

---

### ⚙️ How It Works (Mechanism)

```
Browser rendering pipeline:

  JSX → DOM → Accessibility Tree
               ↕
          Screen Reader
          Keyboard Nav
          Switch Control
```

1. React renders JSX → real DOM elements.
2. Browser builds the **accessibility tree** from DOM semantics and ARIA attributes.
3. Assistive technologies query the accessibility tree, not the DOM or CSS.
4. Native elements (`button`, `input`) automatically map to tree nodes with role, name, and state.
5. `aria-*` attributes override or augment tree node properties.
6. `aria-live` regions trigger announcements when their text content changes.
7. `tabIndex` and `element.focus()` control the keyboard navigation order.

```
Accessibility Tree Node:
+---------------------------+
| role:    button           |
| name:    "Close dialog"   |
| state:   disabled=false   |
| focused: true             |
+---------------------------+
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
User presses Tab
  → Browser moves focus to next focusable element
    → Accessibility tree node receives focus
      → Screen reader announces role + name + state
        → User presses Enter or Space        ← YOU ARE HERE
          → click or keydown event fires
            → State updates, UI changes
              → aria-live region announces change
```

**FAILURE PATH:**
```
<div onClick={open}> - is it focusable? NO
  → User presses Tab → focus skips element
    → Screen reader announces: nothing
      → User cannot discover or operate control
        → Feature is completely inaccessible
```

**WHAT CHANGES AT SCALE:**
At 100+ components, manual ARIA audits break down. Teams adopt: (1) `eslint-plugin-jsx-a11y` in CI to block violations at PR time, (2) Storybook a11y addon for component-level audits, (3) `axe-core` integration tests on critical flows (login, checkout), (4) quarterly audits with real AT users, and (5) an accessible component library that encapsulates patterns.

---

### 🔁 Flow / Lifecycle

**Accessible Component Development Lifecycle:**

```
1. DESIGN
   UX defines keyboard flow, focus order,
   and screen reader copy alongside visuals.

2. BUILD
   Use semantic HTML first.
   Add ARIA only where native fails.
   Implement keyboard handlers and focus mgmt.

3. LINT (eslint-plugin-jsx-a11y)
   Catches missing labels, interactive non-
   focusable elements, invalid ARIA at save time.

4. TEST
   jest-axe: unit a11y assertions per component.
   @axe-core/react: overlay in dev browser.
   Screen reader smoke test: NVDA/VoiceOver.

5. CI GATE
   axe-core integration test suite runs in CI.
   Violations block PR merge.

6. AUDIT
   Quarterly: manual audit with real AT users.
   Findings feed back to Design step.
```

---

### 💻 Code Example

**BAD - inaccessible icon button and modal:**
```tsx
// ❌ div-button: no role, no keyboard, no name
function BadButton({ onClick }: { onClick: () => void }) {
  return (
    <div style={{ cursor: 'pointer' }} onClick={onClick}>
      <img src="/icons/close.svg" />
    </div>
  );
}

// ❌ modal: no role, no focus trap, no accessible name
function BadModal({ isOpen }: { isOpen: boolean }) {
  if (!isOpen) return null;
  return (
    <div className="modal">
      <h2>Confirm action</h2>
      <div onClick={() => {}}>OK</div>
    </div>
  );
}
```

**GOOD - accessible button and modal with focus management:**
```tsx
import { useEffect, useRef } from 'react';

// ✅ Semantic button with accessible name
function CloseButton({ onClick }: { onClick: () => void }) {
  return (
    <button type="button" aria-label="Close dialog"
      onClick={onClick}>
      {/* aria-hidden hides decorative icon from AT */}
      <img src="/icons/close.svg" aria-hidden="true" />
    </button>
  );
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

// ✅ Accessible dialog with focus management
function AccessibleModal({
  isOpen, onClose, title, children
}: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Move focus into dialog when it opens
    if (isOpen) dialogRef.current?.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  };

  return (
    <div
      role="presentation"
      style={{ position: 'fixed', inset: 0,
        background: 'rgba(0,0,0,0.5)' }}
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        tabIndex={-1}
        onKeyDown={handleKeyDown}
        onClick={(e) => e.stopPropagation()}
        style={{ background: 'white', padding: '24px',
          borderRadius: '8px', maxWidth: '480px',
          margin: '10vh auto' }}
      >
        <h2 id="dialog-title">{title}</h2>
        {children}
        <CloseButton onClick={onClose} />
      </div>
    </div>
  );
}
```

**Testing with jest-axe:**
```tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('Modal has no a11y violations when open', async () => {
  const { container } = render(
    <AccessibleModal
      isOpen={true}
      onClose={() => {}}
      title="Confirm"
    >
      <p>Are you sure?</p>
    </AccessibleModal>
  );
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

### ⚖️ Comparison Table

| Approach | Keyboard | Screen Reader | WCAG Level | Effort |
|---|---|---|---|---|
| Semantic HTML only | ✅ Auto | ✅ Auto | AA | Low |
| ARIA on `<div>` | Manual | ✅ If correct | AA | High |
| Custom `useDialog` hook | ✅ Via hook | ✅ Via hook | AA | Medium |
| Radix UI / Headless UI | ✅ Built-in | ✅ Built-in | AA | Low |
| react-aria (Adobe) | ✅ Built-in | ✅ Built-in | AA+ | Low |
| No a11y work | ❌ | ❌ | Fails | None |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "ARIA fixes everything" | Semantic HTML is always preferred. ARIA repairs gaps; it cannot replace native semantics. `role="button"` on a `<div>` still needs manual keyboard handling and focus management. |
| "Adding `tabIndex={0}` is enough" | `tabIndex` makes an element focusable but gives it no role, name, or keyboard behaviour. A `<div tabIndex={0}>` is still not a button - it needs `role="button"` and `onKeyDown` for Enter/Space. |
| "Accessibility is for blind users only" | 1 in 6 people has a disability: motor, cognitive, temporary (broken arm), situational (bright sunlight, one hand occupied). Everyone benefits from keyboard nav and good labelling. |
| "Automated tools catch all violations" | axe-core and `eslint-plugin-jsx-a11y` catch ~30–40% of WCAG violations. Colour contrast, logical reading order, and complex widget interactions require manual testing with real AT. |
| "We'll add a11y at the end of the project" | Retrofitting accessibility into an existing component library costs 5–10× more than building it in from the start. Focus management and keyboard patterns must be designed, not bolted on. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1 - Missing accessible name on icon button**

**Symptom:** Screen reader announces "button" with no description. Users cannot determine the button's purpose without visual context.

**Root Cause:** Icon-only button with no `aria-label`, no visible text, and no `aria-labelledby`.

**Diagnostic:**
```bash
# Run axe-core CLI audit against dev server
npx @axe-core/cli http://localhost:3000

# Typical output:
# Violation: "Buttons must have discernible text"
# Element: <button><img src="/icons/close.svg"></button>
# Rule: button-name
```

**Fix:**
```tsx
// BAD
<button onClick={close}>
  <XIcon />
</button>

// GOOD
<button onClick={close} aria-label="Close dialog">
  <XIcon aria-hidden="true" />
</button>
```

**Prevention:** Enable `jsx-a11y/interactive-supports-focus` and `jsx-a11y/aria-proptypes` ESLint rules. Require all icon buttons to have `aria-label` in the component API contract.

---

**Failure Mode 2 - Focus lost after modal closes**

**Symptom:** After closing a modal, keyboard focus disappears to `<body>`. The user must Tab from the start of the page to find their place.

**Root Cause:** Modal unmounts without restoring focus to the trigger element that opened it.

**Diagnostic:**
```tsx
// Manual test: open modal, press Escape.
// Then check in browser console:
console.log(document.activeElement);
// Expected: <button id="open-modal">
// Actual:   <body>  ← focus lost
```

**Fix:**
```tsx
// Capture trigger before opening; restore on close
const triggerRef = useRef<HTMLButtonElement>(null);

const handleClose = () => {
  setOpen(false);
  // Explicitly return focus to trigger
  triggerRef.current?.focus();
};

<button ref={triggerRef} onClick={() => setOpen(true)}>
  Open settings
</button>
```

**Prevention:** Wrap focus return logic in a reusable `useFocusReturn` hook that captures `document.activeElement` on mount and calls `.focus()` on unmount.

---

**Failure Mode 3 - Async content not announced to screen readers**

**Symptom:** A form error appears visually after API failure but screen reader users never hear it. They cannot understand why the submit failed.

**Root Cause:** Error message renders into a plain `<div>` with no `aria-live` attribute.

**Diagnostic:**
```tsx
// In Chrome DevTools → Accessibility tab:
// Inspect the error container element.
// Check Properties: aria-live is absent.
// Screen reader fires no announcement on text change.
```

**Fix:**
```tsx
// BAD: plain div - screen reader silent
<div className="error">{errorMessage}</div>

// GOOD: assertive live region for form errors
<div
  role="alert"
  aria-live="assertive"
  aria-atomic="true"
>
  {errorMessage}
</div>
```

**Prevention:** Create a shared `<LiveRegion>` or `<Alert>` component used for all async messages. Include `aria-live` tests in the form's `jest-axe` test suite.

---

**Failure Mode 4 - Keyboard trap in custom dropdown**

**Symptom:** User opens dropdown with keyboard, navigates in, then cannot exit with Tab or Escape. Focus is permanently trapped inside.

**Root Cause:** `onKeyDown` handler calls `preventDefault` but does not implement arrow/Escape navigation, and `stopPropagation` blocks browser Tab.

**Diagnostic:**
```bash
# Manual keyboard test:
# 1. Tab to dropdown trigger. Press Enter.
# 2. Press Escape → should close + return focus.
# 3. Press Tab → should close + move forward.
# If neither works: inspect onKeyDown handler.
# Look for e.stopPropagation() on all keys.
```

**Fix:**
```tsx
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Escape') {
    setOpen(false);
    triggerRef.current?.focus();
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    focusNextOption();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    focusPrevOption();
  }
  // Do NOT call stopPropagation on Tab key
};
```

**Prevention:** Use Radix UI `<Select>` or Headless UI `<Listbox>` which implement full WAI-ARIA keyboard patterns. Avoid building custom compound widgets from scratch.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- React - component model, JSX rendering, and the `useRef` + `useEffect` hooks
- HTML - semantic elements and their native accessibility semantics
- ARIA - roles, states, properties, live regions, and the WAI-ARIA spec

**Builds On This (learn these next):**
- ESLint (React) - lint-time enforcement via `eslint-plugin-jsx-a11y`
- Testing - axe-core integration tests and screen reader smoke tests
- WCAG - the full normative standard defining success criteria for every rule

**Alternatives / Comparisons:**
- Radix UI / Headless UI - unstyled component libraries with a11y built-in
- react-aria (Adobe) - hooks implementing complete WAI-ARIA patterns
- Reach UI - accessible React primitives (now largely superseded by Radix)

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS   | React UIs operable by all users        |
| PROBLEM      | JSX lets you build inaccessible UIs     |
| KEY INSIGHT  | Code for the a11y tree, not the screen  |
| USE WHEN     | Every React UI - a11y is never optional  |
| AVOID WHEN   | Never skip - use Radix if complex       |
| TRADE-OFF    | More code; primitives reduce the burden |
| ONE-LINER    | Semantic HTML first, ARIA second, test  |
| NEXT EXPLORE | WCAG, ESLint (React), jest-axe          |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction - Type A)** A screen reader user navigates to a new route in your SPA via a `<Link>` click. The URL changes but the screen reader announces nothing. What browser mechanism is missing, what React API would you use to announce the new page title, and where in the component tree would you place it?

2. **(Scale - Type B)** Your team has 80 React components across 5 feature areas with no existing a11y testing. You have one sprint to make progress. Describe a triage strategy that delivers the highest a11y impact first without halting ongoing feature work.

3. **(Design Trade-off - Type C)** Radix UI provides fully accessible primitives with limited visual customisation. A custom-built dropdown gives full design control but requires implementing all WAI-ARIA keyboard patterns manually. What factors determine which approach you choose, and what is the long-term maintenance cost of each?
