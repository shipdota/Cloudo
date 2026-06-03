## 2024-06-03 - [Missing B-tree index on scores table]
**Learning:** Found a missing B-tree index on the `score` column (specifically `DESC`) of the `scores` table in `schema.sql`. Without it, sorting operations in leaderboard and profile queries are less efficient.
**Action:** Always check `schema.sql` for missing indexes on frequently sorted or queried columns, particularly for core features like leaderboards. Added B-tree index to optimize the query.
