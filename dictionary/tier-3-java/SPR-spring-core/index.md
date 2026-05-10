---
layout: default
title: "Spring Core"
parent: "Technical Dictionary"
nav_order: 13
has_children: true
permalink: /spring/
---

# Spring Core

Spring IoC/DI, AOP, MVC, transactions, data access, reactive programming, Spring Boot, Spring Security, Spring Batch, Spring Cloud, and creator-level framework design theory.

> **Note:** SPR-005 (Spring in Production) and SPR-057 (Spring Cloud) provide entry-level and working-level views respectively of Spring Cloud integration.

**Keywords:** SPR-001–SPR-101 (101 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| SPR-001 | What Is Spring - History and Philosophy | ★☆☆ |
| SPR-002 | The Spring Ecosystem Map | ★☆☆ |
| SPR-003 | Why Spring Boot Changed Java Development | ★☆☆ |
| SPR-004 | Spring vs Jakarta EE vs Micronaut vs Quarkus | ★☆☆ |
| SPR-005 | Spring in Production - What to Expect | ★☆☆ |
| SPR-006 | Spring Batch | ★★★ |
| SPR-007 | Spring Batch Job  Step  Tasklet | ★★★ |
| SPR-008 | Spring Batch ItemReader  ItemProcessor  ItemWriter | ★★★ |
| SPR-009 | Spring Batch Chunk Processing | ★★★ |
| SPR-010 | Spring Cloud Overview | ★★★ |
| SPR-011 | Spring Cloud Config | ★★★ |
| SPR-012 | Spring Cloud Gateway | ★★★ |
| SPR-013 | Spring Cloud Service Discovery (Eureka) | ★★★ |
| SPR-014 | Spring Cloud Load Balancer | ★★★ |
| SPR-015 | Spring Cloud Circuit Breaker | ★★★ |
| SPR-016 | Micronaut Framework | ★★★ |
| SPR-017 | Micronaut vs Spring Boot | ★★★ |
| SPR-018 | Quarkus Framework | ★★★ |
| SPR-019 | IoC (Inversion of Control) | ★☆☆ |
| SPR-020 | DI (Dependency Injection) | ★☆☆ |
| SPR-021 | ApplicationContext | ★★☆ |
| SPR-022 | BeanFactory | ★★☆ |
| SPR-023 | Bean | ★☆☆ |
| SPR-024 | Bean Lifecycle | ★★☆ |
| SPR-025 | Bean Scope | ★★☆ |
| SPR-026 | BeanPostProcessor | ★★★ |
| SPR-027 | BeanFactoryPostProcessor | ★★★ |
| SPR-028 | @Autowired | ★★☆ |
| SPR-029 | @Qualifier  @Primary | ★★☆ |
| SPR-030 | @Configuration  @Bean | ★★☆ |
| SPR-031 | Circular Dependency | ★★★ |
| SPR-032 | CGLIB Proxy | ★★★ |
| SPR-033 | JDK Dynamic Proxy | ★★★ |
| SPR-034 | AOP (Aspect-Oriented Programming) | ★★☆ |
| SPR-035 | Aspect | ★★☆ |
| SPR-036 | Advice | ★★☆ |
| SPR-037 | Pointcut | ★★☆ |
| SPR-038 | JoinPoint | ★★☆ |
| SPR-039 | Weaving | ★★★ |
| SPR-040 | DispatcherServlet | ★★☆ |
| SPR-041 | HandlerMapping | ★★★ |
| SPR-042 | Filter vs Interceptor | ★★☆ |
| SPR-043 | @Transactional | ★★☆ |
| SPR-044 | Transaction Propagation | ★★★ |
| SPR-045 | Transaction Isolation Levels | ★★★ |
| SPR-046 | N+1 Problem | ★★★ |
| SPR-047 | Lazy vs Eager Loading | ★★☆ |
| SPR-048 | HikariCP | ★★☆ |
| SPR-049 | Auto-Configuration | ★★★ |
| SPR-050 | Spring Boot Actuator | ★★☆ |
| SPR-051 | Spring Boot Startup Lifecycle | ★★★ |
| SPR-052 | WebFlux  Reactive | ★★★ |
| SPR-053 | Mono  Flux | ★★★ |
| SPR-054 | Backpressure (Spring) | ★★★ |
| SPR-055 | Spring Security | ★★★ |
| SPR-056 | Spring Data JPA | ★★☆ |
| SPR-057 | Spring Cloud | ★★★ |
| SPR-058 | Spring Boot Testing | ★★☆ |
| SPR-059 | Spring Architecture at Scale | ★★★ |
| SPR-060 | Spring Migration Strategy (MVC to WebFlux) | ★★★ |
| SPR-061 | Spring Boot Configuration Strategy | ★★★ |
| SPR-062 | Spring Security Architecture Design | ★★★ |
| SPR-063 | Microservice Decomposition with Spring Cloud | ★★★ |
| SPR-064 | Spring Framework Internals Deep Dive | ★★★ |
| SPR-065 | Spring Reactive Model (Project Reactor Internals) | ★★★ |
| SPR-066 | Spring Native and GraalVM Integration | ★★★ |
| SPR-067 | Spring Specification and Extension Points | ★★★ |
| SPR-068 | IoC-First Thinking | ★★★ |
| SPR-069 | Spring Configuration Trade-off Framing | ★★★ |
| SPR-070 | Framework Selection Mental Model | ★★★ |
| SPR-071 | @Component / @Service / @Repository | ★☆☆ |
| SPR-072 | @SpringBootApplication | ★☆☆ |
| SPR-073 | @RestController / @Controller | ★★☆ |
| SPR-074 | @RequestMapping / @GetMapping / @PostMapping | ★★☆ |
| SPR-075 | @RequestBody / @ResponseBody | ★★☆ |
| SPR-076 | @PathVariable / @RequestParam | ★★☆ |
| SPR-077 | Spring Profiles (@Profile, application.yml) | ★★☆ |
| SPR-078 | Spring Validation (@Valid, @NotNull) | ★★☆ |
| SPR-079 | Exception Handling (@ExceptionHandler, @ControllerAdvice) | ★★☆ |
| SPR-080 | Spring Cache Abstraction (@Cacheable) | ★★☆ |
| SPR-081 | Spring Events (ApplicationEvent, @EventListener) | ★★☆ |
| SPR-082 | Conditional Beans (@ConditionalOnProperty) | ★★☆ |
| SPR-083 | ResponseEntity and HTTP Status Handling | ★★☆ |
| SPR-084 | Spring Boot DevTools | ★☆☆ |
| SPR-085 | Spring Retry | ★★☆ |
| SPR-086 | MockMvc | ★★☆ |
| SPR-087 | @MockBean / @SpyBean | ★★☆ |
| SPR-088 | Spring Context Refresh (AbstractApplicationContext) | ★★★ |
| SPR-089 | Bean Definition Registry | ★★★ |
| SPR-090 | Spring Boot AOT Compilation (Spring 6) | ★★★ |
| SPR-091 | Spring + Virtual Threads (Spring 6.1) | ★★★ |
| SPR-092 | Spring Security OAuth2 Resource Server | ★★★ |
| SPR-093 | Spring Data REST | ★★★ |
| SPR-094 | Spring Native Image Support | ★★★ |
| SPR-095 | Spring Framework Design Rationale | ★★★ |
| SPR-096 | Project Reactor Design (Reactive Streams Spec) | ★★★ |
| SPR-097 | Spring Boot Auto-Configuration Algorithm | ★★★ |
| SPR-098 | Spring Test Context Management | ★★★ |
| SPR-099 | Spring Interview Preparation Guide | ★☆☆ |
| SPR-100 | Spring Modulith (Spring 6.1+) | ★★★ |
| SPR-101 | Spring AOT and GraalVM Native Image | ★★★ |
