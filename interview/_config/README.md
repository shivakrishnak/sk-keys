# Interview Mastery Dictionary - Generation Guide

How to generate new interview mastery content using the two PowerShell scripts.

> **Always use `pwsh` (PowerShell 7+).** Never use `powershell.exe` - it corrupts emoji/Unicode.

---

## Scripts Overview

| Script                  | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `generate-keywords.ps1` | Step 1: Create keyword lists, folders, stubs |
| `generate-content.ps1`  | Step 2: Generate full content from stubs     |

**Spec References:**

| File                                               | Purpose                                     |
| -------------------------------------------------- | ------------------------------------------- |
| `technical-mastery/_config/MASTERY_OS_PROMPT.md`   | Master keyword generation spec (v4.0)       |
| `.github/prompts/technical-mastery-generate-keywords.prompt.md` | Prompt for category/tier keyword processing |
| `interview/_config/INTERVIEW_PROMPT.md`            | Master content generation spec (v3.0)       |

---

## Design Considerations

1. **New topic (no index.md):** Use `technical-mastery/_config/MASTERY_OS_PROMPT.md` v4.0 to generate keywords. Analyse tier placement. Create folders/files. Generate content.
2. **Brand-new topic (e.g., Angular):** Analyse which tier it belongs to. Generate keywords via `technical-mastery/_config/MASTERY_OS_PROMPT.md`. Create folders/files. Generate content.
3. **New subtopic (e.g., React Hooks, topic exists):** Create file in existing folder. Generate keywords via `technical-mastery/_config/MASTERY_OS_PROMPT.md`. Generate content.
4. **Existing dictionary category (e.g., JVM, JCC):** Scan dictionary `index.md`. Analyse keywords. Check for new folder/file opportunities. Generate content.

---

## Quick Start - End to End

```powershell
cd c:\ASK\MyWorkspace\sk-keys

# 1. Scaffold a new topic from dictionary keywords
pwsh -File interview/_config/generate-keywords.ps1 -Topic "React" -FromDictionary "RCT"

# 2. Generate content for all files in the topic
pwsh -File interview/_config/generate-content.ps1 -Mode topic -Topic "React"
```

---

## generate-keywords.ps1

Creates keyword lists, groups them into sub-topic files, and scaffolds folder/index/stub structure.

### Flow 1: New Topic from Dictionary

Pull keywords from existing dictionary categories and auto-group into sub-topic files.

```powershell
# Single dictionary category
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "Kubernetes" -FromDictionary "K8S"

# Multiple dictionary categories merged into one topic
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "Java" -FromDictionary "JVM,JLG"

# Preview without creating files
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "Security" -FromDictionary "SEC,IAM,CRY" -DryRun
```

**What it does:**

1. Reads keywords from dictionary `index.md` files
2. Groups keywords by difficulty into sub-topic files (5-15 per file)
3. Creates `interview/{topic}/` folder
4. Creates `index.md` with file listing table
5. Creates stub `.md` files with YAML frontmatter

### Flow 2: New Topic from Scratch

Generates an AI prompt for keyword discovery when no dictionary category exists.

```powershell
pwsh -File interview/_config/generate-keywords.ps1 -Topic "GraphQL"
```

**What it does:**

1. Checks if a matching dictionary category exists
2. If not found, outputs a prompt to paste into an AI assistant
3. Creates empty folder and index.md
4. You then manually add keywords from the AI output

### Flow 3: Add Subtopic to Existing Topic

Add a new sub-topic file with specific keywords to an existing topic.

```powershell
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "React" `
  -Subtopic "Hooks" `
  -Keywords "useState,useEffect,useContext,useReducer,useMemo,useCallback,useRef,Custom Hooks"
```

**What it does:**

1. Creates `React - Hooks.md` stub in `interview/react/`
2. Populates YAML `keywords:` list
3. Updates `interview/react/index.md` with new file row

---

## generate-content.ps1

Generates interview mastery content using `INTERVIEW_PROMPT.md` spec. Has 5 modes.

### Mode 1: `file` - Single Sub-topic File

Generate content for one specific file.

```powershell
# Generate Java Collections content
pwsh -File interview/_config/generate-content.ps1 `
  -Mode file -Topic "Java" -File "Collections"

