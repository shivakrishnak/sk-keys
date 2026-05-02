---
layout: default
title: "Annotation Processing (APT)"
parent: "Java Language"
nav_order: 320
permalink: /java-language/annotation-processing-apt/
number: "0320"
category: Java Language
difficulty: ★★★
depends_on: Reflection, Generics, Bytecode, Class Loader
used_by: Spring Core, Serialization / Deserialization, Records (Java 16+)
related: Reflection, invokedynamic, Metaprogramming
tags:
  - java
  - annotation
  - apt
  - deep-dive
  - build
---

# 0320 — Annotation Processing (APT)

⚡ TL;DR — Annotation Processing runs user-written processors at compile time to inspect annotations, generate source files or bytecode, and validate constraints — replacing reflection-at-runtime patterns with compile-time code generation for zero runtime overhead.

| #0320 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Reflection, Generics, Bytecode, Class Loader | |
| **Used by:** | Spring Core, Serialization / Deserialization, Records (Java 16+) | |
| **Related:** | Reflection, invokedynamic, Metaprogramming | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
DI frameworks like Spring, ORM mappers like Hibernate, and serialization libraries like Jackson rely on reflection to discover annotations at runtime. Every startup, the JVM scans thousands of class files reading annotation metadata, calling `getDeclaredFields()`, `isAnnotationPresent()`, and `setAccessible()` thousands of times. This costs startup time (a Spring Boot app can take 5–30 seconds), memory (metadata held in heap), and prohibits GraalVM native image compilation (which cannot perform dynamic reflection discovery).

THE BREAKING POINT:
A microservice needs to start in under 1 second (Kubernetes readiness probe timeout). Spring's annotation scanning takes 8 seconds. The team cannot use the framework. Alternative: write boilerplate wiring code for every bean by hand — hundreds of classes × 10 minutes each = weeks of work that Spring was supposed to eliminate.

THE INVENTION MOMENT:
This is exactly why **Annotation Processing** was created — to move annotation discovery and code generation from runtime reflection to compile time, so that generated wiring code exists as regular `.java` files before the application ever runs.

---

### 📘 Textbook Definition

**Annotation Processing** (APT — Annotation Processing Tool, now integrated into `javac`) is a compile-time metaprogramming facility where user-defined `Processor` implementations are invoked by the Java compiler during compilation. Processors receive a model of the source code's abstract syntax tree, can read annotations, emit diagnostic messages, and generate new `.java` or resource files. The generated files are compiled in subsequent rounds. Standard library: `javax.annotation.processing`. Common users: Lombok (code generation), MapStruct (type-safe mappers), Dagger (DI), Immutables (value types), Micronaut (DI/AOP at compile time).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Annotation processors run as plugins inside javac to read your annotations and generate source code before your app compiles.

**One analogy:**
> A blueprint reviewer stamps all drawings with "approved" and generates a parts list before construction starts. No inspector is needed on the build site because all checking was done at blueprint stage. APT is the blueprint reviewer — it validates annotations and generates boilerplate before the program ever runs.

**One insight:**
The key distinction is WHEN code runs: reflection reads annotations at JVM startup (runtime); annotation processors generate code at `javac` time (compile time). The generated code is plain Java, compiled like any other class — type-safe, JIT-optimised, GraalVM-compatible, and zero overhead at runtime.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Processors run inside `javac` — before the application is compiled, not after.
2. Processors can read source elements (classes, methods, fields) but cannot modify existing source code — they can only generate new files.
3. Processing runs in rounds: if a processor generates new files, the new files are re-processed until no new files are generated.

DERIVED DESIGN:
Given invariant 2, annotation processors are additive — they generate companion classes, not patches. Lombok appears to modify source (adding getters/setters) but actually patches the AST directly using `javac` internals (`com.sun.tools.javac.tree`), which is not the official APT API and breaks with certain compilers. Standard APT (JSR-269) is strictly additive.

Given invariant 3, a processor that generates a class containing annotations is automatically re-processed. Cycles must be tracked to avoid infinite loops.

