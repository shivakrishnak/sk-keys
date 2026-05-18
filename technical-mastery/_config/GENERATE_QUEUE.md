# generate_queue.py  -  Usage Guide

Finds stub / draft entries that need full v4.0 content generated,
and outputs ready-to-paste batch invocations for Copilot.

**Script location:** `tmp/generate_queue.py`
**Python:** `C:\Users\skurremula\.local\bin\python3.14.exe`

---

## Quick start

```powershell
# From the workspace root:
python tmp/generate_queue.py --target <TARGET>
```

A file is treated as a stub when **any** of these are true:

- Body contains `> Entry stub`
- `status: draft` AND file is smaller than 3 KB

---

## `--target`  -  required

Accepts three forms:

| Form             | Example                          | Scope                       |
| ---------------- | -------------------------------- | --------------------------- |
| Category code    | `MSV`, `JVM`, `SPR`              | One category                |
| Tier number      | `1`, `3`, `7`                    | All categories in that tier |
| Tier folder name | `tier-3-java`, `tier-7-frontend` | All categories in that tier |

---

## Options

| Flag           | Short | Default      | Description                                |
| -------------- | ----- | ------------ | ------------------------------------------ |
| `--target`     | `-t`  | _(required)_ | Category code, tier number, or tier folder |
| `--batch-size` | `-b`  | `10`         | Entries per generation batch               |
| `--list`       | `-l`  | off          | List stubs only, no batch formatting       |

---

## Examples

### By category code

```powershell
# Batches of 10 (default)  -  ready to paste into Copilot
python tmp/generate_queue.py --target MSV

# Smaller batches  -  useful for large categories or complex entries
python tmp/generate_queue.py --target SPR --batch-size 5

# Batches of 1  -  generate one entry at a time
python tmp/generate_queue.py --target LNX --batch-size 1

# Just list stubs  -  quick scan without batch formatting
python tmp/generate_queue.py --target JVM --list
```

### By tier number

```powershell
# All stubs across every category in Tier 1 (CS Foundations)
python tmp/generate_queue.py --target 1

# Tier 3 (Java), batches of 5
python tmp/generate_queue.py --target 3 --batch-size 5

# Tier 7 (Frontend)  -  list only, no formatting
python tmp/generate_queue.py --target 7 --list

# Tier 8 (AI), default batch size
python tmp/generate_queue.py --target 8
```

### By tier folder name

```powershell
# Full tier folder name also works
python tmp/generate_queue.py --target tier-6-infrastructure-devops

python tmp/generate_queue.py --target tier-8-artificial-intelligence --list

python tmp/generate_queue.py --target tier-5-distributed-architecture --batch-size 5
```

---

## Tier reference

| Number | Folder                            | Categories                                            |
| ------ | --------------------------------- | ----------------------------------------------------- |
| 1      | `tier-1-foundations`              | CSF, DSA, OSY, LNX                                    |
| 2      | `tier-2-networking-security`      | NET, API, SEC                                         |
| 3      | `tier-3-java`                     | JVM, JLG, JCC, SPR                                    |
| 4      | `tier-4-data`                     | DBF, NDB, CCH, DAT, BIG                               |
| 5      | `tier-5-distributed-architecture` | DST, MSV, SYD, SAP, DPT                               |
| 6      | `tier-6-infrastructure-devops`    | CTR, K8S, AWS, AZR, CCD, GIT, MVN, CDQ, TST, OBS, IAC |
| 7      | `tier-7-frontend`                 | HTM, CSS, JSC, TSC, RCT, ANG, NDJ, NPM, WBP           |
| 8      | `tier-8-artificial-intelligence`  | AIF, LLM, RAG, AIP                                    |
| 9      | `tier-9-professional-domain`      | ASY, DGN, FIN, PLT, BHV                               |

---

## Output format

### `--list` mode (scan / review)

```
--------------------------------------------------------------
Microservices  (15 stubs)
  MSV-003      | Why Microservices Became Popular           | ★☆☆
  MSV-004      | The Microservices Ecosystem Map            | ★☆☆
  MSV-005      | When NOT to Use Microservices              | ★☆☆
  MSV-066      | Service Decomposition Strategy             | ★★★
  ...
```

### Batch mode (default  -  paste into Copilot)

