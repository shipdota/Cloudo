## 2024-03-03 - Custom In-Memory Caching and Global State
**Learning:** The application lacks external dependencies for caching (like Redis or Flask-Caching). To implement lightweight caching without adding new dependencies, a global dictionary with a `threading.Lock()` and a TTL based on `time.time()` works well. However, this introduces global state that can bleed across tests.
**Action:** Always implement a corresponding test fixture (e.g., in `conftest.py` with `autouse=True`) to reset the global state (like `leaderboard_cache.clear()`) before each test to guarantee test isolation.
