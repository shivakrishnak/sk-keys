#!/usr/bin/env python3
"""Fill TODO sections for Java - Java 11 to 17.md (4 keywords)."""
import re

FILE = "interview/java/Java - Java 11 to 17.md"

KEYWORDS = [
    "Records",
    "Sealed Classes",
    "Text Blocks",
    "Switch Expressions",
]

# ── Level 5 ──────────────────────────────────────────────

LEVEL5 = {
    "Records": (
        "Records represent the JVM's first step toward value "
        "semantics - the idea that some objects are defined "
        "entirely by their data, not their identity. This same "
        "concept appears in Kotlin data classes, Scala case "
        "classes, C# records, and Haskell algebraic data types. "
        "The cross-domain insight: whenever you see boilerplate "
        "code that mechanically derives behavior from data "
        "(equals, hashCode, toString, accessors), the language "
        "is missing a first-class abstraction for value types. "
        "Records fill that gap by making the compiler generate "
        "canonical implementations. At extreme scale, records "
        "compose with sealed classes to form algebraic data "
        "types (ADTs), enabling exhaustive pattern matching "
        "that the compiler can verify. If redesigning today, "
        "you would combine records with value types (Project "
        "Valhalla) to eliminate the identity/reference overhead "
        "entirely, making records as efficient as primitives.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this object defined by its data or its identity?\" "
        "- data = record, identity = class\n"
        "- \"Would I want structural equality?\" - if yes, "
        "record's auto-generated equals is correct\n"
        "- \"Can this be immutable?\" - records enforce "
        "immutability, which is essential for thread safety"
    ),
    "Sealed Classes": (
        "Sealed classes implement closed-world subtyping - the "
        "ability to define a type whose subtypes are known at "
        "compile time. This is the OOP equivalent of algebraic "
        "data types in functional languages (Haskell, Rust, "
        "Scala). The same closed-world principle appears in "
        "protocol buffers (oneof), database schemas (enum "
        "columns), and state machines (finite state sets). "
        "The expert insight: sealed classes solve the expression "
        "problem's 'data side' - you can add operations "
        "(methods) without modifying existing code, because "
        "the compiler guarantees all subtypes are handled. "
        "Combined with pattern matching (JDK 21), sealed "
        "hierarchies enable the visitor pattern without the "
        "visitor boilerplate. If redesigning today, you would "
        "make sealed the default for non-final classes, "
        "requiring explicit `open` for extensibility.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Should this hierarchy be open or closed?\" - "
        "if subtypes are a fixed set, seal it\n"
        "- \"Does switch need to be exhaustive?\" - sealed "
        "enables compiler-checked exhaustiveness\n"
        "- \"Is this a state machine or event type?\" - "
        "sealed classes model finite type sets perfectly"
    ),
    "Text Blocks": (
        "Text blocks solve the universal string literal "
        "readability problem: embedding multi-line text "
        "(JSON, SQL, HTML, XML) in source code without escape "
        "character noise. This same problem was solved by "
        "Python triple-quotes, JavaScript template literals, "
        "Kotlin raw strings, and C# raw string literals. The "
        "cross-domain insight: code that constructs other code "
        "(SQL queries, API payloads, config files) should look "
        "as close to the output as possible - this reduces "
        "cognitive load and prevents escaping bugs. Text blocks "
        "use a sophisticated indentation stripping algorithm "
        "(common leading whitespace removal) that preserves "
        "relative indentation while allowing code-level "
        "formatting. If redesigning today, you would add "
        "string interpolation (like Kotlin's `${}` or "
        "JavaScript template literals) directly in text blocks "
        "instead of requiring `.formatted()` or `String.format()`.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this string >1 line?\" - text block for "
        "readability\n"
        "- \"Does this have escape characters?\" - text block "
        "eliminates most escaping\n"
        "- \"Is indentation significant?\" - understand the "
        "common whitespace stripping algorithm"
    ),
    "Switch Expressions": (
        "Switch expressions transform Java's switch from a "
        "statement (control flow) to an expression (value "
        "producer), enabling functional-style pattern matching. "
        "This evolution mirrors Kotlin's `when`, Rust's `match`, "
        "Scala's `match`, and C#'s switch expressions. The "
        "cross-domain insight: the shift from statements to "
        "expressions is part of a broader language evolution "
        "toward expression-oriented programming, where every "
        "construct produces a value. This eliminates an entire "
        "class of bugs: uninitialized variables from missed "
        "branches, fall-through errors, and incomplete case "
        "coverage. Combined with sealed classes (JDK 17) and "
        "pattern matching (JDK 21), switch expressions become "
        "the foundation for algebraic data type deconstruction. "
        "If redesigning today, arrow-form switch expressions "
        "would be the only syntax, and the classic fall-through "
        "switch statement would never have existed.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is switch producing a value?\" - use expression form "
        "with arrow syntax\n"
        "- \"Is fall-through intentional?\" - if not, arrow form "
        "prevents it by design\n"
        "- \"Is the type sealed?\" - compiler enforces "
        "exhaustiveness with sealed types"
    ),
}

