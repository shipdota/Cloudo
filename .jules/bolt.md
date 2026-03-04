## 2024-05-24 - Avoiding external cache dependencies
**Learning:** This codebase favors avoiding external dependencies like `Flask-Caching` for simple TTL caches. A custom standard-library dictionary and `time`/`threading.Lock` based TTL cache is sufficient for caching Supabase queries on high-traffic routes without introducing external overhead or Redis setups.
**Action:** When adding caching to improve performance, rely on native Python features (`dict`, `time`, `threading.Lock`) for simple TTL caches rather than adding new caching libraries, unless complexity genuinely warrants it.
