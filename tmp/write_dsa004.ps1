# Run with: pwsh -ExecutionPolicy Bypass -File tmp\write_dsa004.ps1
Set-Location "c:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-1-foundations\DSA-data-structures"

$content = @'
---
id: DSA-004
title: How to Think About Problems Algorithmically
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-001, DSA-002
used_by: DSA-051, DSA-081
related: DSA-003, DSA-005
tags:
  - dsa
  - foundational
  - mental-model
  - thought-experiment
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /dsa/how-to-think-about-problems-algorithmically/
---

# DSA-004 - How to Think About Problems Algorithmically

⚡ TL;DR - Algorithmic thinking is a learnable five-step mental process: observe the problem, abstract it, classify it, select the matching tool, and verify the solution's correctness and efficiency.

| #4 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | DSA-001, DSA-002 | |
| **Used by:** | DSA-051, DSA-081 | |
| **Related:** | DSA-003, DSA-005 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer is given a problem: "Find all users who have purchased from both Category A and Category B." They know arrays, loops, and hash maps. But faced with this new problem, they write the first solution that comes to mind — a nested loop over all purchases, comparing every pair. It works. They move on. Three weeks later, the same developer is given "find users who bought in exactly 3 out of 5 categories." They write a new nested loop. And again when the problem is "find users who bought in any 2 categories." Each time, they reinvent a slightly different wheel, never recognising that all three problems are the same problem class — set intersection — and all have the same O(n) hash-set solution.

**THE BREAKING POINT:**
Without a framework for thinking about problems algorithmically, every new problem looks unique. Engineers accumulate ad-hoc solutions that cannot be generalised, cannot be reused, and often have hidden efficiency problems. Technical debt accumulates not in the code — the code works — but in the *thinking*.

**THE INVENTION MOMENT:**
This is exactly why algorithmic thinking matters as an explicit skill. It provides a repeatable mental process for decomposing any problem into a known problem class, selecting the appropriate tool, and verifying that the solution is correct and efficient. Once a developer can do this reliably, every new problem is a combination of patterns they already know — not a blank-slate invention.

**EVOLUTION:**
Algorithmic thinking was formalised alongside algorithm theory in the 1960s-80s. The competitive programming community (ACM ICPC, Codeforces) codified it into a practice. Modern technical interviews explicitly test it — not because they want engineers who can sort arrays, but because they want engineers who can decompose novel problems systematically under pressure. The skill transfers to system design, debugging, and any domain requiring structured reasoning.

---

### 📘 Textbook Definition

**Algorithmic thinking** is the cognitive process of decomposing a problem into its essential structure, classifying it within a known problem class, selecting an appropriate algorithm or data structure, implementing a solution, and verifying its correctness and efficiency. It transforms the experience of encountering a new problem from blank-slate invention to pattern recognition and informed selection from a known solution repertoire.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Algorithmic thinking turns every new problem into a problem you have already solved.

**One analogy:**
> A plumber does not reinvent pipes for each new bathroom. They recognise the job type (drainage, supply, pressure), select from their established toolkit (fittings, valves, pipe sizes), and assemble a solution. The novelty is in the combination, not the components.

**One insight:**
Most problems that look different on the surface are the same problem underneath: find minimum, find intersection, find shortest path, find all arrangements. Algorithmic thinking is the skill of seeing through the surface to the structure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every computational problem has an abstract form independent of its domain-specific clothing — recognising that form is the first step.
2. Known problem classes (search, sort, traverse, optimise, count) have known solution patterns — the skill is mapping, not inventing.
3. Every solution must be verified for both correctness (produces the right output) and efficiency (scales to the expected input size).

**DERIVED DESIGN:**
Because most problems are instances of known classes, the highest-leverage skill is not knowledge of specific algorithms — it is the ability to recognise which class a problem belongs to. This is why algorithmic thinking is a meta-skill that multiplies the value of any specific algorithm knowledge.

