## 2025-02-20 - [Supabase Sync Client Performance]
**Learning:** The default Supabase python client executes queries synchronously, potentially causing performance bottlenecks by blocking the application thread on expensive or repeated database calls. A previous cache implementation mitigated this for the leaderboard, but profile fetching remains vulnerable if multiple queries are sequential.
**Action:** Use a thread pool (like `concurrent.futures.ThreadPoolExecutor`) globally instantiated to execute independent database queries concurrently where possible.