# ── Quick Reference Card ─────────────────────────────────

QUICKREF = {
    "Records": (
        "**WHAT IT IS:** Immutable data carrier class with "
        "compiler-generated equals, hashCode, toString, and "
        "accessors (JDK 16)\n"
        "**PROBLEM IT SOLVES:** Eliminates boilerplate for "
        "data-only classes - no more manual equals/hashCode/"
        "toString/getters\n"
        "**KEY INSIGHT:** A record is defined entirely by its "
        "components. The compiler derives all behavior from the "
        "data definition\n"
        "**USE WHEN:** DTOs, value objects, API responses, "
        "compound map keys, method return types with multiple "
        "values\n"
        "**AVOID WHEN:** Mutable state needed, inheritance "
        "required, or custom equals/hashCode semantics differ "
        "from component-based\n"
        "**ANTI-PATTERN:** Using records with mutable component "
        "types (List, Date) - immutability is not deep by default\n"
        "**TRADE-OFF:** Simplicity and safety vs flexibility - "
        "no inheritance, no mutable fields, no custom storage\n"
        "**ONE-LINER:** \"Records are transparent, immutable "
        "data carriers where the class IS its data\""
    ),
    "Sealed Classes": (
        "**WHAT IT IS:** Classes/interfaces that restrict which "
        "classes can extend/implement them using a `permits` "
        "clause (JDK 17)\n"
        "**PROBLEM IT SOLVES:** Enables exhaustive type checking "
        "in switch/pattern matching by defining a closed set "
        "of subtypes\n"
        "**KEY INSIGHT:** Sealed classes make the type hierarchy "
        "a known, finite set - enabling compiler-verified "
        "exhaustiveness\n"
        "**USE WHEN:** Domain models with fixed variants (Shape, "
        "Payment type), state machines, event hierarchies, "
        "result types\n"
        "**AVOID WHEN:** Open extension is needed (plugin "
        "architectures, framework SPI), or subtypes are not a "
        "fixed finite set\n"
        "**ANTI-PATTERN:** Sealing a class but adding a "
        "'catch-all' subtype to handle future cases - defeats "
        "the purpose\n"
        "**TRADE-OFF:** Exhaustiveness checking and type safety "
        "vs extensibility - sealed hierarchies can't be "
        "extended by consumers\n"
        "**ONE-LINER:** \"Sealed classes tell the compiler: "
        "these are ALL the subtypes, check my switches\""
    ),
    "Text Blocks": (
        "**WHAT IT IS:** Multi-line string literals delimited by "
        "triple quotes (`\"\"\"`) with automatic indentation "
        "management (JDK 15)\n"
        "**PROBLEM IT SOLVES:** Readable embedding of JSON, SQL, "
        "HTML, and other multi-line text without escape character "
        "noise\n"
        "**KEY INSIGHT:** Common leading whitespace is "
        "automatically stripped, so text blocks can be indented "
        "with surrounding code\n"
        "**USE WHEN:** Multi-line strings (SQL queries, JSON "
        "payloads, HTML templates, config snippets, test data)\n"
        "**AVOID WHEN:** Single-line strings where regular "
        "literals are clearer. Dynamic strings needing "
        "interpolation\n"
        "**ANTI-PATTERN:** Mixing tabs and spaces in text blocks "
        "- inconsistent whitespace breaks the stripping "
        "algorithm\n"
        "**TRADE-OFF:** Readability vs precision - indentation "
        "stripping is implicit and may surprise if not "
        "understood\n"
        "**ONE-LINER:** \"Text blocks make embedded SQL, JSON, "
        "and HTML look like actual SQL, JSON, and HTML\""
    ),
    "Switch Expressions": (
        "**WHAT IT IS:** Switch as an expression that returns "
        "a value, with arrow syntax and no fall-through "
        "(JDK 14)\n"
        "**PROBLEM IT SOLVES:** Eliminates switch fall-through "
        "bugs, enables exhaustiveness checking, produces values "
        "directly\n"
        "**KEY INSIGHT:** Arrow form (`->`) replaces colon form "
        "(`:`) - no fall-through, no break needed, returns a "
        "value\n"
        "**USE WHEN:** Mapping input to output, enum dispatch, "
        "any switch that should produce a value, pattern matching "
        "preparation\n"
        "**AVOID WHEN:** Fall-through behavior is genuinely "
        "needed (rare), or simple if-else is clearer for 2 "
        "cases\n"
        "**ANTI-PATTERN:** Using colon-form switch with break "
        "statements when arrow-form is cleaner and safer\n"
        "**TRADE-OFF:** Safety (no fall-through) vs flexibility "
        "(intentional fall-through requires colon form)\n"
        "**ONE-LINER:** \"Switch expressions turn 'do something "
        "for each case' into 'what is the value for each "
        "case'\""
    ),
}

