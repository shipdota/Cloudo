## 2024-03-10 - Cache Supabase Clients for Per-User RLS
**Learning:** Creating a new Supabase client on every authenticated request (e.g. `create_client(..., options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))`) incurs significant overhead due to repeated `httpx.Client` instantiation.
**Action:** Use `functools.lru_cache` to cache client instances keyed by the user's access token, balancing RLS compliance with performance.
