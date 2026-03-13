## 2024-03-13 - High overhead when repeatedly instantiating Supabase clients
**Learning:** Instantiating `supabase.create_client` dynamically on every authenticated request incurs significant overhead, as it creates a new underlying `httpx.Client` connection pool each time. This creates a severe backend performance bottleneck, specific to how this app handled per-user authentications using `ClientOptions`.
**Action:** Use `functools.lru_cache` to cache client instances keyed by the user's access token when dealing with Row Level Security (RLS) requirements.