```
==============================================================
CATEGORY : Microservices
Tier     : tier-5-distributed-architecture
Folder   : MSV-microservices
Stubs    : 15

--------------------------------------------------------------
# Batch 1  (MSV-003 through MSV-007)
Generate technical-mastery entries MSV-003 through MSV-007:
  MSV-003      | Why Microservices Became Popular           | ★☆☆
  MSV-004      | The Microservices Ecosystem Map            | ★☆☆
  MSV-005      | When NOT to Use Microservices              | ★☆☆
  MSV-066      | Service Decomposition Strategy             | ★★★
  MSV-067      | Microservices Migration Strategy (Strangler Fig) | ★★★

Category: Microservices | Tier: tier-5-distributed-architecture | Folder: MSV-microservices
Follow Master Prompt v4.0 exactly.

--------------------------------------------------------------
# Batch 2  (MSV-068 through MSV-072)
...
```

Each `# Batch N` block is the **exact generation invocation**  -  paste it directly into Copilot chat.

---

## Full workflow

### Step 1  -  Discover stubs

```powershell
python tmp/generate_queue.py --target MSV
```

The output groups all stubs into numbered batches. Copy one batch block at a time for Step 2.

---

### Step 2  -  Generate content (two options)

#### Option A  -  Agent prompt (recommended)

Open Copilot Chat in **Agent mode**, use `@technical-mastery-generate-entries`, and fill in the prompts:

1. In VS Code, open Copilot Chat (`Ctrl+Shift+I`)
2. Switch to **Agent** mode (top-left of chat panel)
3. Type `@technical-mastery-generate-entries` or click paperclip → select `.github/prompts/technical-mastery-generate-entries.prompt.md`
4. When prompted, enter:
   - **Target:** category code or tier number (e.g. `MSV` or `5`)
   - **Batch size:** number of entries per batch (e.g. `5`)

The agent will automatically:

- Run `generate_queue.py` to discover stubs
- Read each stub's existing frontmatter
- Generate full v4.0 content for each entry
- Write each file
- Verify and commit

#### Option B  -  Manual chat (paste batch blocks)

Copy one `# Batch N` block from Step 1 output and paste it directly into Copilot Chat.
The block already contains the generation invocation in the exact format required:

```
Generate technical-mastery entries MSV-003 through MSV-007:
  MSV-003      | Why Microservices Became Popular    | ★☆☆
  MSV-004      | The Microservices Ecosystem Map     | ★☆☆
  MSV-005      | When NOT to Use Microservices       | ★☆☆
  MSV-066      | Service Decomposition Strategy      | ★★★
  MSV-067      | Microservices Migration Strategy    | ★★★

Category: Microservices | Tier: tier-5-distributed-architecture | Folder: MSV-microservices
Follow Master Prompt v4.0 exactly.
```

Copilot will read each stub, generate full v4.0 content, and write the files.
Repeat for each batch block until all stubs are done.

> **Requirement for both options:** the technical-mastery instructions auto-load when editing
> `technical-mastery/**` files (via `.github/instructions/technical-mastery.instructions.md`). The full
> Master Prompt v4.0 spec lives in `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md`.

---

### Step 3  -  Verify

```powershell
# Check all generated files for v4.0 compliance
python tmp/check_all_categories.py --category MSV --v3-only

# Expected: every generated entry shows v4.0 + complete
# If any show v2.1 or earlier, re-generate that batch
```

---

### Step 4  -  Commit

```powershell
git add technical-mastery/
git commit -m "feat: generate MSV-003-MSV-007 - full v4.0 entries"
```

---

## Exit codes

| Code | Meaning                                   |
| ---- | ----------------------------------------- |
| `0`  | No stubs found  -  all entries are complete |
| `1`  | Stubs were found (or an error occurred)   |

---

## Related files

| File                                              | Purpose                                            |
| ------------------------------------------------- | -------------------------------------------------- |
| `tmp/generate_queue.py`                           | This script  -  stub discovery and batch output      |
| `tmp/check_all_categories.py`                     | Full audit  -  version and compliance check          |
| `.github/prompts/technical-mastery-generate-entries.prompt.md` | VS Code agent prompt that drives the full loop     |
| `.github/instructions/technical-mastery.instructions.md` | Auto-loaded instructions for technical-mastery/\*\* edits |
| `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md`          | Master Prompt v4.0 spec (full 671-line reference)  |
