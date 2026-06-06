## 2026-06-06 - Flask Template Fallbacks
**Learning:** When implementing a TTL cache fallback, relying on `.get('data', [])` is dangerous if the initial dictionary state is explicitly set to `{'data': None}` because it will return `None` instead of the fallback default, causing template iteration crashes if the very first database query fails.
**Action:** Use the `or` operator (e.g., `cache['data'] or []`) or initialize the cache default value to the expected safe type (e.g., `[]`) rather than `None`.
