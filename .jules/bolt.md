## 2024-04-06 - Supabase Python Client is Synchronous
**Learning:** The Supabase Python client's data querying methods (like `.table('...').select('...').execute()`) operate synchronously. If a route makes multiple independent database queries sequentially, it results in sequential network delays that compound latency.
**Action:** For independent queries in the same route (e.g., fetching a user's profile and their scores), use `concurrent.futures.ThreadPoolExecutor` to execute them concurrently, halving the network latency.
