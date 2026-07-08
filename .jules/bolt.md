## 2024-05-24 - Double-Checked Locking in Python

**Learning:** When implementing a thread-safe TTL cache in Python, simple locking can lead to unnecessary lock contention on every request, creating a bottleneck. However, a naive lock-free check followed by a locked update can lead to cache stampedes.

**Action:** Use the double-checked locking pattern: Check the cache validity (fast path), and if it's invalid, acquire the lock and re-check validity before updating. Ensure the `current_time` is recalculated inside the lock to avoid using stale values that could lead to race conditions.
