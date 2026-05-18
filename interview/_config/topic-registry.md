# Interview Mastery Dictionary - Topic Registry

> This registry maps topics to their interview folders and links them
> to existing dictionary categories where applicable. Start with core
> topics; grow organically as new topics are added.

---

## Spec References

| File                                               | Purpose                                     |
| -------------------------------------------------- | ------------------------------------------- |
| `technical-mastery/_config/MASTERY_OS_PROMPT.md`   | Master keyword generation spec (v4.0)       |
| `.github/prompts/technical-mastery-generate-keywords.prompt.md` | Prompt for category/tier keyword processing |
| `interview/_config/INTERVIEW_PROMPT.md`            | Master content generation spec (v3.0)       |

## Design Considerations

1. **New topic (no folder/index.md):** Use `technical-mastery/_config/MASTERY_OS_PROMPT.md` v4.0 to generate keywords. Analyse tier placement. Create folders/files. Generate content.
2. **Brand-new topic (e.g., Angular):** Analyse which tier it belongs to. Generate keywords via `technical-mastery/_config/MASTERY_OS_PROMPT.md`. Create folders/files. Generate content.
3. **New subtopic (e.g., React Hooks, topic exists):** Create file in existing folder. Generate keywords via `technical-mastery/_config/MASTERY_OS_PROMPT.md`. Generate content.
4. **Existing dictionary category (e.g., JVM, JCC):** Scan dictionary `index.md`. Analyse keywords. Check for new folder/file opportunities. Generate content.

---

## Registry Format

| Topic        | Folder         | Dictionary Sources           | Status                                       |
| ------------ | -------------- | ---------------------------- | -------------------------------------------- |
| [Topic Name] | [folder-name/] | [CODE1, CODE2, ...] or "new" | planned / scaffolded / generating / complete |

---

## Active Topics

| Topic            | Folder            | Dictionary Sources | Status     | Description                                                                   |
| ---------------- | ----------------- | ------------------ | ---------- | ----------------------------------------------------------------------------- |
| Java             | java/             | JVM, JLG           | generating | Core Java language, OOP, collections, modern Java features, JVM internals, GC |
| Java Concurrency | java-concurrency/ | JCC                | generating | Threading, synchronization, virtual threads, concurrent collections           |

---

## Sub-topic File Mapping

Each topic is split into sub-topic files. Below are the planned file
splits for each topic. Files are grouped by relatedness - each file
should be self-sufficient.

### Java (java/)

| File                               | Keywords (approximate)                                                                                                                                                 | Source IDs                          |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Java - Basics.md                   | Variables/Data Types, Operators/Control Flow, Classes/Objects, Inheritance, Interfaces, Access Modifiers, Enums                                                        | JLG-019 to JLG-027                  |
| Java - Collections.md              | Collections Framework, ArrayList/LinkedList, HashMap/TreeMap, HashSet, Queue/Deque, Iterator, Comparable/Comparator, equals/hashCode                                   | JLG-029, JLG-077/078/080            |
| Java - Exceptions and IO.md        | Exception Hierarchy, Checked vs Unchecked, Try-with-Resources, Custom Exceptions, File IO, NIO, Serialization, Logging                                                 | JLG-030/031/040/070/076             |
| Java - Java 8 Features.md          | Lambdas, Functional Interfaces, Stream API, Optional, Method References, Default Methods, DateTime API, Collectors                                                     | JLG-035 to JLG-038, JLG-072/075/079 |
| Java - Java 11 to 17.md            | var, Text Blocks, Switch Expressions, Records, Sealed Classes, Pattern Matching instanceof, JPMS, HttpClient                                                           | JLG-032/039/071/082/083/014         |
| Java - Java 21 and Beyond.md       | Virtual Threads Patterns, Structured Concurrency, Scoped Values, Pattern Matching switch, Record Patterns, Sequenced Collections, String Templates, Foreign Memory API | JLG-049/097/098                     |
| Java - JVM Internals.md            | JVM Architecture, JVM/JRE/JDK, Bytecode, Class Loading, Stack/Heap, Metaspace, JIT (C1/C2), Escape Analysis, GraalVM                                                   | JVM-001 to JVM-057                  |
| Java - Garbage Collection.md       | GC Fundamentals, GC Roots, Generational GC, Serial/Parallel GC, G1GC, ZGC, Shenandoah, GC Tuning/Logs, Reference Types                                                 | JVM-037 to JVM-048                  |
| Java - Diagnostics and Security.md | JFR, Thread Dumps, Heap Dumps, Performance Tuning, GC Selection Framework, Java Security, Version Migration                                                            | JVM-063 to JVM-067, JLG-015/016     |
