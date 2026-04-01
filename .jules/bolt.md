## 2024-05-24 - Frontend Game Loop DOM Thrashing
**Learning:** The arcade game loop previously caused severe garbage collection pauses and layout thrashing by destroying/creating DOM elements (`document.createElement`) and querying layout properties (`clientWidth`/`clientHeight`) on every single target spawn.
**Action:** Always implement DOM Object Pooling (reusing existing elements with CSS classes like `.hidden`) and cache layout queries (`clientWidth`) outside of hot loops in fast-paced frontend mechanics.
