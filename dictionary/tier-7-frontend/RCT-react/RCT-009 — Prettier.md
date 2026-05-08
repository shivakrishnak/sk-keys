---
layout: default
title: "Prettier"
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /react/prettier/
id: RCT-009
category: React
difficulty: ★☆☆
depends_on: JavaScript, TypeScript, Code Quality
used_by: CI-CD, React
related: ESLint (React), EditorConfig, Husky
tags:
  - javascript
  - typescript
  - cicd
  - foundational
  - bestpractice
---

# RCT-009 — Prettier

⚡ **TL;DR —** Prettier auto-formats code to one opinionated style, permanently ending formatting debates and noisy diff reviews across the entire team.

| Relationship | Keywords |
|---|---|
| **Depends on** | JavaScript, TypeScript, Code Quality |
| **Used by** | CI-CD, React |
| **Related** | ESLint (React), EditorConfig, Husky |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every PR review contains comments like "indent with 2 spaces, not 4", "add a trailing comma", "no space before the bracket". Senior engineers spend ten minutes per PR on formatting. Git blame is full of whitespace-only commits. A developer reformats the entire file to fix a two-line change, and the diff becomes unreadable. The team argues for two hours in a style guide meeting and still does not fully agree.

**THE BREAKING POINT:**
Code style is a solved problem — but it costs teams hours of review time and generates friction that slows down real work. The cost is invisible because it is spread across hundreds of small interactions. It is not until you measure that you realise the entire team wasted 10% of review capacity on formatting opinions.

**THE INVENTION MOMENT:**
James Long published Prettier in 2017 with a radical design principle: **zero configurability by default**. Instead of being a style guide enforcer with hundreds of rules (like ESLint), Prettier parses source code into an AST, discards all original formatting, and reprints it from scratch according to one built-in algorithm. The result: every developer in every editor on every OS produces identical output. Formatting debates end permanently.

---

### 📘 Textbook Definition

**Prettier** is an opinionated code formatter for JavaScript, TypeScript, JSX, CSS, HTML, JSON, Markdown, and other formats. It parses source into an AST, applies a fixed line-length algorithm to determine where to break lines, and reprints the file. It is not a linter — it makes no judgements about code correctness or style preferences. It enforces exactly one output, making team formatting consistent without configuration debate.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Prettier reprints your code in one canonical style so you never argue about formatting again.

> Prettier is like a stamp press for code. No matter what shape of metal you put in, it always stamps out the same coin. Every developer's output looks like the same developer wrote it.

**One insight:** Prettier's value is not in the style it chooses — it is in the fact that it chooses exactly one style, non-negotiably. The specific style matters far less than having no style debate at all.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Prettier parses code to an AST — original whitespace is discarded entirely.
2. Prettier's algorithm reprints from the AST using a line-length fitting algorithm.
3. The same input always produces the same output — it is deterministic.
4. Prettier has minimal config; most options are binary (e.g., semicolons: yes/no).
5. Prettier is not a linter — it does not report errors, it rewrites files.

**DERIVED DESIGN:**
The reprinting algorithm uses a document intermediate representation (IR) that models groups of tokens and their possible line-break configurations. The fitting algorithm walks the IR and decides, for each group, whether its tokens fit on the current line. If they fit, it joins them; if not, it breaks at the specified break points. This produces consistent multi-line formatting without requiring rules for every case.

**THE TRADE-OFFS:**

**Gain:** Zero formatting debates in PR review. Consistent diffs that show only logic changes. On-save formatting means developers never think about style. New team members instantly match the codebase style.

**Cost:** Prettier's output is opinionated and occasionally produces aesthetically displeasing results that cannot be overridden. Teams must accept Prettier's choices or not use it — partial use is worse than no use. The initial "big bang" commit that formats the entire codebase disrupts `git blame`.

---

### 🧪 Thought Experiment

**SETUP:** A team of six developers works on a React codebase. Three prefer single quotes, two prefer double quotes, one uses backticks. Two indent with 2 spaces, two with 4, one with tabs. They have a style guide document that nobody reads.

**WHAT HAPPENS WITHOUT Prettier:**
Every PR has at least two formatting comments. Developers regularly reformat entire files when touching them, making diffs unreadable. `git blame` shows that 30% of lines were last touched in whitespace-only commits. A new developer joins, reads the style guide, and still formats differently from the rest of the team. The senior engineer spends Friday afternoon enforcing style.

**WHAT HAPPENS WITH Prettier:**
Prettier runs on save in every developer's editor. All six developers' editors produce identical output. The PR shows only the two lines that changed logic. `git blame` is clean. Onboarding a new developer takes zero style explanation. The style guide document is deleted. No formatting comment appears in a PR review again.