# ── Comparison Table ─────────────────────────────────────

COMPARISON = {
    "Records": (
        "| Aspect | Record | Regular Class | "
        "Lombok @Data |\n"
        "|--------|--------|---------------|"
        "-------------|\n"
        "| Mutability | Immutable | Mutable | Mutable |\n"
        "| equals/hashCode | Auto (components) | Manual | "
        "Auto (all fields) |\n"
        "| Inheritance | Cannot extend | Can extend | "
        "Can extend |\n"
        "| Boilerplate | Zero | High | Low (annotation) |\n"
        "| Compile-time safety | Yes | N/A | "
        "Annotation processor |\n"
        "| Serialization | Built-in support | Manual | Manual |"
    ),
    "Sealed Classes": (
        "| Aspect | Sealed Class | Final Class | "
        "Abstract Class |\n"
        "|--------|-------------|-------------|"
        "---------------|\n"
        "| Extension | Permitted set | None | "
        "Unlimited |\n"
        "| Exhaustiveness | Compiler-checked | N/A | "
        "No |\n"
        "| Pattern matching | Full support | Limited | "
        "Requires default |\n"
        "| Use case | Fixed type hierarchy | Utility class | "
        "Open hierarchy |\n"
        "| JDK version | 17+ | Any | Any |"
    ),
    "Text Blocks": (
        "| Feature | Text Block | String Literal | "
        "StringBuilder |\n"
        "|---------|-----------|----------------|"
        "--------------|\n"
        "| Multi-line | Yes (native) | No (\\n) | "
        "Yes (append) |\n"
        "| Readability | High | Low for multi-line | "
        "Low |\n"
        "| Indentation | Auto-stripped | Manual | Manual |\n"
        "| Interpolation | No (use .formatted) | No | "
        "Yes (append) |\n"
        "| Escaping | Minimal | Heavy | Heavy |\n"
        "| Type | String | String | String |"
    ),
    "Switch Expressions": (
        "| Feature | Switch Expression | Switch Statement | "
        "if-else |\n"
        "|---------|------------------|-----------------|"
        "--------|\n"
        "| Returns value | Yes | No | "
        "No (ternary: yes) |\n"
        "| Fall-through | No (arrow) | Yes (colon) | No |\n"
        "| Exhaustiveness | Compiler-checked | No | No |\n"
        "| Pattern matching | JDK 21+ | No | No |\n"
        "| Multi-case | Comma-separated | Stack cases | "
        "\\|\\| chains |"
    ),
}

