
## 2024-05-18 - [Double-Checked Locking for In-Memory TTL Caches]
**Learning:** [When implementing thread-safe, in-memory TTL caches using standard Python library tools like dictionaries and `threading.Lock()` to prevent cache stampedes upon expiration, the double-checked locking pattern is crucial. You must check if the cache is valid outside the lock (fast path), and if not, acquire the lock and re-check the validity before performing the expensive operation to avoid multiple threads regenerating the cache concurrently.]
**Action:** [Always use the double-checked locking pattern when implementing thread-safe in-memory caching to avoid cache stampedes, ensuring the fast path requires no lock acquisition.]
