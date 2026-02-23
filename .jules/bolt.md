## 2024-05-23 - Dependency Conflict
**Learning:** `gotrue` (2.9.1) and `supafunc` (0.3.3) have conflicting `httpx` version requirements. `gotrue` needs `<0.28`, while other packages might need newer versions. `supafunc` 0.3.3 was restricting `httpx` to `<0.26` which conflicted with `supabase` needing `>=0.26`.
**Action:** Downgraded `httpx` to `0.27.2` and upgraded `supafunc` to `0.4.7` to resolve the diamond dependency conflict.
