## 2024-03-06 - Supabase Fetching Bottleneck

**Learning:** The Supabase API request on the `/leaderboard` route was a codebase-specific performance bottleneck due to frequent polling by users. Calling `supabase.table().select().order().limit().execute()` synchronously blocks the main thread on every request.

**Action:** Built a 60s TTL cache in `app/main.py` using `threading.Lock` and standard library dictionary for an immediate reduction in repeated Supabase calls on the hot path without external dependencies. Next time, always check if frequently accessed standard routes are fetching unmodified global data.
