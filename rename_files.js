
/**
 * Rename and move all existing keyword files to new IDs per master list.
 * Uses fs.renameSync (in-process, no git tracking needed for untracked files).
 */
const fs = require('fs');
const path = require('path');
const DOCS = 'C:/ASK/MyWorkspace/sk-keys/docs';

function mv(srcDir, srcFile, dstDir, dstFile) {
  const src = path.join(DOCS, srcDir, srcFile);
  const dst = path.join(DOCS, dstDir, dstFile);
  if (!fs.existsSync(src)) { console.warn(`  SKIP (not found): ${srcDir}/${srcFile}`); return; }
  const dir = path.dirname(dst);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.renameSync(src, dst);
  if (srcDir === dstDir && srcFile === dstFile) return;
  console.log(`  ✓ ${srcDir}/${srcFile}  →  ${dstDir}/${dstFile}`);
}

console.log('\n── Java JVM (001–026 → 261–286) ─────────────────────────');
const javaMap = [
  ['001 — JVM (Java Virtual Machine).md',                       '261 — JVM (Java Virtual Machine).md'],
  ['002 — JRE (Java Runtime Environment).md',                   '262 — JRE (Java Runtime Environment).md'],
  ['003 —JDK (Java Development Kit).md',                        '263 — JDK (Java Development Kit).md'],
  ['004 —Bytecode.md',                                           '264 — Bytecode.md'],
  ['005 — Class Loader.md',                                      '265 — Class Loader.md'],
  ['006 — Stack Memory.md',                                      '266 — Stack Memory.md'],
  ['007 — Heap Memory.md',                                       '267 — Heap Memory.md'],
  ['008 — Metaspace.md',                                         '268 — Metaspace.md'],
  ['009 — Stack Frame.md',                                       '269 — Stack Frame.md'],
  ['010 — Operand Stack.md',                                     '270 — Operand Stack.md'],
  ['011 — Local Variable Table.md',                              '271 — Local Variable Table.md'],
  ['012 — Object Header.md',                                     '272 — Object Header.md'],
  ['013 — Escape Analysis.md',                                   '273 — Escape Analysis.md'],
  ['014 — Memory Barrier.md',                                    '274 — Memory Barrier.md'],
  ['015 — Happens-Before.md',                                    '275 — Happens-Before.md'],
  ['016 — GC Roots.md',                                          '276 — GC Roots.md'],
  ['017 — Reference Types (Strong, Soft, Weak, Phantom).md',     '277 — Reference Types (Strong, Soft, Weak, Phantom).md'],
  ['018 — Young Generation.md',                                  '278 — Young Generation.md'],
  ['019 — Eden Space.md',                                        '279 — Eden Space.md'],
  ['020 — Survivor Space.md',                                    '280 — Survivor Space.md'],
  ['021 — Minor GC.md',                                          '282 — Minor GC.md'],
  ['022 — Major GC.md',                                          '283 — Major GC.md'],
  ['023 — Full GC.md',                                           '284 — Full GC.md'],
  ['024 — Stop-The-World (STW).md',                              '285 — Stop-The-World (STW).md'],
  ['025 — Serial GC.md',                                         '286 — Serial GC.md'],
  ['026 — Parallel GC.md',                                       '287 — Parallel GC.md'],
];
for (const [s, d] of javaMap) mv('Java', s, 'Java', d);

console.log('\n── Java Language (051–065 → 312–324) ────────────────────');
const jlMap = [
  ['051 — Autoboxing-Unboxing.md',             '312 — Autoboxing-Unboxing.md'],
  ['052 — Integer Cache.md',                   '313 — Integer Cache.md'],
  ['053 — Generics.md',                        '314 — Generics.md'],
  ['054 — Type Erasure.md',                    '315 — Type Erasure.md'],
  ['055 — Bounded Wildcards.md',               '316 — Bounded Wildcards.md'],
  ['056 — Covariance-Contravariance.md',       '317 — Covariance-Contravariance.md'],
  ['057 — Varargs.md',                         '318 — Varargs.md'],
  ['058 — Reflection.md',                      '319 — Reflection.md'],
  ['059 — Annotation Processing (APT).md',     '320 — Annotation Processing (APT).md'],
  ['060 — Serialization-Deserialization.md',   '321 — Serialization-Deserialization.md'],
  ['061 — SerialVersionUID.md',                '321b — SerialVersionUID.md'],
  ['062 — Records (Java 16+).md',              '322 — Records (Java 16+).md'],
  ['063 — Sealed Classes (Java 17+).md',       '323 — Sealed Classes (Java 17+).md'],
  ['064 — Pattern Matching (Java 16+).md',     '324 — Pattern Matching (Java 21+).md'],
  ['065 — Text Blocks (Java 15+).md',          '325b — Text Blocks (Java 15+).md'],
];
for (const [s, d] of jlMap) mv('Java Language', s, 'Java Language', d);

