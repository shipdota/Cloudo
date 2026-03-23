## 2026-03-23 - Prevent Layout Thrashing in Game Loops
**Learning:** Querying layout-triggering properties like `clientWidth` and `clientHeight` inside high-frequency functions (like `spawnTarget` which runs on every user click) forces synchronous DOM layout reflows (layout thrashing), slowing down the main thread.
**Action:** When working on game mechanics or any high-frequency loops in the frontend, cache layout-triggering DOM properties during initialization (e.g., `DOMContentLoaded`) and update them only via window `resize` events, rather than querying them directly in the loop.
