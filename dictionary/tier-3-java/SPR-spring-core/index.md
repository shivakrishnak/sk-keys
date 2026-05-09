---
layout: default
title: "Spring Core"
parent: "Technical Dictionary"
nav_order: 10
has_children: true
permalink: /spring/
---

# Spring Core

Spring IoC/DI, AOP, MVC, transactions, data access, reactive programming, Spring Boot, Spring Security, Spring Batch, Spring Cloud, and creator-level framework design theory.

**Keywords:** SPR-001–SPR-082 (82 terms · 53 original + 29 gap-fill)

> ⚠️ **Malformed IDs fixed:** Original entries `2120–2132` → `SPR-001–SPR-013`. Original entries `371–410` → `SPR-014–SPR-053`. All now use `SPR-NNN` format.
> ⚠️ **Note:** `SPR-005` (Spring Cloud Overview) and `SPR-052` (Spring Cloud) overlap - `SPR-005` is the Spring Cloud sub-system overview; `SPR-052` covers the broader Cloud integration entry.

| ID      | Keyword                                               | Difficulty |
|---------|-------------------------------------------------------|------------|
| SPR-001 | Spring Batch                                          | ★★★        |
| SPR-002 | Spring Batch Job / Step / Tasklet                     | ★★★        |
| SPR-003 | Spring Batch ItemReader / ItemProcessor / ItemWriter  | ★★★        |
| SPR-004 | Spring Batch Chunk Processing                         | ★★★        |
| SPR-005 | Spring Cloud Overview                                 | ★★★        |
| SPR-006 | Spring Cloud Config                                   | ★★★        |
| SPR-007 | Spring Cloud Gateway                                  | ★★★        |
| SPR-008 | Spring Cloud Service Discovery (Eureka)               | ★★★        |
| SPR-009 | Spring Cloud Load Balancer                            | ★★★        |
| SPR-010 | Spring Cloud Circuit Breaker                          | ★★★        |
| SPR-011 | Micronaut Framework                                   | ★★★        |
| SPR-012 | Micronaut vs Spring Boot                              | ★★★        |
| SPR-013 | Quarkus Framework                                     | ★★★        |
| SPR-014 | IoC (Inversion of Control)                            | ★☆☆        |
| SPR-015 | DI (Dependency Injection)                             | ★☆☆        |
| SPR-016 | ApplicationContext                                    | ★★☆        |
| SPR-017 | BeanFactory                                           | ★★☆        |
| SPR-018 | Bean                                                  | ★☆☆        |
| SPR-019 | Bean Lifecycle                                        | ★★☆        |
| SPR-020 | Bean Scope                                            | ★★☆        |
| SPR-021 | BeanPostProcessor                                     | ★★★        |
| SPR-022 | BeanFactoryPostProcessor                              | ★★★        |
| SPR-023 | @Autowired                                            | ★★☆        |
| SPR-024 | @Qualifier / @Primary                                 | ★★☆        |
| SPR-025 | @Configuration / @Bean                                | ★★☆        |
| SPR-026 | Circular Dependency                                   | ★★★        |
| SPR-027 | CGLIB Proxy                                           | ★★★        |
| SPR-028 | JDK Dynamic Proxy                                     | ★★★        |
| SPR-029 | AOP (Aspect-Oriented Programming)                     | ★★☆        |
| SPR-030 | Aspect                                                | ★★☆        |
| SPR-031 | Advice                                                | ★★☆        |
| SPR-032 | Pointcut                                              | ★★☆        |
| SPR-033 | JoinPoint                                             | ★★☆        |
| SPR-034 | Weaving                                               | ★★★        |
| SPR-035 | DispatcherServlet                                     | ★★☆        |
| SPR-036 | HandlerMapping                                        | ★★★        |
| SPR-037 | Filter vs Interceptor                                 | ★★☆        |
| SPR-038 | @Transactional                                        | ★★☆        |
| SPR-039 | Transaction Propagation                               | ★★★        |
| SPR-040 | Transaction Isolation Levels                          | ★★★        |
| SPR-041 | N+1 Problem                                           | ★★★        |
| SPR-042 | Lazy vs Eager Loading                                 | ★★☆        |
| SPR-043 | HikariCP                                              | ★★☆        |
| SPR-044 | Auto-Configuration                                    | ★★★        |
| SPR-045 | Spring Boot Actuator                                  | ★★☆        |
| SPR-046 | Spring Boot Startup Lifecycle                         | ★★★        |
| SPR-047 | WebFlux / Reactive                                    | ★★★        |
| SPR-048 | Mono / Flux                                           | ★★★        |
| SPR-049 | Backpressure (Spring)                                 | ★★★        |
| SPR-050 | Spring Security                                       | ★★★        |
| SPR-051 | Spring Data JPA                                       | ★★☆        |
| SPR-052 | Spring Cloud                                          | ★★★        |
| SPR-053 | Spring Boot Testing                                   | ★★☆        |
| SPR-054 | What is Spring Framework                              | ★☆☆        |
| SPR-055 | Spring Boot vs Spring Framework                       | ★☆☆        |
| SPR-056 | @Component / @Service / @Repository                  | ★☆☆        |
| SPR-057 | @SpringBootApplication                                | ★☆☆        |
| SPR-058 | @RestController / @Controller                         | ★★☆        |
| SPR-059 | @RequestMapping / @GetMapping / @PostMapping          | ★★☆        |
| SPR-060 | @RequestBody / @ResponseBody                          | ★★☆        |
| SPR-061 | @PathVariable / @RequestParam                         | ★★☆        |
| SPR-062 | Spring Profiles (@Profile, application.yml)           | ★★☆        |
| SPR-063 | Spring Validation (@Valid, @NotNull)                  | ★★☆        |
| SPR-064 | Exception Handling (@ExceptionHandler, @ControllerAdvice) | ★★☆    |
| SPR-065 | Spring Cache Abstraction (@Cacheable)                 | ★★☆        |
| SPR-066 | Spring Events (ApplicationEvent, @EventListener)      | ★★☆        |
| SPR-067 | Conditional Beans (@ConditionalOnProperty)            | ★★☆        |
| SPR-068 | ResponseEntity and HTTP Status Handling               | ★★☆        |
| SPR-069 | Spring Boot DevTools                                  | ★★☆        |
| SPR-070 | Spring Retry                                          | ★★☆        |
| SPR-071 | Spring Context Refresh (AbstractApplicationContext)   | ★★★        |
| SPR-072 | Bean Definition Registry                              | ★★★        |
| SPR-073 | Spring Boot AOT Compilation (Spring 6)                | ★★★        |
| SPR-074 | Spring + Virtual Threads (Spring 6.1)                 | ★★★        |
| SPR-075 | Spring Security OAuth2 Resource Server                | ★★★        |
| SPR-076 | Spring Data REST                                      | ★★★        |
| SPR-077 | Spring Native Image Support                           | ★★★        |
| SPR-078 | Spring Framework Design Rationale (Expert One-on-One) | 🔬          |
| SPR-079 | Project Reactor Design (Reactive Streams Spec)        | 🔬          |
| SPR-080 | Spring Boot Auto-Configuration Algorithm              | 🔬          |
| SPR-081 | Spring Annotation Processing Internals                | 🔬          |
| SPR-082 | Spring TestContext Framework Design                   | 🔬          |