# ── Misconceptions ───────────────────────────────────────

MISCONCEPTIONS = {
    "Records": [
        ("Records are just like Lombok @Data",
         "Records are immutable (final fields, no setters) and "
         "part of the language. Lombok @Data generates mutable "
         "classes with setters. Records also integrate with "
         "sealed classes and pattern matching."),
        ("Records can't have methods",
         "Records can have instance methods, static methods, "
         "and implement interfaces. They just can't have "
         "non-final instance fields or extend other classes."),
        ("Records provide deep immutability",
         "Record fields are final (shallow immutability), but "
         "mutable component types (List, Map) can still be "
         "modified. Use `List.copyOf()` in the compact "
         "constructor for deep immutability."),
        ("Records replace all POJOs",
         "Records can't extend classes, can't have mutable "
         "state, and auto-generate equals based on all "
         "components. When you need inheritance or mutable "
         "state, regular classes are still needed."),
    ],
    "Sealed Classes": [
        ("Sealed classes are just final classes with subtypes",
         "Sealed classes define a CLOSED hierarchy - the "
         "compiler knows all subtypes and can verify exhaustive "
         "pattern matching. Final classes prevent ALL extension."),
        ("All subtypes must be in the same file",
         "Subtypes must be in the same package (or module), "
         "not necessarily the same file. The `permits` clause "
         "lists all allowed subtypes explicitly."),
        ("Sealed classes prevent extension entirely",
         "Sealed classes control the FIRST level of extension. "
         "Permitted subtypes can themselves be sealed, "
         "non-sealed (open for further extension), or final."),
        ("Sealed classes are only useful with pattern matching",
         "Sealed classes are valuable for domain modeling even "
         "without pattern matching. They document and enforce "
         "the type hierarchy at compile time."),
    ],
    "Text Blocks": [
        ("Text blocks are a different type than String",
         "Text blocks produce regular `java.lang.String` "
         "objects. They are compile-time sugar for multi-line "
         "string literals, not a new type."),
        ("Leading whitespace is always removed",
         "Only COMMON leading whitespace is removed. The "
         "closing `\"\"\"` position determines the common "
         "indent baseline. Relative indentation is preserved."),
        ("Text blocks support string interpolation",
         "Java text blocks have no interpolation syntax. Use "
         "`.formatted()` (JDK 15+) or `String.format()` for "
         "variable substitution."),
        ("Text blocks can start on the opening line",
         "Content must start on the line AFTER the opening "
         "`\"\"\"`. The opening delimiter line cannot contain "
         "content - only a line terminator follows it."),
    ],
    "Switch Expressions": [
        ("Arrow-form switch can't have multiple statements",
         "Arrow cases can use a block with `yield` to execute "
         "multiple statements and return a value: "
         "`case X -> { /* code */ yield val; }`"),
        ("Switch expressions replace switch statements",
         "Both forms coexist. Switch statements (with fall-"
         "through) are still valid. Use expressions when "
         "producing a value, statements for side-effect-only "
         "logic."),
        ("All switch expressions need a default case",
         "If the switch covers all possible values (all enum "
         "constants, all sealed subtypes), no default is needed. "
         "The compiler verifies exhaustiveness."),
        ("yield is the same as return",
         "`yield` returns a value from a switch expression "
         "block. `return` exits the enclosing method. Using "
         "`return` inside a switch expression block is a "
         "compilation error."),
    ],
}

