---
layout: default
title: "Annotation Processing (APT)"
parent: "Java Fundamentals"
nav_order: 59
permalink: /java/annotation-processing-apt/
number: "059"
category: Java Language
difficulty: ★★★
depends_on: Annotations, Reflection, Compiler API
used_by: Lombok, MapStruct, Dagger 2, Spring (compile-time), Auto-Value
tags: #java #advanced #annotations #apt #codegen
---

# 059 — Annotation Processing (APT)

`#java` `#advanced` `#annotations` `#apt` `#codegen`

⚡ TL;DR — A compile-time code generation hook: `@Getter` on a class triggers Lombok to write the getter source before javac finishes — zero runtime cost, all errors caught at compile time.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #059         │ Category: Java Language              │ Difficulty: ★★★           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Annotations, Reflection, Compiler API                             │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Lombok, MapStruct, Dagger 2, Spring, Auto-Value, Record Builder   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Textbook Definition

Annotation Processing (APT — Annotation Processing Tool) is a Java compiler feature that allows custom code to run during compilation. Processors extend `AbstractProcessor` and are invoked by `javac` when their supported annotation types are found. They can generate new source files, resource files, or emit compiler errors/warnings — all before the final `.class` files are produced. Processors operate on the AST via the `javax.annotation.processing` and `javax.lang.model` APIs.

---

## 🟢 Simple Definition (Easy)

APT is about writing code that **writes code**. You put `@Builder` on your class, and at compile time a processor generates a `UserBuilder` class for you — before your code even finishes compiling. The generated class is real Java that the compiler then also compiles.

---

## 🔵 Simple Definition (Elaborated)

Unlike runtime reflection (which reads class structure at runtime), APT happens **before** bytecode is produced. Processors are plugins to the compiler itself. This gives them access to the full source code model, lets them validate annotations with compile-time errors, and generates boilerplate with zero runtime overhead — the generated code is just regular Java classes.

---

## 🔩 First Principles Explanation

**Compilation pipeline with APT:**
```
Source (.java)
    ↓ javac round 1
Annotations discovered → call registered processors
    ↓ processors run
New .java files generated (e.g., UserBuilder.java)
    ↓ javac round 2 (new files compiled)
Annotations in new files → processors run again (until stable)
    ↓ Final bytecode (.class) produced
```

**Two types of processors:**
1. **Source generators** (Lombok, MapStruct, Dagger): write new `.java` files
2. **Validators** (Bean Validation APT, Error-Prone): emit compiler errors/warnings

---

## ❓ Why Does This Exist (Why Before What)

Repetitive boilerplate (getters, setters, builders, mappers, DI wiring) wastes developer time and clutters codebases. Runtime alternatives (reflection) add overhead and defer errors. APT eliminates the boilerplate at source level with **zero runtime cost** and **compile-time error detection**.

---

## 🧠 Mental Model / Analogy

> APT is like a **ghostwriter hired by the compiler**. You write notes (`@Builder`), and before the publisher (JVM) gets the final manuscript, the ghostwriter fills in all the chapters (builder code). The publisher only ever sees the complete, filled-in manuscript — they don't know anyone added boilerplate.

---

## ⚙️ How It Works (Mechanism)

```
1. Register processor in META-INF/services/javax.annotation.processing.Processor
   OR use @AutoService(Processor.class) from Google AutoService

2. Implement AbstractProcessor
   @SupportedAnnotationTypes("com.example.Builder")
   @SupportedSourceVersion(SourceVersion.RELEASE_17)
   public class BuilderProcessor extends AbstractProcessor {
       @Override
       public boolean process(Set<? extends TypeElement> annotations,
                              RoundEnvironment roundEnv) {
           for (Element e : roundEnv.getElementsAnnotatedWith(Builder.class)) {
               // generate source using processingEnv.getFiler()
               JavaFileObject f = processingEnv.getFiler()
                   .createSourceFile(e.getSimpleName() + "Builder");
               // write Java source to f.openWriter()
           }
           return true;  // claim the annotation (others won't process it)
       }
   }

3. Tools: JavaPoet (code generation), Javaparser, Filer API
4. Build systems: Maven (maven-compiler-plugin annotationProcessors),
                  Gradle (annotationProcessor configuration)
```

---

## 🔄 How It Connects (Mini-Map)

