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

> **Note:** SPR-005 (Spring in Production) and SPR-076 (Spring Cloud) provide entry-level and working-level views respectively of Spring Cloud integration.

**Keywords:** SPR-001–SPR-101 (101 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| SPR-001 | What Is Spring - History and Philosophy | ★☆☆ |
| SPR-002 | The Spring Ecosystem Map | ★☆☆ |
| SPR-003 | Why Spring Boot Changed Java Development | ★☆☆ |
| SPR-004 | Spring vs Jakarta EE vs Micronaut vs Quarkus | ★☆☆ |
| SPR-005 | Spring in Production - What to Expect | ★☆☆ |
| SPR-047 | IoC (Inversion of Control) | ★☆☆ |
| SPR-048 | DI (Dependency Injection) | ★☆☆ |
| SPR-049 | Bean | ★☆☆ |
| SPR-050 | @Component / @Service / @Repository | ★☆☆ |
| SPR-051 | @SpringBootApplication | ★☆☆ |
| SPR-052 | Spring Boot DevTools | ★☆☆ |
| SPR-053 | Spring Interview Preparation Guide | ★☆☆ |
| SPR-054 | ApplicationContext | ★★☆ |
| SPR-055 | BeanFactory | ★★☆ |
| SPR-056 | Bean Lifecycle | ★★☆ |
| SPR-057 | Bean Scope | ★★☆ |
| SPR-058 | @Autowired | ★★☆ |
| SPR-059 | @Qualifier  @Primary | ★★☆ |
| SPR-006 | @Configuration  @Bean | ★★☆ |
| SPR-007 | AOP (Aspect-Oriented Programming) | ★★☆ |
| SPR-013 | Aspect | ★★☆ |
| SPR-014 | Advice | ★★☆ |
| SPR-008 | Pointcut | ★★☆ |
| SPR-015 | JoinPoint | ★★☆ |
| SPR-016 | DispatcherServlet | ★★☆ |
| SPR-060 | Filter vs Interceptor | ★★☆ |
| SPR-061 | @Transactional | ★★☆ |
| SPR-017 | Lazy vs Eager Loading | ★★☆ |
| SPR-018 | HikariCP | ★★☆ |
| SPR-019 | Spring Boot Actuator | ★★☆ |
| SPR-062 | Spring Data JPA | ★★☆ |
| SPR-063 | Spring Boot Testing | ★★☆ |
| SPR-064 | @RestController / @Controller | ★★☆ |
| SPR-020 | @RequestMapping / @GetMapping / @PostMapping | ★★☆ |
| SPR-021 | @RequestBody / @ResponseBody | ★★☆ |
| SPR-022 | @PathVariable / @RequestParam | ★★☆ |
| SPR-023 | Spring Profiles (@Profile, application.yml) | ★★☆ |
| SPR-024 | Spring Validation (@Valid, @NotNull) | ★★☆ |
| SPR-065 | Exception Handling (@ExceptionHandler, @ControllerAdvice) | ★★☆ |
| SPR-025 | Spring Cache Abstraction (@Cacheable) | ★★☆ |
| SPR-066 | Spring Events (ApplicationEvent, @EventListener) | ★★☆ |
| SPR-026 | Conditional Beans (@ConditionalOnProperty) | ★★☆ |
| SPR-027 | ResponseEntity and HTTP Status Handling | ★★☆ |
| SPR-067 | Spring Retry | ★★☆ |
| SPR-068 | MockMvc | ★★☆ |
| SPR-069 | @MockBean / @SpyBean | ★★☆ |
| SPR-028 | Spring Batch | ★★★ |
| SPR-029 | Spring Batch Job  Step  Tasklet | ★★★ |
| SPR-070 | Spring Batch ItemReader  ItemProcessor  ItemWriter | ★★★ |
| SPR-030 | Spring Batch Chunk Processing | ★★★ |
| SPR-071 | Spring Cloud Overview | ★★★ |
| SPR-072 | Spring Cloud Config | ★★★ |
| SPR-073 | Spring Cloud Gateway | ★★★ |
| SPR-074 | Spring Cloud Service Discovery (Eureka) | ★★★ |
| SPR-075 | Spring Cloud Load Balancer | ★★★ |
| SPR-031 | Spring Cloud Circuit Breaker | ★★★ |
| SPR-076 | Micronaut Framework | ★★★ |
| SPR-032 | Micronaut vs Spring Boot | ★★★ |
| SPR-077 | Quarkus Framework | ★★★ |
| SPR-060 | BeanPostProcessor | ★★★ |
| SPR-079 | BeanFactoryPostProcessor | ★★★ |
| SPR-080 | Circular Dependency | ★★★ |
| SPR-081 | CGLIB Proxy | ★★★ |
| SPR-082 | JDK Dynamic Proxy | ★★★ |
| SPR-083 | Weaving | ★★★ |
| SPR-084 | HandlerMapping | ★★★ |
| SPR-085 | Transaction Propagation | ★★★ |
| SPR-086 | Transaction Isolation Levels | ★★★ |
| SPR-087 | N+1 Problem | ★★★ |
| SPR-088 | Auto-Configuration | ★★★ |
| SPR-009 | Spring Boot Startup Lifecycle | ★★★ |
| SPR-010 | WebFlux  Reactive | ★★★ |
| SPR-033 | Mono  Flux | ★★★ |
| SPR-034 | Backpressure (Spring) | ★★★ |
| SPR-035 | Spring Security | ★★★ |
| SPR-036 | Spring Cloud | ★★★ |
| SPR-037 | Spring Architecture at Scale | ★★★ |
| SPR-038 | Spring Migration Strategy (MVC to WebFlux) | ★★★ |
| SPR-039 | Spring Boot Configuration Strategy | ★★★ |
| SPR-040 | Spring Security Architecture Design | ★★★ |
| SPR-041 | Microservice Decomposition with Spring Cloud | ★★★ |
| SPR-042 | Spring Framework Internals Deep Dive | ★★★ |
| SPR-043 | Spring Reactive Model (Project Reactor Internals) | ★★★ |
| SPR-011 | Spring Native and GraalVM Integration | ★★★ |
| SPR-044 | Spring Specification and Extension Points | ★★★ |
| SPR-045 | IoC-First Thinking | ★★★ |
| SPR-046 | Spring Configuration Trade-off Framing | ★★★ |
| SPR-089 | Framework Selection Mental Model | ★★★ |
| SPR-090 | Spring Context Refresh (AbstractApplicationContext) | ★★★ |
| SPR-091 | Bean Definition Registry | ★★★ |
| SPR-092 | Spring Boot AOT Compilation (Spring 6) | ★★★ |
| SPR-093 | Spring + Virtual Threads (Spring 6.1) | ★★★ |
| SPR-094 | Spring Security OAuth2 Resource Server | ★★★ |
| SPR-095 | Spring Data REST | ★★★ |
| SPR-096 | Spring Native Image Support | ★★★ |
| SPR-097 | Spring Framework Design Rationale | ★★★ |
| SPR-098 | Project Reactor Design (Reactive Streams Spec) | ★★★ |
| SPR-099 | Spring Boot Auto-Configuration Algorithm | ★★★ |
| SPR-012 | Spring Test Context Management | ★★★ |
| SPR-100 | Spring Modulith (Spring 6.1+) | ★★★ |
| SPR-101 | Spring AOT and GraalVM Native Image | ★★★ |