**THE TRADE-OFFS:**
**Gain:** Faster problem solving, higher reuse, correct efficiency analysis, and a structured approach that performs under interview pressure.
**Cost:** Requires building a repertoire of known patterns first — the framework is only as useful as the pattern library it references.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every problem requires understanding what input comes in, what output is required, and what constraints bound the search space. This cannot be skipped.
**Accidental:** The specific language, syntax, or library used to implement the solution — these are separable from the thinking process itself.

---

### 🧪 Thought Experiment

**SETUP:**
A problem arrives: "Given a list of job postings and a list of user skills, find all jobs the user qualifies for (requires 100% skill match)."

**WHAT HAPPENS WITHOUT ALGORITHMIC THINKING:**
The developer reads the problem, thinks "I need to compare skills," and writes a nested loop: for each job, for each required skill, check if the user has it. This is O(j × s²) where j = jobs and s = skills per job. It works for 10 jobs and 5 skills. At 100,000 jobs with 20 skills each, it takes minutes.

**WHAT HAPPENS WITH ALGORITHMIC THINKING:**
Step 1 — Observe: input is two lists; output is a filtered subset.
Step 2 — Abstract: "does set A contain all elements of set B?" — this is set containment.
Step 3 — Classify: set operations problem class.
Step 4 — Select: convert user skills to a set O(s); for each job, check if required_skills ⊆ user_set using O(r) set lookups, where r = requirements per job. Total: O(j × r).
Step 5 — Verify: O(j × r) where r << s² — dramatically better at scale.

**THE INSIGHT:**
The five-step process converts a potentially novel-looking problem into a known class in under two minutes. The implementation follows naturally and is provably more efficient.

---

### 🧠 Mental Model / Analogy

> A doctor follows a diagnostic protocol: observe symptoms, hypothesise disease class, order confirming tests, select treatment, monitor outcome. A doctor who skips the protocol and prescribes based on first impression misdiagnoses frequently. The protocol is not bureaucracy — it is the accumulated wisdom of medical thinking made repeatable.

- "Observe symptoms" → observe the problem inputs, outputs, and constraints
- "Hypothesise disease class" → classify the problem into a known algorithmic category
- "Order confirming tests" → verify complexity at expected N
- "Select treatment" → choose the algorithm and data structure
- "Monitor outcome" → test edge cases and verify correctness

Where this analogy breaks down: medical diagnosis is probabilistic; algorithmic classification is deterministic — a problem either is or is not a set-intersection problem.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Algorithmic thinking is a way of looking at any problem and asking: "Have I seen something like this before?" Most problems share deep similarities with other problems. Recognising those similarities lets you solve new problems using approaches that already work.

**Level 2 - How to use it (junior developer):**
Apply the five-step framework: (1) Read the problem carefully — what goes in, what comes out? (2) Simplify — what is the smallest version of this problem? (3) Classify — does this look like searching, sorting, counting, or comparing sets? (4) Select — what structure or algorithm handles that class? (5) Verify — will it work correctly and efficiently at the expected scale?

**Level 3 - How it works (mid-level engineer):**
Problem classification relies on pattern recognition built from a repertoire of known classes: search problems, sort problems, graph traversal, dynamic programming (optimal substructure), greedy (locally optimal choices), divide-and-conquer, sliding window, two-pointer. Each class has a canonical solution family. The skill is matching, not inventing.

**Level 4 - Why it was designed this way (senior/staff):**
Algorithmic thinking is a prerequisite for system design because system design is algorithmic thinking at component granularity — "what is the dominant access pattern? what structure serves it? what is the trade-off?" Senior engineers apply the same five steps to components: observe the system's requirements, abstract the access patterns, classify the data management problem, select the appropriate storage/processing model, and verify the SLA implications.

**Level 5 - Mastery (distinguished engineer):**
At mastery level, algorithmic thinking is automatic and applied across problem domains simultaneously. When designing a distributed system, you are simultaneously classifying the consistency problem (distributed consensus), the routing problem (graph + shortest path), and the caching problem (LRU). Mastery also includes meta-thinking: recognising when a problem genuinely has no known efficient solution (NP-hard) versus when you are simply missing the right framing.

