## 2024-05-24 - [Avoid `flask` module unapproved dependency for `current_app`]
**Learning:** Adding caching for leaderboard requires simple imports to avoid testing constraints.
**Action:** Use `import time` and `import threading` for in-memory caching without 3rd party modules.
