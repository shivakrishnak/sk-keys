---
layout: default
title: "Annotation Processing (APT)"
parent: "Java Language"
nav_order: 320
permalink: /java-language/annotation-processing/
number: "320"
category: Java Language
difficulty: ★★★
depends_on: "Reflection, Annotations, Generics, javac compilation pipeline"
used_by: "Lombok, MapStruct, Dagger, AutoValue, Spring AOT, Hibernate Metamodel"
tags: #java, #annotation-processing, #code-generation, #compile-time, #lombok, #mapstruct
---

# 320 — Annotation Processing (APT)

`#java` `#annotation-processing` `#code-generation` `#compile-time` `#lombok` `#mapstruct`

⚡ TL;DR — **Annotation Processing (APT)** runs custom processors during `javac` compilation to inspect annotations and generate new source/class files — enabling zero-runtime-cost code generation (Lombok `@Data`, MapStruct mappers, Dagger DI).

| #320 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Reflection, Annotations, Generics, javac compilation pipeline | |
| **Used by:** | Lombok, MapStruct, Dagger, AutoValue, Spring AOT, Hibernate Metamodel | |

---

### 📘 Textbook Definition

**Annotation Processing (APT — Annotation Processing Tool)**: a standard hook in the Java compiler (`javac`) that allows custom `AbstractProcessor` implementations to inspect annotated source code elements during compilation and generate new Java source files or class files. Processors are registered via `META-INF/services/javax.annotation.processing.Processor`. The process runs in multiple rounds: each round may generate new source files that trigger subsequent rounds. Key API: `javax.annotation.processing.AbstractProcessor`, `ProcessingEnvironment`, `RoundEnvironment`, `Elements`, `Types`, `Filer` (for writing generated files). Advantages over runtime reflection: zero runtime overhead (code is generated at compile time); errors caught at compile time; generated code is type-safe.

---

### 🟢 Simple Definition (Easy)

Lombok's `@Data` annotation: you write `@Data class User { String name; int age; }` and get `getName()`, `setName()`, `equals()`, `hashCode()`, `toString()` — for free. How? During compilation, Lombok's annotation processor reads your `@Data` annotation and generates that code before the compiler finishes. No reflection at runtime. No code in your `.java` file. The processor runs inside `javac` and generates the methods. You write 3 lines; the compiler produces a class with 30 lines of boilerplate — transparently.

---

### 🔵 Simple Definition (Elaborated)

Annotation processors receive control during `javac` compilation. They see your annotated classes (as `Element` objects) and can: (1) validate annotations (e.g., Dagger checks that all `@Inject` constructor dependencies are provided); (2) generate new `.java` files (e.g., MapStruct generates a `UserMapperImpl` class from a `@Mapper` interface); (3) generate resource files (e.g., Spring generates `spring.factories` metadata). The generated source files are compiled in a subsequent round — they're real Java code, visible to the IDE, testable, and type-safe. This is fundamentally different from runtime reflection: all the "magic" happens at build time, leaving zero overhead in production.

---

### 🔩 First Principles Explanation

**Writing a custom annotation processor:**

