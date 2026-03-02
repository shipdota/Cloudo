## 2024-05-24 - Caching Supabase Queries in Flask
**Learning:** Supabase API calls from the backend can add significant latency to frequently accessed pages like leaderboards. Simple Python dictionaries with thread locks work well for lightweight TTL caching without requiring external dependencies like Redis.
**Action:** Always consider adding a standard-library based TTL cache to high-traffic read-heavy backend routes that hit external APIs/Databases, especially for data that doesn't need to be perfectly real-time.
