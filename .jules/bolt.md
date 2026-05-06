## 2024-03-24 - [Avoid Forced Synchronous Layout in Game Loop]
**Learning:** Accessing layout-triggering properties like `clientWidth` and `clientHeight` immediately after modifying the DOM (such as calling `element.remove()`) within the same block triggers forced synchronous layouts (reflows). This is particularly impactful in high-frequency logic like a game loop.
**Action:** Always cache dimensions (`clientWidth`, `clientHeight`) during initialization (e.g. `startGame`) to avoid forcing the browser to recalculate layouts synchronously during high-frequency updates.