# Generate with smaller batches (2 keywords per prompt)
pwsh -File interview/_config/generate-content.ps1 `
  -Mode file -Topic "Java" -File "Java 8 Features" -BatchSize 2

# Preview the generation prompts
pwsh -File interview/_config/generate-content.ps1 `
  -Mode file -Topic "Spring" -File "Core and IoC" -DryRun
```

**What it does:**

1. Reads keywords from the stub file's YAML frontmatter
2. Splits keywords into batches (default: 3 per batch)
3. Outputs a generation prompt for each batch
4. You paste each prompt into an AI assistant, then save the output

### Mode 2: `topic` - Full Topic

Generate content for all pending files in a topic folder.

```powershell
# Generate all Java files that don't have content yet
pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "Java"

# Generate all Kubernetes files
pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "Kubernetes"
```

**What it does:**

1. Scans all `.md` files in the topic folder (excluding `index.md`)
2. Identifies which files are stubs (no content) vs complete
3. Generates content prompts for each pending file
4. Updates `index.md` after all files are processed

### Mode 3: `tier` - From Dictionary Tier

Scan an entire dictionary tier and generate interview content for all mapped categories.

```powershell
# Generate from all tier-3-java categories (JVM, JLG, JCC, SPR, JPH)
pwsh -File interview/_config/generate-content.ps1 `
  -Mode tier -Tier "tier-3-java"

# Scan tier-4-data (DBF, NDB, CCH, DAT, BIG, MSG)
pwsh -File interview/_config/generate-content.ps1 `
  -Mode tier -Tier "tier-4-data"

# Preview what would be generated
pwsh -File interview/_config/generate-content.ps1 `
  -Mode tier -Tier "tier-6-infrastructure-devops" -DryRun
```

**What it does:**

1. Lists all category folders in the technical-mastery tier
2. Maps each category code to an interview topic via `TierTopicMap`
3. Reads dictionary keywords from each category
4. Creates interview topic folders, stubs, and index files
5. Unmapped categories are flagged for manual mapping

**Tier-to-Topic mappings** (built into the script):

| Category Codes     | Interview Topic                 |
| ------------------ | ------------------------------- |
| JVM, JLG           | Java                            |
| JCC                | Java Concurrency                |
| SPR                | Spring                          |
| JPH                | Hibernate                       |
| DBF, NDB           | SQL and Databases               |
| CTR                | Containers                      |
| K8S                | Kubernetes                      |
| DST, MSV, SYD, SAP | System Design                   |
| DPT                | Design Patterns                 |
| ASY                | Async and Background Processing |
| SEC, IAM, CRY      | Security                        |
| RCT                | React                           |
| DSA                | Data Structures and Algorithms  |
| CCH                | Caching                         |
| MSG                | Messaging                       |
| CCD, GIT, OBS      | CI/CD and DevOps                |
| AIF, LLM, RAG      | AI and RAG                      |

### Mode 4: `new` - Brand-New Topic

Create a topic that may not exist in the technical-mastery at all.

```powershell
# Create Angular topic (auto-checks dictionary for ANG category)
pwsh -File interview/_config/generate-content.ps1 `
  -Mode new -Topic "Angular"

# Create a topic with no dictionary equivalent
pwsh -File interview/_config/generate-content.ps1 `
  -Mode new -Topic "GraphQL"
```

**What it does:**

1. Checks if topic folder already exists (error if yes)
2. Searches dictionary for matching category
3. Creates `interview/{topic}/` folder and empty `index.md`
4. Prints next steps: run `generate-keywords.ps1` then `generate-content.ps1 -Mode topic`

### Mode 5: `subtopic` - Add Sub-topic to Existing Topic

Add a new sub-topic file to a topic that already exists.

```powershell
# Add a Hooks file to React
pwsh -File interview/_config/generate-content.ps1 `
  -Mode subtopic -Topic "React" -File "Hooks"

# Add Performance section to Java
pwsh -File interview/_config/generate-content.ps1 `
  -Mode subtopic -Topic "Java" -File "Performance Tuning"
```

**What it does:**

1. Verifies topic folder exists
2. Creates a stub file (or reports it already exists)
3. Updates `index.md`
4. Prints the command to generate content for the new file

---

## Common Workflows

### Workflow A: Generate a single topic end-to-end

```powershell
# Step 1 - Scaffold from dictionary
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "Spring" -FromDictionary "SPR"

# Step 2 - Generate content file by file
pwsh -File interview/_config/generate-content.ps1 `
  -Mode file -Topic "Spring" -File "Core and IoC"