console.log('\n── Java Concurrency (066–102 → 331–370) ─────────────────');
const jcMap = [
  ['066 — Thread.md',                          '331 — Thread (Java).md'],
  ['067 — Runnable vs Callable.md',            '332 — Runnable vs Callable.md'],
  ['068 — Thread Lifecycle.md',                '336 — Thread Lifecycle.md'],
  ['069 — synchronized.md',                    '338 — synchronized.md'],
  ['070 — volatile.md',                        '339 — volatile.md'],
  ['071 — Deadlock.md',                        '368 — Deadlock Detection (Java).md'],
  ['072 — Race Condition.md',                  '346 — Race Condition.md'],
  ['073 — ThreadLocal.md',                     '344 — ThreadLocal.md'],
  ['074 — ExecutorService.md',                 '350 — ExecutorService.md'],
  ['075 — Future and CompletableFuture.md',    '335 — Future and CompletableFuture.md'],
  ['076 — ReentrantLock.md',                   '341 — ReentrantLock.md'],
  ['077 — Atomic Variables.md',                '363 — Atomic Variables.md'],
  ['078 — CountDownLatch.md',                  '357 — CountDownLatch.md'],
  ['079 — CyclicBarrier.md',                   '358 — CyclicBarrier.md'],
  ['080 — Semaphore.md',                       '356 — Semaphore (Java).md'],
  ['081 — BlockingQueue.md',                   '360 — BlockingQueue.md'],
  ['082 — ConcurrentHashMap.md',               '361 — ConcurrentHashMap.md'],
  ['083 — ReadWriteLock.md',                   '342 — ReadWriteLock.md'],
  ['084 — ForkJoinPool.md',                    '352 — ForkJoinPool.md'],
  ['085 — Virtual Threads.md',                 '353 — Virtual Threads (Project Loom).md'],
  ['086 — Producer-Consumer Pattern.md',       '792b — Producer-Consumer Pattern.md'],
  ['087 — StampedLock.md',                     '343 — StampedLock.md'],
  ['088 — Livelock.md',                        '119b — Livelock (OS).md'],
  ['089 — Starvation.md',                      '120b — Starvation (OS).md'],
  ['090 — Thread Interruption.md',             '337b — Thread Interruption.md'],
  ['091 — CopyOnWriteArrayList.md',            '362 — CopyOnWriteArrayList.md'],
  ['092 — Parallel Streams.md',                '327b — Parallel Streams.md'],
  ['093 — ScheduledExecutorService.md',        '349b — ScheduledExecutorService.md'],
  ['094 — Structured Concurrency.md',          '365 — Structured Concurrency.md'],
  ['095 — Java Memory Model.md',               '345 — Java Memory Model (JMM).md'],
  ['096 — Phaser.md',                          '359 — Phaser.md'],
  ['097 — Exchanger.md',                       '369b — Exchanger.md'],
  ['098 — ConcurrentLinkedQueue.md',           '360b — ConcurrentLinkedQueue.md'],
  ['099 — DelayQueue.md',                      '360c — DelayQueue.md'],
  ['100 — ThreadPoolExecutor.md',              '351 — ThreadPoolExecutor.md'],
  ['101 — Lock-Free Data Structures.md',       '347b — Lock-Free Data Structures.md'],
  ['102 — Thread Safety Patterns.md',          '370b — Thread Safety Patterns.md'],
];
for (const [s, d] of jcMap) mv('Java Concurrency', s, 'Java Concurrency', d);

