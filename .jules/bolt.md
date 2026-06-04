## 2025-02-25 - Python Supabase Client Concurrency
**Learning:** The standard Supabase Python client operates synchronously, causing independent database queries (like fetching user profile and scores sequentially) to create N+1 bottlenecks.
**Action:** Use a globally instantiated `concurrent.futures.ThreadPoolExecutor` to execute independent queries concurrently, avoiding thread creation overhead on every request and reducing overall latency.
