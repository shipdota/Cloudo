## 2023-10-27 - Dependency Conflict in requirements.txt
**Learning:** The `requirements.txt` file specifies incompatible versions of `httpx` (0.28.1) and `gotrue` (2.9.1). `gotrue` requires `httpx < 0.28`.
**Action:** When running tests or CI, you must manually resolve this (e.g., downgrade `httpx` to 0.27.2) or update `gotrue`. Future PRs should fix this properly.