```
┌────────────────────────────────────────────────┐
│       Annotation Processing Rounds            │
│                                                │
│  Round 1:                                      │
│    javac parses source → element model         │
│    Processor reads @MyAnnotation → generates  │
│    NewClass.java                               │
│  Round 2:                                      │
│    javac parses NewClass.java                  │
│    Processor finds no new @MyAnnotation        │
│    → Final round                              │
│  Compilation continues with all .java files   │
└────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Zero runtime overhead for generated code; compile-time validation of annotation constraints; GraalVM native image compatible; fast startup.
Cost: Build time increases (processor execution per module); generated code debugging requires understanding generated files; processor errors manifest as confusing `javac` errors; IDE support varies (IntelliJ handles most processors well; edge cases exist).

---

### 🧪 Thought Experiment

SETUP:
A mapper framework needs to convert `UserEntity` to `UserDto`. Two approaches: runtime reflection (Jackson, Dozer) or compile-time generation (MapStruct with APT).

WITH RUNTIME REFLECTION (no APT):
At startup: reflect on `UserEntity`, find matching fields in `UserDto`, build a mapping plan. Every `map(entity)` call: iterate fields, call `field.get(entity)`, call `field.set(dto, value)`. Per-mapping overhead: ~1μs. 10M mappings/second = 10s of CPU in reflection overhead.

WITH APT (MapStruct):
At compile time: processor reads `@Mapper` annotation, inspects source model of `UserEntity` and `UserDto`, generates:
```java
public class UserMapperImpl implements UserMapper {
    public UserDto map(UserEntity e) {
        UserDto dto = new UserDto();
        dto.setName(e.getName());
        dto.setEmail(e.getEmail());
        return dto;
    }
}
```
Runtime: direct Java method calls — JIT-inlineable. Zero reflection. ~10ns per mapping.

THE INSIGHT:
APT shifts the work of introspection from every program run to a single compile. The generated code is as fast as hand-written code. The developer still writes only annotations — the framework generates the implementation automatically at compile time.

---

### 🧠 Mental Model / Analogy

> An annotation processor is a printing press for boilerplate code. A developer stamps `@GenerateBuilder` on a class. The printing press (processor) reads the stamp during compilation, checks the class layout, and prints a `Builder` class file. The application ships with the pre-printed Builder — no printing at runtime.

"Stamp (@Annotation)" → annotation on a class.
"Printing press" → annotation processor.
"Checking class layout" → reading the `Element` model in the processor.
"Printing a file" → calling `filer.createSourceFile("BuilderClass").openWriter()`.
"Pre-printed file in the app" → generated class compiled with the rest of the application.

Where this analogy breaks down: A printing press produces a fixed design. Annotation processors can produce arbitrarily complex, dynamic code based on the annotated class's structure — closer to a typewriter that writes custom text per stamp.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you put an annotation like `@Getter` on your class, a tool reads it during compilation and writes extra Java code files for you — like having an assistant generate boilerplate while you describe what you want via annotations.

**Level 2 — How to use it (junior developer):**
Most developers use APT indirectly — Lombok's `@Data`, MapStruct's `@Mapper`, Dagger's `@Component`. These work by adding the processor's `.jar` to the compiler's annotation processor path (`annotationProcessorPaths` in Maven). The generated files appear in `target/generated-sources/`. Never edit generated files. IDE support is essential — install the Lombok IntelliJ plugin, for example.

**Level 3 — How it works (mid-level engineer):**
Implement `javax.annotation.processing.AbstractProcessor`. Declare supported annotations with `@SupportedAnnotationTypes("com.example.MyAnnotation")` and source version with `@SupportedSourceVersion`. Override `process(Set<TypeElement> annotations, RoundEnvironment roundEnv)`. Use `roundEnv.getElementsAnnotatedWith(MyAnnotation.class)` to find annotated elements. Use `processingEnv.getFiler().createSourceFile(name)` to write generated files. Return `true` if you claim the annotation (no further processors see it), `false` to let others see it too.

**Level 4 — Why it was designed this way (senior/staff):**
APT (the original JSR-269 standard, replacing the earlier `apt` tool) was designed as a strictly additive, source-level API deliberately to avoid the instability of AST mutation (which Lombok uses). This prevents processors from interfering with each other or with the compiler's internal state. The tradeoff is that APT cannot add methods to existing classes — it can only create new classes. This forces patterns like generated `*Impl` or `*Builder` companions. Project Lombok works around this using `com.sun.tools.javac.tree.JCTree` manipulation — not standardised, not guaranteed to work across JDK versions. The GraalVM native image use case (Micronaut, Quarkus) has strongly revived APT interest because native image requires all reflection to be declared upfront, and APT-generated code avoids the runtime reflection problem entirely.

---

### ⚙️ How It Works (Mechanism)

**Minimal processor skeleton:**
```java
@SupportedAnnotationTypes("com.example.BuilderSpec")
@SupportedSourceVersion(SourceVersion.RELEASE_21)
public class BuilderProcessor extends AbstractProcessor {