**THE INSIGHT:** Prettier does not produce the best style — it produces *a* style. The gain is not aesthetic quality; it is the permanent elimination of a class of team friction that costs hours per week.

---

### 🧠 Mental Model / Analogy

> Think of Prettier as the "gofmt" of the JavaScript ecosystem. Go developers cannot argue about formatting because `gofmt` is the only option. Prettier brings the same property to JavaScript: there is only one canonical format, and the machine enforces it without discussion.

- **gofmt** → Prettier (both parse-and-reprint, both non-negotiable)
- **rustfmt** → Prettier (same principle, different ecosystem)
- **`eslint --fix`** → Prettier (ESLint fixes linting violations; Prettier owns all formatting)
- **`prettier --check`** → `gofmt -l` (lists files that would change)
- **`prettier --write`** → `gofmt -w` (rewrites files in place)

Where this analogy breaks down: `gofmt` is a first-party Go tool with no configuration at all; Prettier has a small set of optional config (printWidth, semicolons, trailingComma) for teams that genuinely need them.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Prettier is a program that automatically formats your code. When you save a file, it tidies up the spacing, quotes, and line breaks so every file in your project looks the same — regardless of who wrote it.

**Level 2 — How to use it (junior developer):**
Run `npm install -D prettier`. Create a `.prettierrc` file with your team's options. Install the Prettier VS Code extension and enable "Format on Save". Run `npx prettier --write src/` to format all existing files. Add `npx prettier --check src/` to your CI pipeline to block unformatted code.

**Level 3 — How it works (mid-level engineer):**
Prettier uses language-specific parsers (Babel for JS/JSX, `@typescript-eslint/typescript-estree` for TypeScript) to produce an AST. It then converts the AST to its own intermediate representation of "doc" objects — groups, line breaks, indents. The Wadler-Lindig fitting algorithm walks this IR and decides where to break each group based on `printWidth`. The final output is reprinted from scratch. The original source is irrelevant to the output.

**Level 4 — Why it was designed this way (senior/staff):**
The parse-then-reprint architecture is Prettier's core insight. Earlier formatters (like `js-beautify`) modified the existing source tokens, which meant they preserved some original formatting — making the output dependent on input. Prettier's full-reprint model is idempotent: running Prettier twice produces the same result as running it once. This is the property that makes `prettier --check` reliable in CI. The line-length algorithm is a variant of Philip Wadler's "prettier printer" algorithm, designed to make optimal decisions about line breaks in polynomial time rather than exponential. This is why Prettier is both fast and consistent.

---

### ⚙️ How It Works (Mechanism)

```
Source file
    ↓
Parser (Babel / TS-estree / etc.)
    ↓
  AST (original whitespace discarded)
    ↓
Doc Builder (AST → IR of groups + breaks)
    ↓
Wadler-Lindig Fitting Algorithm
  (fits tokens into printWidth constraint)
    ↓
Output (canonical formatted source)
```

**Line-length fitting example:**
```
Input:   const x = { foo: 'a', bar: 'b', baz: 'c' }
Width:   40 chars

Fits on one line? YES (35 chars) → keep inline:
  const x = { foo: 'a', bar: 'b', baz: 'c' }

Width:   20 chars — does NOT fit → break group:
  const x = {
    foo: 'a',
    bar: 'b',
    baz: 'c',
  }
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes JSX / TypeScript
  → saves file in VS Code
    → "Format on Save" triggers Prettier
      → file reprinted in canonical style
        → developer continues     ← YOU ARE HERE
          → git add (lint-staged runs)
            → prettier --write on staged files
              → git commit succeeds
                → CI: prettier --check passes
                  → PR merged; diff is logic-only
```

**FAILURE PATH:**
```
Developer has "Format on Save" disabled
  → commits unformatted code
    → CI: prettier --check detects difference
      → Exit code 1 → pipeline fails
        → PR blocked
          → Developer runs: npx prettier --write src/
            → Stages formatted files → re-pushes
```

**WHAT CHANGES AT SCALE:**
At 50+ developers across time zones, "Format on Save" cannot be relied upon. Teams enforce formatting via Husky pre-commit hooks (`lint-staged` runs `prettier --write`) and CI `--check`. A one-time "big bang" formatting commit is created on a dedicated branch, merged during a low-traffic window, and documented so `git blame --ignore-rev` can skip it.

---

### 🔁 Flow / Lifecycle

**Prettier Enforcement Pipeline:**