console.log('\n── Spring (103–138 → 371–406) ────────────────────────────');
const springMap = [
  ['103 — IoC (Inversion of Control).md',          '371 — IoC (Inversion of Control).md'],
  ['104 — DI (Dependency Injection).md',            '372 — DI (Dependency Injection).md'],
  ['105 — ApplicationContext.md',                   '373 — ApplicationContext.md'],
  ['106 — BeanFactory.md',                          '374 — BeanFactory.md'],
  ['107 — Bean.md',                                 '375 — Bean.md'],
  ['108 — Bean Lifecycle.md',                       '376 — Bean Lifecycle.md'],
  ['109 — Bean Scope.md',                           '377 — Bean Scope.md'],
  ['110 — BeanPostProcessor.md',                    '378 — BeanPostProcessor.md'],
  ['111 — BeanFactoryPostProcessor.md',             '379 — BeanFactoryPostProcessor.md'],
  ['112 — @Autowired.md',                           '380 — @Autowired.md'],
  ['113 — @Qualifier @Primary.md',                  '381 — @Qualifier @Primary.md'],
  ['114 — @Configuration @Bean.md',                 '382 — @Configuration @Bean.md'],
  ['115 — Circular Dependency.md',                  '383 — Circular Dependency.md'],
  ['116 — CGLIB Proxy.md',                          '384 — CGLIB Proxy.md'],
  ['117 — JDK Dynamic Proxy.md',                    '385 — JDK Dynamic Proxy.md'],
  ['118 — AOP (Aspect-Oriented Programming).md',    '386 — AOP (Aspect-Oriented Programming).md'],
  ['119 — Aspect.md',                               '387 — Aspect.md'],
  ['120 — Advice.md',                               '388 — Advice.md'],
  ['121 — Pointcut.md',                             '389 — Pointcut.md'],
  ['122 — JoinPoint.md',                            '390 — JoinPoint.md'],
  ['123 — Weaving.md',                              '391 — Weaving.md'],
  ['124 — DispatcherServlet.md',                    '392 — DispatcherServlet.md'],
  ['125 — HandlerMapping.md',                       '393 — HandlerMapping.md'],
  ['126 — Filter vs Interceptor.md',                '394 — Filter vs Interceptor.md'],
  ['127 — @Transactional.md',                       '395 — @Transactional.md'],
  ['128 — Transaction Propagation.md',              '396 — Transaction Propagation.md'],
  ['129 — Transaction Isolation Levels.md',         '397 — Transaction Isolation Levels.md'],
  ['130 — N+1 Problem.md',                          '398 — N+1 Problem.md'],
  ['131 — Lazy vs Eager Loading.md',                '399 — Lazy vs Eager Loading.md'],
  ['132 — HikariCP.md',                             '400 — HikariCP.md'],
  ['133 — Auto-Configuration.md',                   '401 — Auto-Configuration.md'],
  ['134 — Spring Boot Actuator.md',                 '402 — Spring Boot Actuator.md'],
  ['135 — Spring Boot Startup Lifecycle.md',        '403 — Spring Boot Startup Lifecycle.md'],
  ['136 — WebFlux Reactive.md',                     '404 — WebFlux Reactive.md'],
  ['137 — Mono Flux.md',                            '405 — Mono Flux.md'],
  ['138 — Backpressure.md',                         '406 — Backpressure.md'],
];
for (const [s, d] of springMap) mv('Spring', s, 'Spring', d);

console.log('\n── Clean Code (424–433) → Software Architecture + Code Quality ──');
const ccMap = [
  // [srcFolder, srcFile, dstFolder, dstFile]
  ['Clean Code', '424 — Cohesion.md',                         'Software Architecture', '763 — Cohesion.md'],
  ['Clean Code', '425 — Coupling.md',                         'Software Architecture', '764 — Coupling.md'],
  ['Clean Code', '426 — Abstraction.md',                      'CS Fundamentals',       '016 — Abstraction.md'],
  ['Clean Code', '427 — Encapsulation.md',                    'CS Fundamentals',       '017 — Encapsulation.md'],
  ['Clean Code', '428 — Polymorphism.md',                     'CS Fundamentals',       '018 — Polymorphism.md'],
  ['Clean Code', '429 — Inheritance.md',                      'CS Fundamentals',       '019 — Inheritance.md'],
  ['Clean Code', '430 — Command-Query Separation (CQS).md',   'Software Architecture', '762 — Command-Query Separation (CQS).md'],
  ['Clean Code', '431 — Feature Flags.md',                    'Microservices',         '671 — Feature Flags.md'],
  ['Clean Code', '432 — Technical Debt.md',                   'Code Quality',          '1120 — Technical Debt.md'],
  ['Clean Code', '433 — Refactoring.md',                      'Code Quality',          '1121 — Refactoring.md'],
];
for (const [sd, sf, dd, df] of ccMap) mv(sd, sf, dd, df);

