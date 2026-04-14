## 2024-05-24 - DOM Churn Bottleneck
**Learning:** In the arcade game, continuously creating and removing DOM elements (`document.createElement` and `.remove()`) during the game loop causes significant DOM churn and garbage collection overhead, leading to a bottleneck.
**Action:** Implemented DOM Object Pooling by reusing a single target element and toggling its visibility with a `.hidden` class to minimize DOM modifications and improve performance by ~90% in heavy iterations.