*Expert Thinking Cues: Always ask "what is the simplest version of this problem?" before solving the full version. Always ask "what class does this problem belong to?" before writing code. When stuck, ask "what have I seen that produces the same output structure?"*

---

### ⚙️ How It Works (Mechanism)

**The five-step algorithmic thinking process:**

**Step 1 — Observe:** Identify inputs, outputs, and constraints. What type is the input (list, graph, tree, string)? What type must the output be (single value, filtered list, ordered sequence)? What are the size constraints (N up to 10⁶?)

**Step 2 — Abstract:** Strip away domain-specific language and reduce to the essential structure. "Find users who bought from both categories" → "find intersection of two sets." "Find the shortest delivery route" → "find shortest path in a weighted graph."

**Step 3 — Classify:** Match the abstracted problem to a known class. Is it search? Sort? Optimisation with overlapping subproblems (dynamic programming)? A coverage problem (greedy)? A partitioning problem (divide-and-conquer)?

**Step 4 — Select:** Choose the algorithm and data structure canonical for that class. Set intersection → hash sets, O(n). Shortest path → Dijkstra, O(E log V). Optimal subsequence → DP table, O(n²) or O(n log n) depending on variant.

**Step 5 — Verify:** Check correctness (does the algorithm produce the right output for edge cases — empty input, single item, duplicates?) and efficiency (is the Big-O acceptable at the given N?).

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Problem statement → Step 1: Observe inputs/outputs
→ Step 2: Abstract to essential structure
→ Step 3: Classify to problem class
→ [PATTERN MATCH ← YOU ARE HERE]
→ Step 4: Select algorithm + structure
→ Step 5: Verify correctness + efficiency → Implement
```

**FAILURE PATH:**
Skip abstraction → Code first approach → Correct but inefficient solution → Profiler shows hotspot → Refactor required with existing code as constraint → Harder to redesign than starting from the right class

**WHAT CHANGES AT SCALE:**
The five-step process is equally valuable at N=100 and N=100M. The difference is that at large N, Step 5 (verify efficiency) becomes critical — an O(n²) solution that is "fine for now" at N=1,000 will need to be replaced at N=1M anyway.

---

### 💻 Code Example

```python
# Demonstrating the 5-step process on a concrete problem:
# "Find all employees who have ALL of the required skills"

# Step 1 - Observe:
# Input: list of employees (each has a skill list)
#        list of required skills
# Output: filtered list of qualifying employees
# Constraint: N employees up to 100,000; skills up to 50

# Step 2 - Abstract:
# "Does employee's skill SET contain ALL required skills?"
# = set containment: required_skills ⊆ employee_skills

# Step 3 - Classify: set operations

# Step 4 - Select: convert to sets for O(1) membership check

def find_qualified(employees, required_skills):
    # Build required set once: O(r) where r = requirements
    req_set = set(required_skills)

    qualified = []
    for emp in employees:                    # O(n)
        emp_skills = set(emp["skills"])      # O(s)
        if req_set.issubset(emp_skills):     # O(r)
            qualified.append(emp)
    return qualified
    # Total: O(n * (s + r)) — linear in employees