```
COMPILATION PIPELINE WITH APT:

  javac starts
      │
      ├── Parse: .java → AST
      │
      ├── ROUND 1: Call annotation processors
      │   │   Processor.process(annotations, roundEnv)
      │   │   Processor writes new .java files via Filer
      │   └── If new .java files generated → ROUND 2
      │
      ├── ROUND 2: Parse new .java files → Call processors again
      │   └── If more new files → ROUND 3, etc.
      │
      └── Compile all source (original + generated)

CUSTOM ANNOTATION PROCESSOR EXAMPLE:

  // 1. Define the annotation:
  @Retention(RetentionPolicy.SOURCE)  // only needed at compile time
  @Target(ElementType.TYPE)           // applies to classes
  public @interface Builder {}
  
  // 2. Write the processor:
  @SupportedAnnotationTypes("com.example.Builder")
  @SupportedSourceVersion(SourceVersion.RELEASE_17)
  public class BuilderProcessor extends AbstractProcessor {
      
      @Override
      public boolean process(Set<? extends TypeElement> annotations,
                             RoundEnvironment roundEnv) {
          
          for (Element element : roundEnv.getElementsAnnotatedWith(Builder.class)) {
              TypeElement classElement = (TypeElement) element;
              String className = classElement.getSimpleName().toString();
              String packageName = processingEnv.getElementUtils()
                  .getPackageOf(classElement).getQualifiedName().toString();
              
              // Generate builder class:
              try {
                  JavaFileObject file = processingEnv.getFiler()
                      .createSourceFile(packageName + "." + className + "Builder");
                  
                  try (PrintWriter writer = new PrintWriter(file.openWriter())) {
                      writer.println("package " + packageName + ";");
                      writer.println("public class " + className + "Builder {");
                      
                      // Write fields, setters, build() method based on classElement fields
                      for (Element enclosed : classElement.getEnclosedElements()) {
                          if (enclosed.getKind() == ElementKind.FIELD) {
                              String fieldName = enclosed.getSimpleName().toString();
                              String fieldType = enclosed.asType().toString();
                              
                              writer.println("  private " + fieldType + " " + fieldName + ";");
                              writer.println("  public " + className + "Builder " + fieldName +
                                  "(" + fieldType + " v) { this." + fieldName + "=v; return this; }");
                          }
                      }
                      
                      writer.println("  public " + className + " build() {");
                      writer.println("    " + className + " obj = new " + className + "();");
                      // set fields...
                      writer.println("    return obj;");
                      writer.println("  }");
                      writer.println("}");
                  }
              } catch (IOException e) {
                  processingEnv.getMessager().printMessage(
                      Diagnostic.Kind.ERROR, "Failed to generate builder: " + e.getMessage());
              }
          }
          return true;  // claim the annotation (don't pass to other processors)
      }
  }
  
  // 3. Register the processor:
  // META-INF/services/javax.annotation.processing.Processor:
  // com.example.BuilderProcessor
  
  // 4. Maven pom.xml: add to compiler plugin:
  // <annotationProcessors>
  //   <annotationProcessor>com.example.BuilderProcessor</annotationProcessor>
  // </annotationProcessors>

POPULAR APT-BASED LIBRARIES:

  LOMBOK (@Data, @Builder, @Slf4j):
  - Modifies the AST directly (uses internal javac APIs, not standard APT)
  - @Data: generates getters, setters, equals, hashCode, toString
  - @Builder: generates builder pattern
  - @Slf4j: adds private static final Logger log = LoggerFactory.getLogger(...)
  
  MAPSTRUCT (@Mapper):
  - Generates mapper implementation from interface:
    @Mapper interface UserMapper { UserDto toDto(User user); }
  - Generates: UserMapperImpl implements UserMapper with field-by-field copy code
  - Type-safe, null-safe, no reflection at runtime
  
  DAGGER 2 (@Component, @Module, @Inject):
  - Generates complete DI component code at compile time
  - DaggerAppComponent implements AppComponent
  - No runtime reflection → faster startup (vs Spring's reflection-based DI)
  
  HIBERNATE METAMODEL:
  - Generates: User_.class with SingularAttribute<User, String> name
  - Enables type-safe JPA criteria queries: criteriaBuilder.equal(root.get(User_.name), "Alice")

LOMBOK vs STANDARD APT:

  Lombok: modifies AST (compiler-internal API) → adds methods to existing class
  Standard APT: can only GENERATE new files (cannot modify existing classes)
  MapStruct/Dagger: standard APT → generates new .java files
  
  Lombok requires IDE plugin (IntelliJ Lombok plugin) to understand generated methods.
  Standard APT generates real .java files visible to IDE without plugins.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT APT:
- Boilerplate code written manually (getters, setters, builders, equals/hashCode)
- DI framework uses runtime reflection → slower startup, harder native image compilation
- Mapper implementations written by hand → error-prone, maintenance burden

WITH APT:
→ Generate boilerplate at build time. Zero runtime overhead. Type-safe generated code. Errors surfaced at compile time. GraalVM native image compatible (no runtime reflection needed).

---

### 🧠 Mental Model / Analogy

> A factory that pre-fabricates standard components before the building is assembled. Runtime reflection: a construction worker arrives at the site and hand-builds each component from scratch (slow, error-prone, runtime cost). Annotation processing: a factory reads the blueprints (annotations) at design time and ships pre-built components (generated code) to the site. The assembly (compilation + linking) happens before the building is opened to users. When the building opens (runtime), all components are already in place — zero assembly required.

"Factory reads blueprints" = annotation processor reads `@Data`, `@Mapper` annotations during `javac`
"Pre-built components shipped" = generated `.java` files written by the `Filer`
"Assembly at design time" = code generation during compilation, not runtime
"Building opens: components in place" = at runtime, generated classes are already compiled and available
"No assembly at runtime" = zero runtime reflection overhead

---

### ⚙️ How It Works (Mechanism)

```
APT EXECUTION MODEL:

  javac -processorpath processors.jar \
        -processor com.example.BuilderProcessor \
        src/com/example/User.java
  
  Round 1:
    Input: User.java (has @Builder)
    Processor: reads User's fields, writes UserBuilder.java to generated-sources/
    Output: UserBuilder.java
  
  Round 2:
    Input: UserBuilder.java (new file from Round 1)
    Processor: no @Builder on UserBuilder → process() returns false (not claiming)
    Output: no new files
  
  Final compilation: User.java + UserBuilder.java → User.class + UserBuilder.class

