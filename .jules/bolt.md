## 2024-05-22 - [In-memory TTL cache for Leaderboard]
**Learning:** Global read-heavy endpoints like the leaderboard should utilize a thread-safe, in-memory TTL cache to reduce database load. Since cachetools is not approved, we can implement it using standard Python tools (dict, time, threading.Lock).
**Action:** Implement double-checked locking for TTL caches to avoid cache stampedes.
