## 2024-05-24 - Layout Thrashing in Game Loop
**Learning:** In `app/static/game.js`, reading layout-triggering properties (`clientWidth`, `clientHeight`) immediately after a DOM mutation (`activeTarget.remove()`) within the same block triggers a forced synchronous layout (reflow). This can cause severe performance degradation (jank) in a high-frequency spawning loop.
**Action:** Cache static container dimensions (`clientWidth`/`clientHeight`) during initialization (`startGame`) and reuse them in the loop (`spawnTarget`), instead of re-reading them every time a target is removed/spawned.
