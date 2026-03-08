## 2024-03-08 - Leaderboard DB Query Optimization
**Learning:** The `/leaderboard` route receives high traffic and was directly hitting Supabase for identical top 10 queries on every load. This is a critical codebase-specific bottleneck.
**Action:** Implemented a lightweight 60s TTL cache using standard library `time` and `threading.Lock` instead of external dependencies (like Redis) to reduce DB load, keeping architecture simple.