console.log('\n── DevOps & SDLC (450–460) → CI-CD + Microservices ──────');
const devopsMap = [
  ['DevOps & SDLC', '450 — CI-CD Pipeline.md',               'CI-CD',         '991 — CI-CD Pipeline.md'],
  ['DevOps & SDLC', '451 — Blue-Green Deployment.md',        'Microservices', '670 — Blue-Green Deployment.md'],
  ['DevOps & SDLC', '452 — Canary Deployment.md',            'Microservices', '669 — Canary Deployment.md'],
  ['DevOps & SDLC', '453 — Rolling Update.md',               'Kubernetes',    '901 — Rolling Update.md'],
  ['DevOps & SDLC', '454 — GitOps.md',                       'CI-CD',         '1020 — GitOps.md'],
  ['DevOps & SDLC', '455 — Infrastructure as Code (IaC).md', 'CI-CD',         '1016 — Infrastructure as Code (IaC).md'],
  ['DevOps & SDLC', '456 — Immutable Infrastructure.md',     'Cloud - AWS',   '955b — Immutable Infrastructure.md'],
  ['DevOps & SDLC', '457 — Twelve-Factor App.md',            'Microservices', '677 — Twelve-Factor App.md'],
  ['DevOps & SDLC', '458 — SRE.md',                          'Observability', '1210 — SRE.md'],
  ['DevOps & SDLC', '459 — Error Budget.md',                 'System Design', '691 — Error Budget.md'],
  ['DevOps & SDLC', '460 — Toil.md',                         'Observability', '1210b — Toil.md'],
];
for (const [sd, sf, dd, df] of devopsMap) mv(sd, sf, dd, df);

console.log('\n── JavaScript (541–562 → 1291–1370) ─────────────────────');
const jsMap = [
  ['541 — Event Loop.md',                   '1293 — Event Loop.md'],
  ['542 — Call Stack.md',                   '1292 — Call Stack (JS).md'],
  ['543 — Heap (JS).md',                    '1291b — Heap (JS).md'],
  ['545 — Task Queue (Macrotask).md',       '1294 — Task Queue (Macrotask).md'],
  ['546 — Microtask Queue.md',              '1295 — Microtask Queue.md'],
  ['547 — Web APIs.md',                     '1292b — Web APIs.md'],
  ['548 — var ⁄ let ⁄ const.md',           '1296 — var-let-const.md'],
  ['549 — Hoisting.md',                     '1297 — Hoisting.md'],
  ['550 — Temporal Dead Zone (TDZ).md',     '1298 — Temporal Dead Zone.md'],
  ['551 — Scope (Global, Function, Block).md', '1299 — Scope.md'],
  ['552 — Closure.md',                      '1300 — Closure.md'],
  ['553 — Lexical Environment.md',          '1300b — Lexical Environment.md'],
  ['554 — Prototype Chain.md',              '1301 — Prototype Chain.md'],
  ['555 — Prototypal Inheritance.md',       '1302 — Prototypal Inheritance.md'],
  ['556 — this keyword.md',                 '1303 — this keyword.md'],
  ['557 — Binding (call, apply, bind).md',  '1304 — Binding (call, apply, bind).md'],
  ['558 — Arrow Functions.md',              '1305 — Arrow Functions.md'],
  ['559 — Execution Context.md',            '1306 — Execution Context.md'],
  ['560 — IIFE.md',                         '1364 — IIFE.md'],
  ['561 — First-Class Functions.md',        '026b — First-Class Functions.md'],
  ['562 — Higher-Order Functions.md',       '1308 — Higher-Order Functions (JS).md'],
];
for (const [s, d] of jsMap) mv('JavaScript', s, 'JavaScript', d);

console.log('\n── Testing (412–423 → 1131–1175) ────────────────────────');
const testMap = [
  ['412 — Unit Test.md',                '1131 — Unit Test.md'],
  ['413 — Integration Test.md',         '1132 — Integration Test.md'],
  ['414 — Contract Test.md',            '1133 — Contract Test.md'],
  ['415 — E2E Test.md',                 '1134 — E2E Test.md'],
  ['416 — TDD.md',                      '1142 — TDD.md'],
  ['417 — BDD.md',                      '1143 — BDD.md'],
  ['418 — Mocking.md',                  '1144 — Mocking.md'],
  ['419 — Stubbing.md',                 '1145 — Stubbing.md'],
  ['420 — Faking-Spying.md',            '1146 — Faking-Spying.md'],
  ['421 — Test Pyramid.md',             '1148 — Test Pyramid.md'],
  ['422 — Property-Based Testing.md',   '1152 — Property-Based Testing.md'],
  ['423 — Mutation Testing.md',         '1111 — Mutation Testing.md'],
];
for (const [s, d] of testMap) mv('Testing', s, 'Testing', d);

// Move core.md from Spring to docs root (it's a stray file)
const coreFile = path.join(DOCS, 'Spring', 'core.md');
if (fs.existsSync(coreFile)) {
  fs.unlinkSync(coreFile);
  console.log('\n  Deleted stray: Spring/core.md');
}

console.log('\n✅ All file renames complete.');

