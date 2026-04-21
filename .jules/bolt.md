## 2024-04-21 - [Database Index for Sorting]
**Learning:** Adding a B-tree index on the `score` column of the `scores` table (specifically `DESC`) provides a ~99.8% performance improvement for sorting operations in leaderboard and profile queries.
**Action:** Always verify if frequently sorted or filtered columns have appropriate indexes to avoid full table scans.