## 2024-05-24 - Supabase SDK Sync I/O Bottleneck
**Learning:** The official Python Supabase client operates synchronously. Attempting to fetch multiple unbatched resources (like a user's profile and their high scores) in sequential `.execute()` calls severely degrades request performance by chaining network latency.
**Action:** When multiple independent queries are needed in a single route, execute them concurrently using `concurrent.futures.ThreadPoolExecutor`. This bypasses the SDK's synchronous bottleneck and safely leverages its internal connection pool.