# Step 5 - Verify:
# Correctness: test empty employees, zero required skills,
#              employee with exactly matching skills
# Efficiency: O(n*(s+r)) << O(n*s*r) nested loop approach
```

**How to test / verify correctness:**
Test with: (1) empty required_skills → all employees qualify, (2) impossible skill requirement → empty result, (3) employee with exact skill match → included, (4) employee with one skill missing → excluded. Then benchmark at N=100K to confirm linear growth.

---

### ⚖️ Comparison Table

| Approach | Process | Result | When it fails |
|---|---|---|---|
| **Algorithmic thinking (5 steps)** | Observe → Abstract → Classify → Select → Verify | Correct + efficient solution | Requires pattern repertoire |
| Code first | Write loop → test → refactor | Often correct, often inefficient | Hard to refactor when structure is wrong |
| Brute force | Try all possibilities | Always correct | Intractable at scale |
| Intuition only | "Looks like last week's problem" | Fast when right | Misclassification leads to wrong tool |

How to choose: Use the 5-step framework for any problem where efficiency matters or complexity is non-trivial. Use intuition only when the problem is genuinely trivial (N < 100, O(n²) is acceptable).

---

### 🔁 Flow / Lifecycle

**The Five-Step Algorithmic Thinking Lifecycle:**

```
┌─────────────────────────────────────────────────┐
│  STEP 1: OBSERVE                                │
│  Inputs? Outputs? Constraints? Edge cases?      │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  STEP 2: ABSTRACT                               │
│  Strip domain language. What is the structure?  │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  STEP 3: CLASSIFY                               │
│  Search? Sort? Graph? DP? Greedy? Set ops?      │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  STEP 4: SELECT                                 │
│  Choose canonical algorithm + data structure    │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  STEP 5: VERIFY                                 │
│  Correctness (edge cases) + Efficiency (Big-O)  │
│  If efficiency fails: return to STEP 3          │
└─────────────────────────────────────────────────┘
```

**Phase triggers:** A failure in Step 5 (efficiency unacceptable) sends you back to Step 3 (try a different problem class framing). A failure in Step 5 (correctness) may require returning to Step 1 (re-observe the problem constraints).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Algorithmic thinking is only for interviews" | It is applied in every code review, system design, debugging session, and capacity planning exercise — daily. |
| "You have to be naturally gifted at algorithms" | Algorithmic thinking is a repeatable framework. The five steps can be learned and practised. The repertoire of patterns grows with deliberate study. |
| "Getting the right answer means I thought algorithmically" | An O(n³) brute-force that produces the correct answer did not involve algorithmic thinking — it involved trial and error. Thinking algorithmically means choosing a tool because you understand its properties. |
| "Once I know the algorithm, I don't need the framework" | Expert engineers apply the framework unconsciously but still apply it. The framework is what makes pattern recognition reliable rather than lucky. |

---

### 🚨 Failure Modes & Diagnosis

**1. Misclassification: wrong problem class selected**

**Symptom:** The solution is correct for small inputs but fails on edge cases or is dramatically inefficient at scale.

**Root Cause:** The problem was classified incorrectly — e.g., treated as a sorting problem when it is actually a two-pointer problem, or treated as a graph problem when it is a dynamic programming problem.

**Diagnostic:**
```python
# Test with edge cases that expose misclassification:
# - All equal elements (sort doesn't help)
# - Empty input (some algorithms crash)
# - Single element (algorithms assuming N>=2 fail)
# - Already sorted / reverse sorted (exposes sort-dependent logic)
```

**Fix:** Return to Step 3. Try a different problem class framing. Ask: "What other problem produces this same output structure?"

**Prevention:** Always test the edge cases that reveal the assumed problem structure before committing to an implementation.

---

**2. Skipping Step 2 (abstraction): solving surface features, not the structure**

**Symptom:** The solution is tightly coupled to domain-specific details and cannot be generalised; similar problems require rewriting from scratch.

**Root Cause:** The developer jumped from problem statement to implementation without abstracting to the essential structure. The solution solves "this specific problem" not "problems of this class."

**Diagnostic:** Ask: "Could I reuse this code if the domain changed but the structure stayed the same?" If no: abstraction was skipped.

**Fix:** Separate the algorithmic core from the domain-specific wrapper. The core should be expressible without any domain language.

**Prevention:** Before writing any code, write a one-sentence problem description using only abstract terms (sets, sequences, graphs, values) — no business domain words.

---

**3. Skipping Step 5 (verify): shipping unvalidated efficiency**

**Symptom:** Feature works in all test scenarios but degrades at production data volumes.

**Root Cause:** Correctness was verified but efficiency was not analysed — the Big-O of the selected algorithm was not checked against the expected N.

**Diagnostic:**
```python
import time

def measure_growth(fn, sizes):
    for n in sizes:
        data = list(range(n))
        t0 = time.perf_counter()
        fn(data)
        elapsed = time.perf_counter() - t0
        print(f"N={n:>8}: {elapsed*1000:.2f}ms")

