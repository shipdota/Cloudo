
## 2023-10-27 - Double-Checked Locking in TTL Cache
**Learning:** When implementing in-memory TTL caching with a thread lock, it's essential to use double-checked locking where you fetch the current time before checking the fast path, but also update the current time inside the slow path lock to prevent edge cases causing cache stampedes.
**Action:** Always recalculate time and check conditions once more within the slow path lock block for TTL caches. Also, ensure fallback returns safe data types (e.g. empty list) to prevent template rendering errors if the initial cache fetch fails.
