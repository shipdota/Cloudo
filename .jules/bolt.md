## 2024-05-08 - TTL Cache with Threading Lock
**Learning:** For a global read-heavy endpoint like the leaderboard, an in-memory TTL cache effectively mitigates unbatched sequential calls. Using standard Python primitives (dictionary with expiration timestamps and `threading.Lock`) provides a robust caching solution without requiring unapproved third-party dependencies like `cachetools`.
**Action:** Always consider using native library tools (`time`, `threading`) to implement in-memory caching solutions for global state to minimize project dependencies while improving performance bottlenecks.