```
[@Getter annotation in source]
       ↓ javac invokes Lombok processor
[BuilderProcessor.process() runs]
       ↓ generates
[UserBuilder.java written to generated-sources/]
       ↓ compiled alongside your code
[UserBuilder.class in output] → zero runtime overhead
```

---

## 💻 Code Example

```java
// 1. Using Lombok (APT under the hood)
@Data          // generates getters, setters, equals, hashCode, toString
@Builder       // generates UserBuilder inner class
@AllArgsConstructor
@NoArgsConstructor
public class User {
    private String name;
    private int    age;
    private String email;
}
// After APT: User.getName(), User.builder().name("Alice").age(30).build() all work

// 2. Using MapStruct (APT generates mapper implementation)
@Mapper
public interface UserMapper {
    UserDto toDto(User user);
    User    toEntity(UserDto dto);
}
// APT generates: UserMapperImpl with field-by-field copy logic

// 3. Minimal custom processor (conceptual)
@SupportedAnnotationTypes("com.example.GenerateFactory")
@SupportedSourceVersion(SourceVersion.RELEASE_17)
public class FactoryProcessor extends AbstractProcessor {
    @Override
    public boolean process(Set<? extends TypeElement> annotations,
                           RoundEnvironment roundEnv) {
        for (Element element : roundEnv.getElementsAnnotatedWith(GenerateFactory.class)) {
            String className = element.getSimpleName() + "Factory";
            try {
                JavaFileObject fileObject =
                    processingEnv.getFiler().createSourceFile(className);
                try (PrintWriter out = new PrintWriter(fileObject.openWriter())) {
                    out.println("public class " + className + " {");
                    out.println("  public static " + element.getSimpleName()
                        + " create() { return new " + element.getSimpleName() + "(); }");
                    out.println("}");
                }
            } catch (IOException e) {
                processingEnv.getMessager().printMessage(
                    Diagnostic.Kind.ERROR, e.getMessage());
            }
        }
        return true;
    }
}

// 4. Dagger 2 — APT for compile-time DI (vs Spring's runtime reflection)
@Component
interface AppComponent {
    UserService userService();
}
// APT generates DaggerAppComponent with all wiring code
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| APT runs at runtime | Runs at compile time; zero runtime overhead |
| Lombok uses reflection | Lombok uses APT to modify the AST before bytecode generation |
| APT can modify existing class bodies | Standard APT only generates new files; Lombok uses non-standard AST modification |
| APT is only for code generation | Also used for validation (emit errors) and documentation generation |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Incremental compilation issues**
Some processors don't work well with incremental compilation (Gradle). Generated files may not regenerate when they should.
Fix: use `@IncrementalAnnotationProcessor(ISOLATING)` or `AGGREGATING` type when writing processors.

**Pitfall 2: Hard to debug**
Processor errors appear as odd compile errors. Generated source may be hidden.
Fix: configure Maven/Gradle to output generated sources; add `-Xlint:processing` for warnings.

**Pitfall 3: Processor ordering dependencies**
Processor A's output needs to be processed by Processor B — but ordering is not guaranteed.
Fix: use multiple compilation rounds (`RoundEnvironment.processingOver()`); design for multiple rounds.

---

## 🔗 Related Keywords

- **Reflection (#058)** — runtime equivalent; more flexible but slower
- **Annotations** — the mechanism APT hooks into
- **Lombok** — most widely used APT library (boilerplate elimination)
- **MapStruct** — APT-based type-safe mapper generator
- **Dagger 2** — APT-based compile-time DI framework; contrast with Spring's runtime DI

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Compile-time code generation via annotation   │
│              │ processors; zero runtime cost                 │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Generating boilerplate (builders, mappers,    │
│              │ DI wiring) that would be error-prone manually │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ When Java Records / sealed classes solve the  │
│              │ problem natively (Java 16+)                   │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Compile-time ghostwriter: annotations trigger │
│              │  code generation before javac finishes"       │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Lombok → MapStruct → Dagger2 → JavaPoet       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** Why does Dagger 2 (APT-based DI) start faster than Spring (reflection-based DI)?
**Q2.** How does Lombok modify existing class bodies when the standard APT API only allows creating new files?
**Q3.** What is the difference between an `ISOLATING` and `AGGREGATING` annotation processor for incremental compilation?

