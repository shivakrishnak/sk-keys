---
layout: default
title: "Text Blocks"
parent: "Java Language"
nav_order: 65
permalink: /java-language/text-blocks/
---
# 065 — Text Blocks (Java 15+)

`#java` `#java15` `#string` `#readability`

⚡ TL;DR — Text blocks let you write multi-line strings with `"""` delimiters, automatically removing common leading whitespace — making embedded SQL, JSON, HTML, and XML readable without escape clutter.

| #065 | Category: Java Language | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | String, String Literals | |
| **Used by:** | SQL queries, JSON/XML templates, HTML snippets | |

---

### 📘 Textbook Definition

A **text block** is a multi-line string literal delimited by three double-quote characters (`"""`). The opening delimiter is followed by optional whitespace and a mandatory newline. The compiler strips the common leading indentation (incidental whitespace) from all content lines, normalises line endings to `\n`, and applies escape sequences. The resulting value is a regular `java.lang.String`.

---

### 🟢 Simple Definition (Easy)

Text blocks let you paste multi-line content (SQL, JSON, HTML) directly into code without escape characters. Just wrap it in `"""..."""` and Java handles the rest. No more `+` concatenation, no more `\"` clutter.

---

### 🔵 Simple Definition (Elaborated)

Before text blocks, writing a multi-line SQL query in Java meant either: a horrible string concatenation ladder, or a single line with `\n` everywhere. Text blocks let you write the query exactly as it would look in a SQL editor, indented naturally to match your code indentation. The compiler automatically removes the leading spaces that come from your code indentation (called incidental whitespace) so the resulting string contains only the content you care about.

---

### 🔩 First Principles Explanation

**The problem — embedding content in string literals:**

```
String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 30\n" +
              "}";

Problems:
  1. Every " requires \" — noise drowns out content
  2. Every newline requires explicit \n + line continuation
  3. Indentation of the Java code bleeds into the string
  4. Can't visually scan the JSON — it looks nothing like JSON
```

**The solution — a literal that IS the content:**

```java
String json = """
        {
          "name": "Alice",
          "age": 30
        }
        """;

Benefits:
  1. No escape sequences for quotes
  2. Real line breaks — what you see is what you get
  3. Incidental whitespace automatically stripped
  4. Content is visually identical to the embedded format
```

**How incidental whitespace stripping works:**

```
Column positions (spaces = incidental):

        {                   ← 8 spaces before {
          "name": "Alice",  ← 10 spaces before "
        }                   ← 8 spaces before }
        """                 ← 8 spaces before closing """

Common indent = 8 spaces (position of closing """ determines it)
After stripping: {
                   "name": "Alice",
                 }
```

---

### ❓ Why Does This Exist — Why Before What

```
Without text blocks — real-world pain:

String sql = "SELECT u.name, o.total\n" +
             "FROM users u\n" +
             "JOIN orders o ON u.id = o.user_id\n" +
             "WHERE u.active = true\n" +
             "  AND o.total > ?\n" +
             "ORDER BY o.total DESC";

Issues:
  ✗ Hard to read — cognitive overhead from + and \n
  ✗ Hard to copy/paste — must add/remove concatenation
  ✗ Easy to forget \n → silent bug (queries merge into one line)
  ✗ Can't be formatted like real SQL

With text blocks:

String sql = """
        SELECT u.name, o.total
        FROM users u
        JOIN orders o ON u.id = o.user_id
        WHERE u.active = true
          AND o.total > ?
        ORDER BY o.total DESC
        """;

  ✓ Reads exactly like SQL
  ✓ Copy/paste between SQL editor and Java without transformation
  ✓ No escape mess
  ✓ Indentation controlled by closing """ position
```

---

### 🧠 Mental Model / Analogy

> Text blocks are like **sticky notes on glass** — you write what you want on the note, stick it on the glass (your code), and what you see on the note IS what you get. The glass frame (code indentation) doesn't become part of the note's content.

---

### ⚙️ How It Works

```
Opening delimiter rules:
  """ must be followed by optional whitespace + mandatory newline
  Content starts on the NEXT line

Closing delimiter determines common indent:
  Position of closing """ (or leftmost content line) sets
  how many leading spaces to strip from every content line

Escape sequences (special to text blocks):
  \   at end-of-line  → line continuation (no newline in result)
  \s  explicit space  → preserves trailing space on that line
  \"  still works but rarely needed
  \\  literal backslash

Result type: java.lang.String — identical to any other String
```

---

### 🔄 How It Connects