    @Override
    public boolean process(
        Set<? extends TypeElement> annotations,
        RoundEnvironment roundEnv
    ) {
        for (Element el :
             roundEnv.getElementsAnnotatedWith(
                BuilderSpec.class)) {
            if (el.getKind() != ElementKind.CLASS) {
                processingEnv.getMessager().printMessage(
                    Diagnostic.Kind.ERROR,
                    "@BuilderSpec only on classes", el
                );
                continue;
            }
            generateBuilder((TypeElement) el);
        }
        return true; // claim this annotation
    }

    private void generateBuilder(TypeElement cls) {
        String name = cls.getSimpleName() + "Builder";
        try (Writer w = processingEnv.getFiler()
             .createSourceFile(
                cls.getQualifiedName() + "Builder"
             ).openWriter()) {
            w.write("public class " + name + " { ... }");
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
```

**Service discovery (META-INF):**
Processors are registered in
`META-INF/services/javax.annotation.processing.Processor`
— one fully-qualified class name per line. Build tools like Maven (`maven-compiler-plugin annotationProcessorPaths`) and Gradle (`annotationProcessor` dependency config) handle this automatically for known processors.

**Using the processor in Maven:**
```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-compiler-plugin</artifactId>
  <configuration>
    <annotationProcessorPaths>
      <path>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct-processor</artifactId>
        <version>1.5.5.Final</version>
      </path>
    </annotationProcessorPaths>
  </configuration>
</plugin>
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Developer annotates class with @Mapper]
    → [mvn compile / javac invoked]
    → [javac parses source → Element model]
    → [APT: processor.process() called] ← YOU ARE HERE
    → [Processor reads @Mapper, inspects fields]
    → [Generates UserMapperImpl.java in target/]
    → [Round 2: javac parses generated file]
    → [No new annotations → final round]
    → [Both UserMapper.class + UserMapperImpl.class produced]
    → [Application starts: uses generated impl, no reflection]
```

FAILURE PATH:
```
[Processor finds invalid annotation usage]
    → [processingEnv.getMessager().printMessage(ERROR, ...)]
    → [javac compilation fails with processor error]
    → [Build log shows processor error with source location]
    → [Developer fixes annotation usage → recompile]
```

WHAT CHANGES AT SCALE:
In large mono-repo builds, annotation processing adds per-module compile time. A Maven project with 200 modules each running MapStruct, Lombok, and Dagger processors can add minutes to incremental builds. Solutions: incremental annotation processing (Gradle supports this; Maven does not natively); parallel module builds; splitting generated code into separate modules so processors run once.

---

### 💻 Code Example

Example 1 — Reading build-time annotations (validation):
```java
@SupportedAnnotationTypes("com.example.NotNull")
@SupportedSourceVersion(SourceVersion.RELEASE_21)
public class NotNullProcessor extends AbstractProcessor {
    @Override
    public boolean process(
        Set<? extends TypeElement> annotations,
        RoundEnvironment roundEnv
    ) {
        for (Element el :
             roundEnv.getElementsAnnotatedWith(
                NotNull.class)) {
            if (el.getKind() == ElementKind.FIELD) {
                VariableElement field = (VariableElement) el;
                if (field.asType().getKind().isPrimitive()) {
                    processingEnv.getMessager()
                        .printMessage(
                        Diagnostic.Kind.ERROR,
                        "@NotNull on primitive has no effect",
                        el
                    );
                }
            }
        }
        return true;
    }
}
```

Example 2 — Reading annotation values:
```java
// Given annotation: @Table(name = "users")
TypeElement tableAnnotation = processingEnv
    .getElementUtils()
    .getTypeElement("com.example.Table");

for (Element el :
     roundEnv.getElementsAnnotatedWith(tableAnnotation)) {
    AnnotationMirror mirror = el.getAnnotationMirrors()
        .stream()
        .filter(a -> a.getAnnotationType()
                      .asElement().equals(tableAnnotation))
        .findFirst().orElseThrow();

    Map<? extends ExecutableElement,
        ? extends AnnotationValue> values =
            mirror.getElementValues();

    String tableName = values.entrySet().stream()
        .filter(e -> e.getKey().getSimpleName()
                      .contentEquals("name"))
        .map(e -> e.getValue().getValue().toString())
        .findFirst().orElse("unknown");

    System.out.println("Table name: " + tableName);
}
```

Example 3 — MapStruct usage (consuming APT-generated code):
```java
// Developer writes:
@Mapper(componentModel = "spring")
public interface OrderMapper {
    OrderDto toDto(OrderEntity entity);
    OrderEntity toEntity(OrderDto dto);
}

// MapStruct APT generates:
@Component
public class OrderMapperImpl implements OrderMapper {
    public OrderDto toDto(OrderEntity entity) {
        if (entity == null) return null;
        OrderDto dto = new OrderDto();
        dto.setId(entity.getId());
        dto.setTotal(entity.getTotal());
        return dto;
    }
    public OrderEntity toEntity(OrderDto dto) { ... }
}
// Zero reflection. Direct calls. JIT-inlineable.
```

---

### ⚖️ Comparison Table

| Approach | When Runs | Runtime Overhead | Native Image | Debug Ease | Best For |
|---|---|---|---|---|---|
| **APT (compile-time)** | javac build | Zero | Compatible | Generated source readable | DI, mappers, builders |
| Runtime Reflection | JVM startup/request | High (first use) | Needs config | Stacktrace-based | Dynamic unknown classes |
| MethodHandle (runtime) | At call time | Low (after warmup) | Partial | Medium | Performance-sensitive dynamics |
| Byte Buddy (runtime codegen) | First use / startup | Medium | Needs config | Complex | Dynamic proxies, agents |

How to choose: Prefer APT for any framework feature where the class structure is known at compile time. Use reflection for code that genuinely cannot know its targets at compile time (plugins, script engines). Use MethodHandle for performance-critical dynamic dispatch.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Lombok uses the standard APT API | Lombok uses `com.sun.tools.javac.tree.JCTree` — internal javac APIs — to mutate the AST, which is NOT standard APT. It works but is not guaranteed across JDK versions and is why Lombok usage requires version-specific compatibility |
| APT processors can modify existing classes | Standard APT (JSR-269) is strictly additive — processors can only create new files. Any tool that appears to modify existing classes does so through non-standard compiler internals |
| Generated files don't need to be committed | Convention varies: Lombok-generated code appears only in memory (AST mutation), never in files. MapStruct generates `.java` files in `target/generated-sources` that are NOT committed. Always check your VCS ignore rules |
| Annotation processors slow down compilation dramatically | Modern processors (MapStruct, Dagger) are well-optimised and add milliseconds per module. Complex or naive processors that re-scan entire element trees cause problems. Initial Maven builds feel slow; incremental Gradle builds are fast with caching |
| APT and runtime annotation reading are mutually exclusive | They work together. `@Transactional` is both processed at compile time (validation via APT in some frameworks) and read at runtime via Spring's proxy-based AOP. The same annotation can have both compile-time and runtime processors |

---

### 🚨 Failure Modes & Diagnosis

**Processor Not Running — Missing Configuration**

Symptom:
`@Mapper` annotation has no effect; `*Impl` class not generated. Compiler produces no errors. Build succeeds but generated class is missing.

Root Cause:
Processor jar not in annotation processor path. Maven uses regular `<dependency>` scope but annotation processor scope is separate.

Diagnostic:
```bash
# Maven: check if processor is in annotation processor path
mvn dependency:tree | grep mapstruct
# Must be in annotationProcessorPaths, not just dependencies

# Verbose compilation shows active processors:
mvn compile -X 2>&1 | grep "annotation processor"
```

Fix:
```xml
<!-- Maven: add to annotationProcessorPaths -->
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <configuration>
    <annotationProcessorPaths>
      <path>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct-processor</artifactId>
        <version>${mapstruct.version}</version>
      </path>
    </annotationProcessorPaths>
  </configuration>
</plugin>
```

Prevention: Verify processor configuration when adding a new APT-based library. Test with a minimal annotated class after setup.

---

**Infinite Processing Loop**

Symptom:
Compilation hangs or produces "too many rounds" error. CPU spikes during compilation.

Root Cause:
Processor generates a file containing the annotation it processes, causing the next round to reprocess the file endlessly.

Diagnostic:
```bash
# Limit rounds in javac (not standard, but some tools support):
javac -proc:only -processorpath processor.jar \
      -Xlint:processing *.java
# Watch for repeated round messages
```

Fix:
```java
// BAD: generates a file annotated with @BuilderSpec
// → causes infinite rounds
void generateBuilder(TypeElement el) {
    writer.write("@BuilderSpec class GeneratedBuilder {...}");
}

// GOOD: generated file does NOT contain @BuilderSpec
void generateBuilder(TypeElement el) {
    // No @BuilderSpec in generated code
    writer.write("class " + name + "Builder {...}");
}
```

Prevention: Generated files must not contain the annotations your processor responds to, unless you track generated types and skip them in subsequent rounds using a `Set<String> processed`.

---

**IDE Not Recognising Generated Code**

Symptom:
IDE shows "Cannot resolve symbol" errors on generated classes. Compilation succeeds in terminal but IDE reports errors.

Root Cause:
IDE annotation processor settings not configured to match build tool configuration.

Diagnostic:
```bash
# IntelliJ: File → Settings → Build → Compiler
#           → Annotation Processors
# Check: "Enable annotation processing" is checked
# Check: processor path matches Maven config
```

Fix:
IntelliJ: Enable annotation processing in settings. Use "Delegate to Maven" so IntelliJ uses Maven's processor configuration directly.

Prevention: Add `target/generated-sources/annotations` to IDE source roots. For Gradle, use `idea { module { generatedSourceDirs += ... } }`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Reflection` — APT is the compile-time alternative to runtime reflection; understanding what reflection does at runtime motivates why APT is preferable when possible
- `Generics` — processors read `TypeMirror` objects that represent generic types; understanding erasure and generics is needed to correctly generate generic code
- `Bytecode` — some processors generate bytecode (via ASM, ByteBuddy) rather than source; bytecode knowledge is needed for those cases

**Builds On This (learn these next):**
- `Spring Core` — Spring's Spring Native (AOT compilation) uses APT-style compile-time processing to eliminate runtime reflection for GraalVM native image
- `Serialization / Deserialization` — Jackson's `jackson-modules-java-base` supports APT-generated ser/deser code via `@JsonCreator` and `@JsonValue`

**Alternatives / Comparisons:**
- `Reflection` — runtime annotation reading; required when class structure is unknown at compile time; much slower than APT-generated code
- `invokedynamic` — a dynamic dispatch mechanism; orthogonal to APT but both address the "late-bound code execution" problem at different levels

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Compile-time plugin that reads annotations│
│              │ and generates new .java source files      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Runtime reflection is slow on startup and │
│ SOLVES       │ incompatible with GraalVM native image    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Generated code is compiled, type-safe,    │
│              │ JIT-optimised, and has zero runtime       │
│              │ overhead — no reflection needed at start  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ You want automatic code generation at     │
│              │ compile time — mappers, builders, DI wiring│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Class structure is dynamic/unknown at     │
│              │ compile time (plugins, scripting engines) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero runtime cost vs increased build time;│
│              │ IDE support requires correct configuration │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "javac plugin that prints code so you     │
│              │  don't have to — before it runs"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Core (AOT) → GraalVM Native Image  │
│              │ → invokedynamic                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** MapStruct generates `OrderMapperImpl` implementing `OrderMapper` at compile time. At runtime, Spring injects this generated implementation as a `@Component`. Trace the complete path: from the developer writing `@Mapper(componentModel = "spring")` to Spring successfully autowiring `OrderMapper orderMapper` in a service — listing every tool (APT processor, javac, Spring boot autoconfiguration, Spring DI) involved in each step, and explaining why removing MapStruct from the annotationProcessorPaths but keeping it in regular dependencies causes a specific, identifiable runtime error rather than a compile error.

**Q2.** Lombok's `@Data` annotation appears to add getters, setters, `equals()`, `hashCode()`, and `toString()` methods to a class without creating new files. DeeLombok (Lombok's delombok tool) can produce the equivalent source code. Explain precisely why Lombok's approach (AST mutation via `com.sun.tools.javac.tree`) is fundamentally different from standard APT (JSR-269), what specific JVM or JDK version compatibility risks this creates, and why the Lombok team has not migrated to standard APT despite these risks.

