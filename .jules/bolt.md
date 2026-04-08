
## 2024-05-18 - [DOM Object Pooling]
**Learning:** In a fast-paced game loop setting (like the `app/static/game.js` target spawner), frequently recreating and deleting DOM elements can cause significant lag (up to ~3s for 1M operations). Reusing a single element by toggling a CSS `display: none` (`.hidden`) class removes DOM thrashing, achieving a ~93% latency reduction.
**Action:** When working on frontend loops with repetitive element spawning/removal, use Object Pooling by manipulating element state/classes rather than performing expensive `document.createElement()` and `element.remove()` calls.