```
Text Block
    │
    ├─ Opening: """<newline>
    │
    ├─ Content lines (raw)
    │      └─ incidental whitespace stripped (by closing """ pos)
    │      └─ line endings normalised to \n
    │      └─ escape sequences processed
    │
    └─ Result: String (interned like any other string literal)
                  │
                  └─ Can call: .formatted(), .stripIndent(),
                               .translateEscapes(), .indent()
```

---

### 💻 Code Example

```java
// JSON embedding
String json = """
        {
          "name": "Alice",
          "email": "alice@example.com",
          "roles": ["admin", "user"]
        }
        """;
// Starts with '{', ends with '}' + newline
// No escape characters needed for inner quotes

// SQL query
String sql = """
        SELECT p.name, SUM(oi.quantity * oi.price) AS total
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        WHERE p.category = 'electronics'
        GROUP BY p.id
        HAVING total > 100
        ORDER BY total DESC
        LIMIT 20
        """;

// HTML template
String html = """
        <div class="card">
          <h2>%s</h2>
          <p>%s</p>
        </div>
        """.formatted(title, body);  // works with String.formatted()
```

```java
// Controlling the trailing newline

// With trailing newline (closing """ on its own line):
String withNewline = """
        hello
        world
        """;
// value = "hello\nworld\n"

// Without trailing newline (closing """ on last content line):
String noNewline = """
        hello
        world""";
// value = "hello\nworld"
```

```java
// Line continuation — \<newline> merges lines
String oneLiner = """
        This is actually \
        one single line \
        with no newlines.
        """;
// value = "This is actually one single line with no newlines.\n"

// Explicit trailing space — \s prevents stripping
String padded = """
        line one   \s
        line two   \s
        """;
// Trailing spaces preserved by \s
```

```java
// Indentation control — the closing """ controls stripping
String lessIndent = """
    content here
    """;
// 4 spaces stripped (closing """ at column 4)

String moreIndent = """
            content here
            """;
// 12 spaces stripped — content ends up as "content here\n"

// Runtime method: String.stripIndent() — same algorithm at runtime
String dynamic = someMultiLineString.stripIndent();
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Text blocks are a new String type | They produce a regular `java.lang.String` |
| Opening `"""` can be on same line as content | Opening `"""` MUST be followed by a newline — content starts next line |
| All leading spaces are stripped | Only the *common* indent (incidental whitespace) is stripped |
| Trailing spaces are preserved automatically | Trailing spaces stripped unless protected with `\s` |
| Text blocks don't need escape for `\` | `\\` still needed for a literal backslash |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Opening delimiter on same line as content**

```java
// ❌ Compile error — content cannot start on same line as """
String s = """hello
        world""";

// ✅ Correct
String s = """
        hello
        world
        """;
```

**Pitfall 2: Unexpected trailing newline**

```java
// Closing """ on own line adds trailing \n
String s = """
        SELECT 1
        """;
// s equals "SELECT 1\n" — may break exact-match comparisons

// Fix: put closing """ on last content line to omit trailing newline
String s = """
        SELECT 1""";
// s equals "SELECT 1"
```

**Pitfall 3: Mixed indentation (tabs vs spaces)**

```java
// Mixing tabs and spaces for indentation → incidental whitespace algorithm
// may leave unexpected leading chars
// Rule: use consistent indentation (all spaces, or all tabs) in text blocks
```

---

### 🔗 Related Keywords

- **String** — text blocks produce regular `java.lang.String`
- **`String.formatted()`** — pair with `%s` placeholders in text blocks
- **`String.stripIndent()`** — same stripping algorithm, available at runtime
- **`String.translateEscapes()`** — process `\n`, `\t` etc. in runtime strings
- **`String.indent(int n)`** — add/remove indent from multi-line string

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Multi-line string literal with auto indent    │
│              │ stripping — no escape clutter for embedded    │
│              │ SQL/JSON/HTML/XML                             │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Any embedded multi-line content: SQL, JSON,   │
│              │ HTML, XML, YAML, GraphQL queries              │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Single-line strings — normal literals are     │
│              │ shorter and equally readable                  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "What you indent for code structure,          │
│              │  the compiler strips — what you write         │
│              │  is what you get in the string"               │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ String.formatted() → String.stripIndent()     │
│              │ → Records → Pattern Matching                  │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a text block used as a SQL template. You move the closing `"""` two spaces to the right by accident. What happens to the resulting string — will it compile, and will the output change?

**Q2.** How does `\` (line continuation) differ from explicitly writing the content on one line? Are there any differences in the resulting `String` value?

**Q3.** Can text blocks be used in annotations (`@SuppressWarnings`, `@Query`)? What limitations exist?

