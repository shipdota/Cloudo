## 2024-06-18 - Added Thread-safe TTL Cache for Leaderboard

**Learning:** When adding caching to a Flask application that uses threading, especially for database query results like the leaderboard, using a simple global dictionary is not thread-safe and can lead to cache stampedes (where multiple requests hitting an expired cache simultaneously all try to fetch and update the cache).

**Action:** Implemented a thread-safe in-memory TTL cache with double-checked locking using a `threading.Lock()`. This ensures that only one thread queries the database upon cache miss or expiration, while other threads wait and then use the newly fetched cache, significantly reducing database load on high-traffic routes without requiring external dependencies like Redis.