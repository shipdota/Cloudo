## 2024-03-11 - [Supabase RLS Client Caching]
**Learning:** [Instantiating a new `httpx.Client` inside `create_client` on every per-user authenticated Supabase request (RLS) is an extreme performance bottleneck, taking ~3.8 seconds for 100 requests versus ~0.03 seconds for 100 cached requests.]
**Action:** [Use `functools.lru_cache` keyed by the user's token (along with URL and Key) to cache the Supabase `Client` instance in Python for RLS contexts.]