# ── Failure Modes ────────────────────────────────────────

FAILURES = {
    "Records": r"""**Failure Mode 1: Mutable component types break immutability**
**Symptom:** Record instances are modified after creation. Unexpected state changes in code that assumes immutability.
**Root Cause:** Record components are final references, but the referenced objects (List, Map, Date) can be mutated externally.
**Diagnostic:**

```
# Find records with mutable component types
grep -rn "record.*List\|record.*Map\|record.*Date" src/
```

**Fix:**
```java
// BAD: mutable list in record
record Team(String name, List<String> members) {}
var team = new Team("A", new ArrayList<>(list));
team.members().add("hacker"); // mutates!

// GOOD: defensive copy in compact constructor
record Team(String name, List<String> members) {
    Team {
        members = List.copyOf(members);
    }
}
```
**Prevention:** Always use `List.copyOf()`, `Map.copyOf()`, or `Set.copyOf()` in compact constructors for collection components.

**Failure Mode 2: Record serialization with different component order**
**Symptom:** Deserialization fails or produces wrong values when record component order is changed between versions.
**Root Cause:** Record serialization uses the canonical constructor with components in declaration order. Reordering components changes the constructor signature.
**Diagnostic:**

```
# Check for serializable records that changed
git diff --name-only HEAD~10 | xargs grep -l "record"
# Verify component order matches serialized data
```

**Fix:**
```java
// BAD: changing component order
// v1: record Point(int x, int y)
// v2: record Point(int y, int x)  // BREAKS!

// GOOD: never reorder components
// Add new components at the end
// Use explicit serialization if order matters
```
**Prevention:** Treat record component order as a public API contract. Never reorder existing components. Add new components at the end.

**Failure Mode 3: Records in JPA entities**
**Symptom:** JPA/Hibernate errors when using records as entities. "No default constructor" or "Cannot set field" errors.
**Root Cause:** JPA requires a no-arg constructor, mutable fields, and setter methods. Records have none of these.
**Diagnostic:**

```
grep -rn "@Entity" src/ | xargs grep "record "
# Records cannot be JPA entities
```

**Fix:**
```java
// BAD: record as JPA entity
@Entity
record User(Long id, String name) {} // FAILS

// GOOD: records for DTOs, classes for entities
@Entity
class UserEntity { /* mutable fields */ }
record UserDto(Long id, String name) {
    static UserDto from(UserEntity e) {
        return new UserDto(e.getId(), e.getName());
    }
}
```
**Prevention:** Use records for DTOs, projections, and value objects. Use regular classes for JPA entities.""",

    "Sealed Classes": r"""**Failure Mode 1: Non-exhaustive switch after adding a new permitted subtype**
**Symptom:** Compilation error in all switch expressions that match on the sealed type after adding a new permitted subclass.
**Root Cause:** Adding a new subtype to the `permits` clause makes existing exhaustive switches incomplete.
**Diagnostic:**

```
# Find all switch expressions on the sealed type
grep -rn "switch.*instanceof\|case.*Shape" src/
# Each must handle the new subtype
```

**Fix:**
```java
// When adding Circle to sealed Shape:
sealed interface Shape
    permits Square, Triangle, Circle {}

// Every switch must be updated:
return switch (shape) {
    case Square s -> s.side() * s.side();
    case Triangle t -> 0.5 * t.base() * t.height();
    case Circle c -> Math.PI * c.radius() * c.radius();
    // Compiler error if Circle case is missing
};
```
**Prevention:** Document all switch sites when defining sealed hierarchies. Consider adding tests that verify all subtypes are handled.

**Failure Mode 2: Sealed class with non-sealed subtype opens the hierarchy**
**Symptom:** External code extends a subtype of the sealed class, bypassing the closed hierarchy.
**Root Cause:** A permitted subtype declared `non-sealed` allows unrestricted extension, breaking exhaustiveness guarantees.
**Diagnostic:**

```
grep -rn "non-sealed" src/
# Each non-sealed subtype is an open extension point
```

**Fix:**
```java
// BAD: non-sealed reopens the hierarchy
sealed interface Result permits Ok, Err {}
non-sealed class Ok implements Result {}
// Anyone can: class WeirdOk extends Ok {}

// GOOD: use final or sealed on subtypes
sealed interface Result permits Ok, Err {}
record Ok(Object value) implements Result {}
record Err(String msg) implements Result {}
// Both are final (records are implicitly final)
```
**Prevention:** Prefer `final` or `record` for leaf subtypes. Use `non-sealed` only when intentional open extension is needed.

**Failure Mode 3: Circular permits dependency**
**Symptom:** Compilation error: "cyclic inheritance" or confusing type hierarchies.
**Root Cause:** Two sealed types permitting each other's subtypes, creating circular dependencies.
**Diagnostic:**

```
grep -rn "sealed.*permits" src/ | sort
# Check for circular references between sealed types
```

**Fix:**
```java
// BAD: circular sealed hierarchy
sealed interface A permits B {}
sealed interface B extends A permits C {}
// (confusing, hard to reason about)

// GOOD: clear tree hierarchy
sealed interface Shape permits Circle, Polygon {}
sealed interface Polygon extends Shape
    permits Triangle, Square {}
record Circle(double r) implements Shape {}
```
**Prevention:** Design sealed hierarchies as strict trees. Each sealed type should have a clear parent and non-overlapping subtypes.""",

    "Text Blocks": (
        '**Failure Mode 1: Unexpected trailing whitespace**\n'
        '**Symptom:** String comparisons fail. JSON/SQL has invisible whitespace at end of lines. Tests pass locally but fail in CI.\n'
        '**Root Cause:** Text blocks preserve trailing whitespace unless lines end with `\\s` escape (JDK 14+). Editors may add/trim trailing spaces.\n'
        '**Diagnostic:**\n\n'
        '```\n'
        '# Visualize whitespace in text block output\n'
        'cat -A output.txt  # Shows $ at line ends, ^I for tabs\n'
        '# Or in Java:\n'
        'System.out.println(textBlock.replace(" ", "."));\n'
        '```\n\n'
        '**Fix:**\n'
        '```java\n'
        '// BAD: invisible trailing spaces\n'
        'String json = ""\"\n'
        '    {"name": "Alice"}   \n'
        '    ""\";  // 3 trailing spaces on line 1\n'
        '\n'
        '// GOOD: use \\s to mark intentional trailing space\n'
        '// or ensure no trailing whitespace\n'
        'String json = ""\"\n'
        '    {"name": "Alice"}\n'
        '    ""\";\n'
        '```\n'
        '**Prevention:** Configure IDE to trim trailing whitespace. Use `.strip()` on text block output when whitespace-sensitive.\n'
        '\n'
        '**Failure Mode 2: Wrong indentation due to closing delimiter position**\n'
        '**Symptom:** Text block has unexpected leading whitespace. Indentation doesn\'t match what\'s visible in source code.\n'
        '**Root Cause:** The closing `""\"` position determines the common leading whitespace baseline. Misplacing it adds or removes indentation.\n'
        '**Diagnostic:**\n\n'
        '```\n'
        '# Print with visible whitespace markers\n'
        'String result = textBlock.replace(" ", ".");\n'
        'System.out.println(result);\n'
        '```\n\n'
        '**Fix:**\n'
        '```java\n'
        '// BAD: closing delimiter at column 0\n'
        'String sql = ""\"\n'
        '    SELECT *\n'
        '    FROM users\n'
        '""\";  // No indent stripped (closing at col 0)\n'
        '\n'
        '// GOOD: closing delimiter aligned with content\n'
        'String sql = ""\"\n'
        '    SELECT *\n'
        '    FROM users\n'
        '    ""\";  // 4-space common indent stripped\n'
        '// Result: "SELECT *\\nFROM users\\n"\n'
        '```\n'
        '**Prevention:** Align the closing `""\"` with the content to control indentation stripping. Understand the common whitespace algorithm.\n'
        '\n'
        '**Failure Mode 3: Text block in annotation breaks compilation**\n'
        '**Symptom:** Compilation error when using text block in annotation value.\n'
        '**Root Cause:** Annotations require compile-time constant expressions. Text blocks ARE constants, but some older annotation processors don\'t handle them.\n'
        '**Diagnostic:**\n\n'
        '```\n'
        '# Check JDK version and annotation processor version\n'
        'javac -version\n'
        '# Update annotation processors to support JDK 15+\n'
        '```\n\n'
        '**Fix:**\n'
        '```java\n'
        '// If annotation processor doesn\'t support text blocks:\n'
        '// BAD: text block in annotation\n'
        '@Query(""\"\n'
        '    SELECT u FROM User u\n'
        '    WHERE u.active = true\n'
        '    ""\")  // May fail with old processors\n'
        '\n'
        '// GOOD: regular string or update processor\n'
        '@Query("SELECT u FROM User u "\n'
        '     + "WHERE u.active = true")\n'
        '```\n'
        '**Prevention:** Ensure annotation processors support JDK 15+. Test with text blocks in annotations during upgrade.'
    ),

    "Switch Expressions": r"""**Failure Mode 1: Missing yield in block form**
**Symptom:** Compilation error: "switch expression does not have a value" in block arrow case.
**Root Cause:** Using `return` instead of `yield` in a switch expression block, or forgetting to yield a value.
**Diagnostic:**

```
grep -rn "case.*->" src/ | grep -v "yield\|;"
# Find block cases that might be missing yield
```

**Fix:**
```java
// BAD: return instead of yield
String result = switch (code) {
    case 200 -> {
        log("OK");
        return "Success"; // ERROR: return exits method
    }
    default -> "Unknown";
};

// GOOD: yield returns value from switch block
String result = switch (code) {
    case 200 -> {
        log("OK");
        yield "Success"; // Correct: yields to switch
    }
    default -> "Unknown";
};
```
**Prevention:** Use `yield` for multi-statement switch expression blocks. Reserve `return` for method exit only.

**Failure Mode 2: Mixing arrow and colon forms**
**Symptom:** Compilation error: "different case kinds used in switch".
**Root Cause:** Attempting to use both arrow (`->`) and colon (`:`) case labels in the same switch.
**Diagnostic:**

```
grep -n "case.*->\|case.*:" src/MyFile.java
# Look for mixed -> and : in same switch block
```

**Fix:**
```java
// BAD: mixing arrow and colon forms
var x = switch (day) {
    case MON -> "Start";
    case FRI:         // ERROR: mixed forms
        yield "End";
    default -> "Mid";
};

// GOOD: consistent arrow form
var x = switch (day) {
    case MON -> "Start";
    case FRI -> "End";
    default -> "Mid";
};
```
**Prevention:** Choose one form per switch block. Arrow form for expressions, colon form only when fall-through is needed.

**Failure Mode 3: Enum exhaustiveness broken by new constant**
**Symptom:** `MatchException` at runtime when a switch expression encounters an enum value added after compilation.
**Root Cause:** Switch was exhaustive at compile time (all enum constants covered), but a new constant was added in a different module without recompiling the switch.
**Diagnostic:**

```
# Check if enum was modified without recompiling
# consumers
javap -p EnumClass.class | grep -c "enum constant"
# Compare with switch case count
```

**Fix:**
```java
// Add a default clause for cross-module enums
String label = switch (status) {
    case ACTIVE -> "Active";
    case INACTIVE -> "Inactive";
    // Defensive default for binary compatibility
    default -> throw new AssertionError(
        "Unknown status: " + status);
};
```
**Prevention:** Add a default clause with AssertionError for enums from external modules. Recompile all consumers when enum changes.""",
}