```
1. INSTALL
   npm install -D prettier
   Create .prettierrc (options) and .prettierignore.

2. EDITOR (on save)
   VS Code Prettier extension formats on save.
   EditorConfig provides baseline whitespace settings
   that Prettier respects for non-Prettier files.

3. COMMIT (lint-staged + Husky)
   Husky pre-commit hook triggers lint-staged.
   lint-staged runs: prettier --write on staged files.
   Re-stages formatted files before commit finalises.
   Developers who skip "Format on Save" are caught here.

4. CI CHECK (required gate)
   prettier --check src/ fails if any file differs
   from Prettier's expected output. Exit code 1.
   PR cannot merge until all files are formatted.

5. MERGE
   Every merged file has identical canonical formatting.
   Code review diffs contain only logic changes.
   git blame reflects real authorship, not formatting.
```

---

### 💻 Code Example

**`.prettierrc` — team configuration:**
```json
{
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "jsxSingleQuote": false,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "always"
}
```

**`.prettierignore` — exclude generated and vendor files:**
```
# Build outputs
dist/
build/
coverage/

# Generated files
src/generated/
*.min.js

# Package manager
node_modules/
```

**BAD — inconsistent formatting before Prettier:**
```tsx
const Button=({label,onClick}:{label:string,onClick:()=>void})=>{
return(<button
onClick={onClick}
style={{padding:"8px 16px",background:"blue",color:"white"}}
>{label}</button>)
}
```

**GOOD — canonical output after Prettier:**
```tsx
const Button = ({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) => {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '8px 16px',
        background: 'blue',
        color: 'white',
      }}
    >
      {label}
    </button>
  );
};
```

**Husky + lint-staged pre-commit hook:**
```bash
# Install
npm install -D husky lint-staged
npx husky init
```

```js
// .lintstagedrc.js
export default {
  // Format JS/TS/JSX/TSX on commit
  '**/*.{js,jsx,ts,tsx}': [
    'prettier --write',
    'eslint --fix --max-warnings 0',
  ],
  // Format JSON, CSS, Markdown too
  '**/*.{json,css,md}': ['prettier --write'],
};
```

```bash
# .husky/pre-commit (generated by husky init)
npx lint-staged
```

**CI check (`package.json` scripts):**
```json
{
  "scripts": {
    "format:check": "prettier --check src/",
    "format:write": "prettier --write src/",
    "lint": "eslint src/ --max-warnings 0"
  }
}
```

```yaml
# GitHub Actions step
- name: Check formatting
  run: npm run format:check
```

---

### ⚖️ Comparison Table

| Tool | Role | Configurable | Auto-Fix | Speed |
|---|---|---|---|---|
| Prettier | Formatter — reprints entire file | Minimal (8 options) | Yes (`--write`) | Fast |
| ESLint `--fix` | Fixes lint violations | Highly configurable | Partial | Medium |
| Biome | Formatter + linter (Rust) | Moderate | Yes | Very fast |
| EditorConfig | IDE whitespace baseline | Per-file-type | Via editor | N/A |
| `js-beautify` | Formatter (token-based) | Many options | Yes | Medium |
| `gofmt` | Go formatter (inspiration) | None | Yes | Very fast |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Prettier and ESLint do the same thing" | ESLint checks code correctness and style rules; Prettier handles only code formatting. They complement each other. `eslint-config-prettier` disables ESLint's formatting rules so they do not conflict. |
| "I can configure Prettier to match my preferred style" | Prettier intentionally limits config to a tiny set of binary options. If you want more control, Prettier is not the right tool. Partial configuration still produces opinionated output for everything else. |
| "Prettier makes code more readable" | Prettier makes code *consistently formatted* — readability depends on the code, not the formatter. Prettier can produce long chained expressions that are harder to read but technically correct. |
| "Running ESLint `--fix` is equivalent to Prettier" | ESLint `--fix` applies only to fixable lint rules, which cover a small subset of formatting. Prettier reprints the entire file from AST. The two produce different and often conflicting output without `eslint-config-prettier`. |
| "Once Prettier is set up, no more formatting issues" | Developers who skip editor integration or commit without lint-staged can still introduce unformatted code. CI `--check` is the only reliable enforcement point. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1 — Prettier and ESLint produce conflicting output**

**Symptom:** Running `eslint --fix` changes indentation to 4 spaces. Running `prettier --write` changes it back to 2. Every save triggers alternating changes. Developers disable one tool.

**Root Cause:** ESLint has formatting rules enabled (`indent`, `quotes`, `semi`) that conflict with Prettier's output.

