---
layout: default
title: "HandlerMapping"
parent: "Spring Framework"
nav_order: 125
permalink: /spring/handlermapping/
---

`#spring` `#networking` `#internals` `#intermediate`

⚡ TL;DR — HandlerMapping is the Spring MVC component that maps an incoming HTTP request (URL + method + headers) to the correct controller method.
## 📘 Textbook Definition
`HandlerMapping` is a strategy interface in Spring MVC that determines which handler (controller method) processes a given HTTP request. The primary implementation, `RequestMappingHandlerMapping`, scans `@Controller` classes for `@RequestMapping`, `@GetMapping`, `@PostMapping`, etc. annotations and builds a mapping registry at startup.
## 🟢 Simple Definition (Easy)
HandlerMapping is Spring's URL router. It answers: "For this URL and HTTP method, which controller method should run?" It holds the complete mapping of URL patterns to controller methods.
## 💻 Code Example
```java
// Hand-behind-the-scenes view of HandlerMapping
// When @GetMapping("/users/{id}") is registered:
// RequestMappingHandlerMapping stores:
//   URL pattern: /users/{id}
//   HTTP method: GET
//   Handler: UserController#getUser(Long id)
@RestController
@RequestMapping("/users")
public class UserController {
    @GetMapping("/{id}")          // → registered in RequestMappingHandlerMapping
    public User getUser(@PathVariable Long id) { return userService.find(id); }
    @PostMapping
    public User createUser(@RequestBody User user) { return userService.save(user); }
}
// Introspect all mappings in Spring Boot
@Autowired RequestMappingHandlerMapping handlerMapping;
void printMappings() {
    handlerMapping.getHandlerMethods()
        .forEach((info, method) -> System.out.println(info + " → " + method));
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| HandlerMapping directly calls the controller | HandlerMapping returns a handler + interceptors; HandlerAdapter invokes it |
| Only one HandlerMapping exists | Multiple can coexist — DispatcherServlet queries them in priority order |
## 🔗 Related Keywords
- **[DispatcherServlet](./124 — DispatcherServlet.md)** — uses HandlerMapping to route requests
- **[Filter vs Interceptor](./126 — Filter vs Interceptor.md)** — interceptors configured on HandlerMapping
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Maps URL + HTTP method → controller method          |
+------------------------------------------------------------------+
| MAIN IMPL   | RequestMappingHandlerMapping (scans @RequestMapping) |
+------------------------------------------------------------------+
| ONE-LINER   | "Spring MVC's URL router"                            |
+------------------------------------------------------------------+
```
