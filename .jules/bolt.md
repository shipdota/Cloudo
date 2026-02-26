## 2024-03-24 - Supabase Client Initialization
**Learning:** `app/db.py` initializes `supabase` client at module level, requiring `SUPABASE_URL` and `SUPABASE_KEY` env vars to be present even for test collection/fixtures.
**Action:** Always provide dummy env vars when running tests (e.g., `SUPABASE_URL=x SUPABASE_KEY=y pytest`).

## 2024-03-24 - Dependency Conflict (supafunc/httpx)
**Learning:** `supafunc 0.3.3` requires `httpx < 0.26` while `supabase` requires `httpx >= 0.26`.
**Action:** Update `supafunc` to `0.4.7` and pin `httpx` to `0.27.2` to resolve the conflict and allow tests to run.