# If time grows as N²: the algorithm is O(n²) — flag before shipping
```

**Prevention:** After selecting an algorithm, always calculate its Big-O and verify it is acceptable at the maximum expected N before implementing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `DSA-001 Why DSA Matter` - the motivation for developing this thinking skill
- `DSA-002 The Problem of Efficiency` - the vocabulary (Big-O) used in Step 5 of the framework

**Builds On This (learn these next):**
- `DSA-051 DSA Interview Pattern Catalogue` - a structured repertoire of canonical problem classes and their solutions
- `DSA-081 Algorithm Selection Framework` - a decision-tree extension of this framework for production system design

**Alternatives / Comparisons:**
- `DSA-003 DSA in Real Systems` - the application of this thinking to production systems rather than isolated problems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Five-step process: Observe → Abstract     │
│              │ → Classify → Select → Verify              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Engineers who solve every problem from    │
│ SOLVES       │ scratch, never recognising patterns       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Most problems are instances of 10-15      │
│              │ known classes; the skill is recognition   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any non-trivial problem where efficiency  │
│              │ matters or the solution will be reused    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Problem is genuinely trivial (N < 100,   │
│              │ any approach works, never reused)         │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Code-first: writing implementation        │
│              │ before abstracting the problem structure  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ 5 minutes of structured thinking saves    │
│              │ hours of debugging and refactoring        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every new problem is an old problem      │
│              │ wearing different domain clothes."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Problem Patterns → DP → Graph Algorithms  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Observe → Abstract → Classify → Select → Verify: the five steps are the entire framework.
2. Abstraction is the hardest and most valuable step: strip domain language to find the true structure.
3. Verification is mandatory: correctness without efficiency is incomplete.

**Interview one-liner:**
"I approach every algorithmic problem with five steps: understand the input-output structure, abstract away domain language, classify into a known problem class, select the canonical tool for that class, and verify both correctness and efficiency before coding."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every novel problem is a composition of known patterns. The skill that multiplies all other technical knowledge is pattern recognition — the ability to see through surface novelty to the underlying structure that has been solved before.

**Where else this pattern appears:**
- Medical diagnosis: every patient presents unique symptoms, but physicians classify them into known disease patterns — the process is identical to algorithmic problem classification
- Legal reasoning: attorneys classify a novel dispute into known legal frameworks (contract law, tort, property) to apply established precedent — the abstraction step is the same
- Scientific method: observe → hypothesise (classify) → experiment (verify) — algorithmic thinking is the engineering version of the scientific method

**Industry applications:**
- Google SRE teams use structured problem-solving protocols for incident response that parallel the five steps: observe the symptoms, abstract the failure mode, classify the type of outage, select the response playbook, verify the resolution — reducing MTTR dramatically
- Competitive programming companies (e.g., HackerRank, LeetCode) built entire assessment platforms on the premise that algorithmic thinking can be measured — and that the same 15-20 problem classes cover 90% of software engineering challenges

---

### 💡 The Surprising Truth

The most common mistake in technical interviews is not failing to know an algorithm — it is failing to classify the problem correctly in the first two minutes. Studies of interview data from top technology companies consistently show that candidates who spend 3-5 minutes on Steps 1-3 (observe, abstract, classify) before writing any code have significantly higher success rates than those who start coding immediately. The counter-intuitive insight: spending *more time not coding* at the start of a technical problem leads to *faster, more correct* solutions — because the classification step prevents implementing the wrong algorithm entirely.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given any new problem statement, talk through the five-step process out loud in under 5 minutes, classifying the problem into its algorithmic family before touching a keyboard.
2. [DEBUG] Given an existing inefficient solution, apply Step 2 (abstraction) to the original problem and identify what different classification would have produced a more efficient approach.
3. [DECIDE] Given two different problem descriptions that are actually the same class (e.g., "find common friends" and "find common products purchased"), recognise the shared structure and reuse the same algorithm.
4. [BUILD] Take a problem from an unfamiliar domain (e.g., genomics, finance, operations) and systematically apply the five steps to produce a correct, efficient solution without domain expertise.
5. [EXTEND] Apply the five-step framework to a system design problem — classify the caching problem, the routing problem, and the consistency problem as separate algorithmic classes, and justify a data structure choice for each.

---

### 🧠 Think About This Before We Continue

**Q1.** You encounter a new problem: "Given a list of meeting time ranges, find the minimum number of meeting rooms required." Without looking at solutions, apply the five-step framework. What problem class does this belong to, and what data structure does Step 4 suggest?
*Hint: Think about what changes at each meeting start/end time and what data structure efficiently tracks "how many meetings are currently active."*

**Q2.** Two problems look identical on the surface: "find the longest increasing subsequence" and "find the longest common subsequence." Both produce a "longest subsequence." Why do they fall into different algorithmic classes, and what does Step 3 reveal about the trade-off in solution approaches?
*Hint: Consider what choices are available at each step of each problem and whether those choices have overlapping subproblems.*

**Q3.** (TYPE G) Take any feature request you have worked on recently. Apply all five steps of the framework to it — write them down. What problem class did you identify? Does the actual implementation match the canonical solution for that class? If not, what would the canonical approach look like, and is it more efficient?
*Hint: Most production features are one of: key-value lookup, sorted retrieval, set membership, or graph traversal. The implementation may be using a less-efficient structure due to "the first thing that worked."*

---

### 🎯 Interview Deep-Dive

**Q1: Walk me through how you would approach a problem you have never seen before. What is your process before you write any code?**
*Why they ask:* Tests whether you have a systematic problem-solving process or rely purely on pattern recognition and luck. Interviewers want repeatable methodology, not just correct answers.
*Strong answer includes:*
- Explicitly name the steps: read carefully, clarify constraints, work a small example by hand, identify the problem class, select the structure/algorithm, check complexity before coding
- Mention asking clarifying questions as part of Step 1 (constraints, edge cases, expected N)
- Demonstrate that you do not start coding until Steps 1-3 are complete
- Give an example of a time the classification step saved significant implementation effort

**Q2: You are given this problem: "Find the first non-repeating character in a string." Classify it and explain your algorithm choice.**
*Why they ask:* Tests the classification step directly — this is a frequency-counting problem (hash map counts) with an ordered traversal constraint, not a sorting or searching problem.
*Strong answer includes:*
- Classify: counting problem — need to know frequency of each character
- Select: hash map for O(1) count lookup; single pass for counting, second pass for first with count=1
- Total: O(n) time, O(1) space (26 chars max for lowercase ASCII → constant space)
- Verify: handles empty string (return null), all repeating (return null), single char (return it)
- Common wrong answer: sorting the string (O(n log n)) loses position information

**Q3: When would you choose to brute-force a solution rather than optimise it first?**
*Why they ask:* Tests pragmatic engineering judgment — knowing when NOT to apply advanced algorithmic thinking is as valuable as knowing when to apply it.
*Strong answer includes:*
- When N is provably small and bounded forever: 50 config items, 10 admin users — O(n²) is fine
- When the brute force is fast enough for the SLA: 200ms budget, O(n²) with N=100 takes <1ms
- When you need a correctness baseline: implement brute force first, then optimise, using brute force as the oracle for property-based testing
- When the optimised solution is complex enough to introduce bugs that are harder to fix than the performance problem
- Frame it as a deliberate trade-off decision, not a default — always know the complexity of the brute force before choosing to ship it
'@

$f = Join-Path $base "DSA-004 - How to Think About Problems Algorithmically.md"
[System.IO.File]::WriteAllText($f, $content, [System.Text.UTF8Encoding]::new($false))
$lines = (Get-Content $f -Encoding UTF8).Count
Write-Host "Written: $lines lines -> $f"
$bytes = [IO.File]::ReadAllBytes($f)
Write-Host "BOM check: $($bytes[0]),$($bytes[1]),$($bytes[2])  (must NOT be 239,187,191)"