# ── Related Keywords ─────────────────────────────────────

RELATED = {
    "Records": r"""**Prerequisites (understand these first):**

- Java classes and objects - understanding constructors, fields, methods, equals/hashCode contract
- Immutability - why immutable objects are safer for concurrency and easier to reason about

**Builds on this (learn these next):**

- Sealed classes - combine with records for algebraic data types with exhaustive matching
- Pattern matching (JDK 21) - deconstruct records in switch and instanceof expressions

**Alternatives / Comparisons:**

- Lombok @Data/@Value - annotation-based code generation, works on older JDKs, not language-level
- Kotlin data classes - similar concept in Kotlin with copy() and destructuring""",

    "Sealed Classes": r"""**Prerequisites (understand these first):**

- Inheritance and polymorphism - understanding class hierarchies, abstract classes, interfaces
- Final classes - understanding restriction of extension and its trade-offs

**Builds on this (learn these next):**

- Pattern matching (JDK 21) - exhaustive matching on sealed hierarchies in switch expressions
- Records - combine with sealed classes for complete algebraic data types

**Alternatives / Comparisons:**

- Enum types - simpler closed set of singleton values, but no per-instance data
- Visitor pattern - traditional OOP approach to exhaustive dispatch (more boilerplate)""",

    "Text Blocks": r"""**Prerequisites (understand these first):**

- String handling in Java - String interning, immutability, StringBuilder
- Escape sequences - understanding \n, \t, \", and their limitations

**Builds on this (learn these next):**

- String templates (JDK 21 preview) - string interpolation that may replace .formatted() usage
- Pattern matching with text - regex and parsing multi-line input

**Alternatives / Comparisons:**

- String concatenation with + - traditional approach, poor readability for multi-line
- String.format() / .formatted() - parameterized strings, works with text blocks""",

    "Switch Expressions": r"""**Prerequisites (understand these first):**

- Switch statement (classic) - understanding cases, break, fall-through behavior
- Enum types - the primary type for exhaustive switch expressions

**Builds on this (learn these next):**

- Pattern matching in switch (JDK 21) - matching on types and deconstructing records in switch
- Sealed classes - enables compiler-checked exhaustiveness in switch expressions

**Alternatives / Comparisons:**

- if-else chains - more flexible conditions but no exhaustiveness checking
- Map lookup - O(1) dispatch by key, good for simple value mapping""",
}