**Diagnostic:**
```bash
# Identify conflicting ESLint rules:
npx eslint-config-prettier src/App.tsx

# Output example:
# The following rules are unnecessary or might
# conflict with Prettier:
# - indent
# - quotes
# - semi
# These should be turned off in your ESLint config.
```

**Fix:**
```js
// eslint.config.js — add prettier config LAST
import prettierConfig from 'eslint-config-prettier';

export default [
  // ... all other configs ...
  prettierConfig, // disables conflicting ESLint rules
];
```

**Prevention:** Always install `eslint-config-prettier` when using both tools. Make it the last entry in the ESLint config array. Never add formatting rules to ESLint in Prettier projects.

---

**Failure Mode 2 — CI formatting check fails for new contributors**

**Symptom:** A new developer opens a PR. CI fails with `prettier --check` errors on files they touched. The developer is confused — their editor showed no errors.

**Root Cause:** New developer's editor does not have the Prettier extension installed or "Format on Save" is disabled. The Husky pre-commit hook was not installed because they ran `npm install` after Husky's `prepare` script was removed or skipped.

**Diagnostic:**
```bash
# Reproduce locally:
npx prettier --check src/

# Output lists all files that differ:
# [warn] src/components/Button.tsx
# [warn] src/pages/Home.tsx
# [warn] Code style issues found in 2 files.
# Run Prettier to fix.
```

**Fix:**
```bash
# Developer runs locally to fix all files:
npx prettier --write src/

# Verify Husky hooks are installed:
ls .husky/
# Should contain: pre-commit

# Re-install if missing:
npx husky install
```

**Prevention:** Add `"prepare": "husky install"` to `package.json`. Document the VS Code extension requirement in `CONTRIBUTING.md`. Add a workspace `.vscode/extensions.json` recommending the Prettier extension.

---

**Failure Mode 3 — Prettier formats generated or vendored files**

**Symptom:** `prettier --write src/` modifies auto-generated GraphQL types, vendor bundles, or compiled output files. These modifications pollute `git status` and break generated file integrity checks.

**Root Cause:** `.prettierignore` does not exclude generated directories. Prettier formats every file it can parse, including machine-generated source.

**Diagnostic:**
```bash
# See which files Prettier would change:
npx prettier --check .

# If output includes generated files:
# [warn] src/generated/graphql.ts
# [warn] vendor/lib.js
# → Add these to .prettierignore
```

**Fix:**
```bash
# .prettierignore
src/generated/
vendor/
*.d.ts
coverage/
dist/
build/
```

**Prevention:** Create `.prettierignore` on project setup, before the first formatting run. Treat it as authoritative — review it when adding new code generation tools.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- JavaScript — syntax and AST structure that Prettier parses
- TypeScript — TypeScript parser used for `.ts` and `.tsx` formatting
- Code Quality — the broader discipline that Prettier and ESLint serve

**Builds On This (learn these next):**
- ESLint (React) — linting partner; `eslint-config-prettier` coordinates the two
- CI-CD — `prettier --check` as a required pipeline gate blocks unformatted PRs
- Husky — Git hook manager used to run Prettier automatically before every commit

**Alternatives / Comparisons:**
- Biome — Rust-based formatter + linter that replaces both Prettier and ESLint
- `dprint` — plugin-based fast formatter, more configurable than Prettier
- EditorConfig — editor-level whitespace baseline (works alongside Prettier)

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS   | Opinionated code formatter, not linter |
| PROBLEM      | Formatting debates waste review time   |
| KEY INSIGHT  | One style, no config, no debate        |
| USE WHEN     | Every JS/TS project from day one       |
| AVOID WHEN   | If team needs full style control       |
| TRADE-OFF    | You accept Prettier's style, not yours |
| ONE-LINER    | Parse → discard → reprint → done      |
| NEXT EXPLORE | ESLint (React), Husky, Biome           |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles — Type E)** Prettier discards all original whitespace before reprinting. ESLint modifies the existing token stream. What are the practical consequences of this architectural difference for idempotency, conflict resolution, and integration with other tools?

2. **(System Interaction — Type A)** Your team uses Prettier for formatting and ESLint for linting. A new hire sets up `eslint-plugin-prettier`, which runs Prettier as an ESLint rule. A senior engineer insists this is an anti-pattern and that the tools should remain separate. Who is correct, and why does the integration method matter for developer experience and CI performance?

3. **(Scale — Type B)** Your codebase of 300 files has never used Prettier. You want to introduce it. Running `prettier --write` produces a 12,000-line diff that makes `git blame` useless for the entire codebase. What strategy minimises disruption to ongoing feature work, preserves `git blame` usefulness, and ensures enforcement from day one?
