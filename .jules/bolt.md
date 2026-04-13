## 2024-05-15 - Concurrent DB Queries
**Learning:** Sequential database queries (like fetching user profiles and scores) introduce unnecessary I/O latency bottlenecks. Using a global `ThreadPoolExecutor` from `concurrent.futures` allows independent DB queries to run concurrently, cutting I/O latency.
**Action:** Identify endpoints making multiple independent DB requests and execute them concurrently using a global thread pool instead of per-request pools, ensuring the client is thread-safe.