def apply_all(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Level 5
    level5_old = (
        "[TODO: Cross-domain pattern recognition. "
        "Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]"
    )
    for kw in KEYWORDS:
        if level5_old in content and kw in LEVEL5:
            content = content.replace(level5_old, LEVEL5[kw], 1)
            changes += 1

    # Quick Reference Card
    qr_old = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]"
    )
    for kw in KEYWORDS:
        if qr_old in content and kw in QUICKREF:
            content = content.replace(qr_old, QUICKREF[kw], 1)
            changes += 1

    # Comparison Table
    for kw in KEYWORDS:
        ct_old = (
            f"[TODO: Include if 2+ named alternatives exist "
            f"for {kw}. Otherwise remove this section.]"
        )
        if ct_old in content and kw in COMPARISON:
            content = content.replace(ct_old, COMPARISON[kw], 1)
            changes += 1

    # Misconceptions
    mc_pat = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )
    for kw in KEYWORDS:
        if kw in MISCONCEPTIONS:
            m = mc_pat.search(content)
            if m:
                rows = MISCONCEPTIONS[kw]
                replacement = "\n".join(
                    f"| {i+1} | {mis} | {real} |"
                    for i, (mis, real) in enumerate(rows)
                )
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Failure Modes
    fm_pat = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )
    for kw in KEYWORDS:
        if kw in FAILURES:
            m = fm_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[kw] + content[m.end():]
                changes += 1

    # Related Keywords
    rk_pat = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n?'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'\n?'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n?'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'\n?'
        r'\*\*Alternatives / Comparisons:\*\*\n\n?'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )
    for kw in KEYWORDS:
        if kw in RELATED:
            m = rk_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[kw] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_all(FILE)
