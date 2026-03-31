## 2026-03-31 - DOM Object Pooling
**Learning:** Frequent DOM insertions and removals cause layout thrashing and garbage collection pauses in fast-paced game loops, causing micro-stutters.
**Action:** Always reuse a single target DOM element and just update its position and visibility to avoid expensive appendChild and remove operations.
