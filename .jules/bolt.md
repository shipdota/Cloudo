## 2024-05-24 - Environment Variable Caching Danger
**Learning:** Moving `os.environ.get()` lookups to module-level constants in Flask apps using `python-dotenv` and application factories creates a severe race condition. The variables will evaluate to `None` if read at import time before `load_dotenv()` is called in `create_app()`.
**Action:** Avoid caching environment variables at the module level in Flask/dotenv setups. The overhead of repeated `os.environ.get()` calls per request is preferable to application failure.