MAVEN CONFIGURATION:

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
        <path>
          <groupId>org.projectlombok</groupId>
          <artifactId>lombok</artifactId>
          <version>1.18.30</version>
        </path>
      </annotationProcessorPaths>
    </configuration>
  </plugin>
```

---

### 🔄 How It Connects (Mini-Map)

```
Boilerplate code generation needed without runtime overhead
        │
        ▼
Annotation Processing (APT) ◄──── (you are here)
(AbstractProcessor; compile-time code generation; Filer; rounds)
        │
        ├── Reflection: APT is the compile-time alternative to runtime reflection
        ├── Annotations: APT processes annotations; annotations trigger generation
        ├── Lombok: APT (+ AST manipulation) for getters/setters/builders
        └── MapStruct / Dagger: standard APT for mapper and DI code generation
```

---

### 💻 Code Example

```java
// MAPSTRUCT (@Mapper): processor generates implementation
@Mapper
public interface OrderMapper {
    OrderDto toDto(Order order);
    Order toEntity(OrderDto dto);
}

// APT generates at compile time (in target/generated-sources/):
// @Component
// public class OrderMapperImpl implements OrderMapper {
//     @Override
//     public OrderDto toDto(Order order) {
//         if (order == null) return null;
//         OrderDto dto = new OrderDto();
//         dto.setId(order.getId());
//         dto.setStatus(order.getStatus().name());
//         // ... all field mappings
//         return dto;
//     }
// }

// DAGGER 2 (@Component): processor generates DI component
@Component(modules = {AppModule.class, NetworkModule.class})
public interface AppComponent {
    OrderService orderService();
}
// Processor generates: DaggerAppComponent.java
// - No reflection; direct constructor calls; compile-time verified graph

// LOMBOK (@Builder): processor adds builder to compiled class
@Builder
@Data
public class CreateOrderRequest {
    private String customerId;
    private List<OrderItem> items;
    private BigDecimal total;
}

