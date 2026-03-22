
## 2025-03-03 - Avoiding Synchronous DOM Layout Reflows in High-Frequency Functions
**Learning:** Accessing layout properties like `clientWidth` and `clientHeight` triggers synchronous DOM layout reflows (layout thrashing). In high-frequency functions like the target spawner (`spawnTarget`), this can significantly degrade performance.
**Action:** Always cache layout properties upon initialization and update them via event listeners (like `window.resize`) rather than querying them directly inside frequently executing game loops or spawning functions.
