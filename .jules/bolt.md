## 2025-05-22 - Caching Leaderboard API
**Learning:** Implementing a simple in-memory dictionary with a TTL of 60 seconds reduced simulated leaderboard request latency by 90% (from ~200ms to ~20ms per request).
**Action:** Use this pattern for semi-static database results in constrained environments where external caching libraries are unavailable.
