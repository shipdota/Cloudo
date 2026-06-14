## 2024-06-14 - Thread-safe TTL Caching
**Learning:** When implementing in-memory TTL caches, using the double-checked locking pattern is crucial to prevent cache stampedes upon expiration. If multiple threads hit an expired cache concurrently, they could all attempt to query the database simultaneously without this pattern.
**Action:** Always check if the cache is valid, and if not, acquire the lock and re-check the validity before performing the expensive update operation. Recalculate variables used for the check inside the lock.