pwsh -File interview/_config/generate-content.ps1 `
  -Mode file -Topic "Spring" -File "Boot"

# Or generate all at once
pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "Spring"
```

### Workflow B: Generate from an entire dictionary tier

```powershell
# Step 1 - Scaffold all topics in the tier
pwsh -File interview/_config/generate-content.ps1 `
  -Mode tier -Tier "tier-3-java"

# Step 2 - Generate content topic by topic
pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "Java"

pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "Java Concurrency"

pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "Spring"
```

### Workflow C: Add a brand-new topic not in dictionary

```powershell
# Step 1 - Create topic scaffold
pwsh -File interview/_config/generate-content.ps1 `
  -Mode new -Topic "GraphQL"

# Step 2 - Generate keyword list (outputs AI prompt)
pwsh -File interview/_config/generate-keywords.ps1 -Topic "GraphQL"

# Step 3 - Add subtopics with keywords manually
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "GraphQL" -Subtopic "Schema and Types" `
  -Keywords "Schema Definition,Queries,Mutations,Subscriptions,Scalar Types,Object Types,Input Types"

pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "GraphQL" -Subtopic "Advanced" `
  -Keywords "DataLoader,N+1 Problem,Federation,Caching,Authentication,Rate Limiting"

# Step 4 - Generate content
pwsh -File interview/_config/generate-content.ps1 `
  -Mode topic -Topic "GraphQL"
```

### Workflow D: Add a subtopic to an existing topic

```powershell
# Step 1 - Create stub with keywords
pwsh -File interview/_config/generate-keywords.ps1 `
  -Topic "Java" -Subtopic "Design Patterns" `
  -Keywords "Singleton,Factory,Builder,Observer,Strategy,Template Method,Decorator"

# Step 2 - Generate content
pwsh -File interview/_config/generate-content.ps1 `
  -Mode file -Topic "Java" -File "Design Patterns"
```

---

## Parameters Reference

### generate-keywords.ps1

| Parameter         | Required | Description                                                    |
| ----------------- | -------- | -------------------------------------------------------------- |
| `-Topic`          | Yes      | Topic name (e.g., "Java", "React")                             |
| `-FromDictionary` | No       | Dictionary category code(s), comma-separated (e.g., "JVM,JLG") |
| `-Subtopic`       | No       | Subtopic name to add to existing topic                         |
| `-Keywords`       | No       | Comma-separated keywords (used with `-Subtopic`)               |
| `-DryRun`         | No       | Preview without writing files                                  |

### generate-content.ps1

| Parameter    | Required | Description                                                    |
| ------------ | -------- | -------------------------------------------------------------- |
| `-Mode`      | Yes      | `file`, `topic`, `tier`, `new`, or `subtopic`                  |
| `-Topic`     | Depends  | Topic name (required for all modes except `tier`)              |
| `-File`      | Depends  | Subtopic name without .md (required for `file` and `subtopic`) |
| `-Tier`      | Depends  | Dictionary tier folder (required for `tier` mode)              |
| `-BatchSize` | No       | Keywords per generation batch (default: 3)                     |
| `-DryRun`    | No       | Preview without writing files                                  |

---

## Files in This Folder

| File                        | Purpose                                                                 |
| --------------------------- | ----------------------------------------------------------------------- |
| `INTERVIEW_PROMPT.md`       | Master generation prompt (19-section spec per keyword, v3.0)            |
| `interview-instructions.md` | Pointer to auto-loaded `.github/instructions/interview.instructions.md` |
| `interview_scaffold.py`     | Scaffold generator - creates [FILL:...] stub files (Python 3.14)        |
| `topic-registry.md`         | Topic-to-folder mapping and dictionary category links                   |
| `generate-content.ps1`      | Content generation script (5 modes)                                     |
| `generate-keywords.ps1`     | Keyword generation and folder scaffolding                               |
| `README.md`                 | This file                                                               |

**External references (used by both scripts):**

| File                                               | Purpose                                     |
| -------------------------------------------------- | ------------------------------------------- |
| `technical-mastery/_config/MASTERY_OS_PROMPT.md`   | Master keyword generation spec (v4.0)       |
| `.github/prompts/technical-mastery-generate-keywords.prompt.md` | Prompt for category/tier keyword processing |

> All files in `interview/_config/` are excluded from the Jekyll build via `_config.yml`.
