
## 2024-05-23 - Repeated Supabase create_client bottleneck
**Learning:** Instantiating a new `supabase.Client` via `create_client` for every authenticated request (to pass user tokens for RLS) is a significant performance bottleneck in Python because it creates a new underlying `httpx.Client` each time, discarding connection pooling and incurring high overhead. Modifying the global singleton with `auth(token)` is thread-unsafe and can cause data leaks.
**Action:** Use `functools.lru_cache` to cache client instances keyed by the user's access token. This safely scopes clients per-user (respecting RLS) while reusing the underlying `httpx.Client` connections across their session, vastly improving API throughput for games.
