## 2024-05-24 - Frontend Layout Thrashing in `spawnTarget`
**Learning:** Querying `clientWidth` and `clientHeight` synchronously inside high-frequency functions like `spawnTarget` causes the browser to perform synchronous DOM layout reflows (layout thrashing), which degrades frame rate.
**Action:** Cache layout-triggering properties during `DOMContentLoaded` and only update them within a `resize` event listener, instead of querying them continuously during the game loop or frequent events.
