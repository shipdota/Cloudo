## 2024-05-10 - Prevent Forced Synchronous Layouts in DOM Mutations
**Learning:** Accessing layout-triggering properties like `clientWidth` and `clientHeight` immediately after DOM mutations (like `element.remove()`) within the same execution block triggers forced synchronous layouts (reflows).
**Action:** Cache these dimensions outside of the high-frequency spawning logic to significantly improve performance. Use event listeners (like `resize`) to keep the cached values up to date only when necessary.
