## 2024-05-24 - Thread-safe TTL Cache for Read-Heavy Endpoints
**Learning:** For global read-heavy endpoints (like leaderboards), a simple in-memory thread-safe dictionary cache with a TTL avoids unapproved third-party dependencies while providing massive latency improvements over repeated database lookups.
**Action:** When optimizing read-heavy global endpoints, check if the data can tolerate a short TTL and implement an in-memory lock-protected cache to avoid external API overhead.