// USAGE: no manual code; builder available at compile time:
CreateOrderRequest request = CreateOrderRequest.builder()
    .customerId("CUST-001")
    .items(items)
    .total(new BigDecimal("99.99"))
    .build();
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Annotation processors modify existing source files | Standard APT can ONLY generate new files. It cannot modify existing `.java` files. Lombok appears to modify classes because it uses internal javac AST manipulation APIs (not standard APT) — this is why Lombok is controversial and requires an IDE plugin to understand the generated methods. |
| APT-generated code has no performance cost | The generation has compile-time cost (adds to build time), but zero runtime overhead. Generated code is plain Java — compiled to bytecode, JIT-compiled, and executed as efficiently as hand-written code. This is the key advantage over runtime reflection. |
| All Java annotation processors work with GraalVM native image | GraalVM native image requires all reflection/resource metadata to be declared ahead of time. APT-generated code that itself uses runtime reflection still needs native image configuration. Dagger (pure APT, no runtime reflection) works natively; Spring (historically reflection-based) required Spring AOT (Spring 6) for native image support. |

---

### 🔥 Pitfalls in Production

**Lombok + MapStruct processing order causing compilation errors:**

```xml
<!-- ANTI-PATTERN: wrong processor order in Maven -->
<annotationProcessorPaths>
    <path>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct-processor</artifactId>
    </path>
    <path>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </path>
</annotationProcessorPaths>

<!-- PROBLEM: MapStruct runs before Lombok generates getters/setters
     MapStruct sees: User class with no getters → generates empty/broken mapper
     Error: "No read accessor found for property 'name' in User" -->

<!-- FIX: Lombok MUST run before MapStruct to generate getters first -->
<annotationProcessorPaths>
    <path>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>   <!-- FIRST: generate getters/setters -->
    </path>
    <path>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct-processor</artifactId>  <!-- SECOND: use getters -->
    </path>
</annotationProcessorPaths>
<!-- Rule: Lombok must always precede MapStruct in annotationProcessorPaths -->
```

---

### 🔗 Related Keywords

- `Reflection` — runtime alternative: APT generates code that replaces runtime reflection use cases
- `Lombok` — uses APT (+ internal AST manipulation) for `@Data`, `@Builder`, `@Slf4j`
- `MapStruct` — standard APT for type-safe mapper code generation from `@Mapper` interfaces
- `Dagger 2` — compile-time DI framework using APT; no runtime reflection
- `GraalVM Native Image` — APT-generated code is native-image-friendly (no runtime reflection)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Compile-time code generation from        │
│              │ annotations. AbstractProcessor generates │
│              │ .java files via Filer. Zero runtime cost.│
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Lombok: @Data, @Builder, @Slf4j          │
│              │ MapStruct: @Mapper → impl class          │
│              │ Dagger 2: @Component → DI factory        │
│              │ Hibernate: @Entity → type-safe Criteria  │
├──────────────┼───────────────────────────────────────────┤
│ ORDER MATTERS│ Lombok before MapStruct in processor     │
│              │ order (getters must exist before MapStruct│
│              │ reads them)                              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pre-fab factory: reads blueprints at    │
│              │  design time, ships ready components.   │
│              │  Zero assembly at runtime."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reflection → Lombok → MapStruct →         │
│              │ Dagger 2 → GraalVM AOT                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Lombok uses internal `javac` AST APIs (`com.sun.tools.javac.*`) to modify the AST directly — adding methods to existing classes. This is NOT standard APT (which can only create new files). This is why Lombok breaks with new JDK versions and requires an IDE plugin. What are the risks of depending on a library that uses internal JDK APIs vs. one that uses only standard APIs? How does the Lombok team manage compatibility across JDK versions?

**Q2.** Spring 6 introduced AOT (Ahead-of-Time) processing as part of its GraalVM native image support. Spring AOT generates bean factory code at build time (replacing runtime reflection). Compare Spring AOT to Dagger 2: both eliminate runtime reflection for DI. What are the architectural differences — can you add new beans to a Spring AOT application at runtime? Can you with Dagger 2? What flexibility do you give up with each approach?
