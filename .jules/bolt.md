## 2024-05-19 - [Caching Database Calls]
**Learning:** Sequential database queries on high-traffic public routes like `/leaderboard` can bottleneck the server when many concurrent users visit the page. Without caching, each request directly hits the database.
**Action:** Implement thread-safe, in-memory TTL caching with double-checked locking using Python's standard `threading.Lock` and `time` modules to prevent cache stampedes and minimize database load without adding new dependencies.
