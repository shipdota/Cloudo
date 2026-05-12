## 2024-05-24 - Missing Index on High-Frequency Sorts
**Learning:** High-frequency, read-heavy routes like `/leaderboard` that rely on queries like `.order('score', desc=True)` without an explicit index on the sort column will cause the database to perform sequential scans. This becomes a major bottleneck as the `scores` table grows.
**Action:** Always verify database indexes align with frequent query patterns, especially for columns used in sorting or filtering large datasets. Added a B-tree index on `scores (score DESC)` to optimize these queries.
